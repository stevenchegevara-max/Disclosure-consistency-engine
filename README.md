# Disclosure Consistency Engine 🧠

This AI-powered tool detects **inconsistencies across investor-facing documents**, such as:

- 📊 **Numeric mismatches** between investor decks and IR websites  
- 🗓️ **Date mismatches** when time periods differ (e.g., FY2023 vs FY2024)  
- 📘 **Definition mismatches** in how metrics like ARR or EBITDA are described  

---

## 🔍 Use Case

Perfect for:
- Pre-IPO companies  
- Investor Relations (IR) teams  
- Consultants preparing due diligence or prospectuses  

---

## 🛠 How It Works

### 1. Provide input files
Two plain `.txt` files:
- `samples/deck.txt`
- `samples/ir.txt`

### 2. Run the engine

```bash
python engine/main.py --deck samples/deck.txt --ir samples/ir.txt
```

### 3. Example output

```json
{
  "issue_type": "numeric_mismatch",
  "metric": "REVENUE",
  "deck_value": "€120M",
  "ir_value": "€135M",
  "recommended_action": "Align the metric value across documents..."
}
```

📌 The JSON above is **only an example output** shown in the README.

---

## 🧪 Example Files

You can find example input files under:

- `samples/deck.txt`
- `samples/ir.txt`

---

## 🔧 Setup

- Python 3.7+
- No external dependencies

Run with:

```bash
python engine/main.py --deck samples/deck.txt --ir samples/ir.txt
```

---

## 👤 Author

Built by Steven Guevara
