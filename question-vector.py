import faiss
import numpy as np
import pickle
import requests
import re
import unicodedata
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

BASE_DIR = Path(__file__).resolve().parent

print("Loading vector database...")

# ✅ Load ONCE (important for speed)
index = faiss.read_index(str(BASE_DIR / "vectors.index"))

with open(BASE_DIR / "chunks.pkl", "rb") as f:
    data = pickle.load(f)

chunks = data["chunks"]
metadata = data["metadata"]

print("System ready!\n")

# Single source of truth for menu data from Burger Lab menu.
MENU = {
    "Classic Street Boss": {"price": 12.0, "tax": 0.10, "category": "burger"},
    "Smoky BBQ Royale": {"price": 15.0, "tax": 0.10, "category": "burger"},
    "Truffle Shuffle": {"price": 16.0, "tax": 0.10, "category": "burger"},
    "Spicy Heatwave": {"price": 13.0, "tax": 0.10, "category": "burger"},
    "Bloody Mary": {"price": 16.0, "tax": 0.12, "category": "cocktail"},
    "Virgin Piña Colada": {"price": 17.0, "tax": 0.12, "category": "cocktail"},
    "French Martini": {"price": 16.0, "tax": 0.12, "category": "cocktail"},
    "Negroni": {"price": 16.0, "tax": 0.12, "category": "cocktail"},
    "Old Fashioned": {"price": 16.0, "tax": 0.12, "category": "cocktail"},
    "Bold & Hoppy IPA": {"price": 8.0, "tax": 0.12, "category": "beer"},
    "Dark & Roasty Stout": {"price": 9.0, "tax": 0.12, "category": "beer"},
    "Crisp Pilsner": {"price": 7.0, "tax": 0.12, "category": "beer"},
    "Smooth Amber Ale": {"price": 8.0, "tax": 0.12, "category": "beer"},
}

# Normalized item names are used for robust matching against user text
# (handles punctuation and accent variants like "Pina" vs "Piña").
MENU_NORMALIZED = {}
for item_name in MENU:
    normalized = unicodedata.normalize("NFKD", item_name.lower())
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    MENU_NORMALIZED[normalized] = item_name

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _extract_quantity_and_items(question: str):
    # Normalize question for stable matching with menu names.
    lowered = question.lower()
    normalized = unicodedata.normalize("NFKD", lowered)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    parsed = {}

    for normalized_item, item_name in MENU_NORMALIZED.items():
        if normalized_item not in normalized:
            continue

        quantity = 1
        pattern = rf"(\d+|{'|'.join(NUMBER_WORDS.keys())})\s+(?:x\s+)?{re.escape(normalized_item)}"
        match = re.search(pattern, normalized)
        if match:
            token = match.group(1)
            quantity = int(token) if token.isdigit() else NUMBER_WORDS.get(token, 1)

        parsed[item_name] = quantity

    return parsed


def _calculate_bill_text(items_with_qty: dict[str, int]) -> str:
    category_subtotals = {}
    total_tax = 0.0
    grand_subtotal = 0.0
    lines = []

    # Calculate each line exactly once and aggregate totals from line values.
    # This avoids duplicate tax calculations.
    for item_name, qty in items_with_qty.items():
        item_data = MENU[item_name]
        unit_price = item_data["price"]
        item_tax_rate = item_data["tax"]
        category = item_data["category"]
        line_total = unit_price * qty
        tax_amount = line_total * item_tax_rate
        gross = line_total + tax_amount

        category_subtotals[category] = category_subtotals.get(category, 0.0) + line_total
        total_tax += tax_amount
        grand_subtotal += line_total

        lines.append(
            f"- {item_name} x{qty}: base {line_total:.2f}, tax ({item_tax_rate * 100:.0f}%) {tax_amount:.2f}, total {gross:.2f}"
        )

    grand_total = grand_subtotal + total_tax

    if not lines:
        return (
            "Bill breakdown:\n"
            "- No recognized menu items were found in your question.\n"
            "Please include menu item names to calculate the bill."
        )

    subtotal_lines = [
        f"{category.title()} subtotal: {amount:.2f}"
        for category, amount in sorted(category_subtotals.items())
    ]
    details_block = "\n".join(lines)
    subtotals_block = "\n".join(subtotal_lines)
    return (
        "Bill breakdown:\n"
        f"{details_block}\n"
        f"{subtotals_block}\n"
        f"Subtotal: {grand_subtotal:.2f}\n"
        f"Tax total: {total_tax:.2f}\n"
        f"Grand total: {grand_total:.2f}"
    )


def _is_billing_question(question: str) -> bool:
    lowered = question.lower()
    markers = ["total price", "total", "bill", "cost", "how much", "price"]
    return any(marker in lowered for marker in markers)


def _is_cheapest_question(question: str) -> bool:
    lowered = question.lower()
    markers = ["cheapest", "lowest price", "least expensive", "lowest cost"]
    return any(marker in lowered for marker in markers)


def _is_availability_question(question: str) -> bool:
    lowered = question.lower()
    markers = ["available", "availability", "have", "contains", "with"]
    return any(marker in lowered for marker in markers)


def _availability_answer(question: str) -> str:
    # Availability is matched directly against normalized item names.
    lowered = question.lower()
    normalized = unicodedata.normalize("NFKD", lowered)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    matched_items = set()
    for normalized_item, item_name in MENU_NORMALIZED.items():
        item_tokens = normalized_item.split()
        if normalized_item in normalized or any(token in normalized for token in item_tokens):
            matched_items.add(item_name)

    if not matched_items:
        return "No matching menu items found for those keywords."

    listing = "\n".join(
        f"- {item}: {MENU[item]['price']:.2f} ({MENU[item]['category']})"
        for item in sorted(matched_items)
    )
    return f"Matching available items:\n{listing}"


def ask_question(question):
    if _is_cheapest_question(question):
        cheapest_item = min(MENU, key=lambda item: MENU[item]["price"])
        answer = f"Cheapest item: {cheapest_item} ({MENU[cheapest_item]['price']:.2f})"
        return answer, {"menu-rules"}

    if _is_billing_question(question):
        items_with_qty = _extract_quantity_and_items(question)
        answer = _calculate_bill_text(items_with_qty)
        return answer, {"menu-rules"}

    if _is_availability_question(question):
        answer = _availability_answer(question)
        # If rule-based availability cannot find a match, continue to RAG fallback.
        if "No matching" not in answer:
            return answer, {"menu-rules"}

    # Convert question to vector
    query_vector = model.encode([question])
    query_vector = np.array(query_vector).astype("float32")

    faiss.normalize_L2(query_vector)

    # Search top 5 matches
    scores, indices = index.search(query_vector, 5)

    context_parts = []
    sources = set()

    for idx in indices[0]:
        context_parts.append(chunks[idx])
        sources.add(metadata[idx]["source"])

    # Limit context (important for speed)
    context = "\n\n".join(context_parts)
    context = context[:1200]

    prompt = f"""
Answer using only the context below.
Be short and accurate.

Context:
{context}

Question:
{question}

Answer:
"""

    # Call Ollama API
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3:latest",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()
    payload = response.json()
    answer = payload.get("response")
    if not answer:
        raise RuntimeError(payload.get("error", "No answer returned from Ollama."))

    return answer.strip(), sources


def main():
    print("🤖 FAST Multi-PDF AI Assistant")
    print("Type 'exit' to quit\n")

    while True:
        question = input("❓ Ask: ")

        if question.lower() == "exit":
            break

        answer, sources = ask_question(question)

        print("\nAnswer:")
        print(answer)

        print("\n📚 Sources:")
        for s in sources:
            print("-", s)

        print("\n" + "="*40 + "\n")


if __name__ == "__main__":
    main()