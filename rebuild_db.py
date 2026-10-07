"""
rebuild_db.py
Reads FAQS list from seed_data.py without importing app.py (avoids model load).
Wipes the faq table and reinserts all real-data entries directly via SQLite.
"""
import sqlite3, io, re, os

src = io.open('seed_data.py', encoding='utf-8').read()

# Extract the FAQS = [...] block (ends just before the seeding section)
match = re.search(r'FAQS = \[(.*?)\]\n\n# ={10}', src, re.DOTALL)
if not match:
    print("ERROR: could not find FAQS = [...] block in seed_data.py")
    raise SystemExit(1)

faqs_src = 'FAQS = [' + match.group(1) + ']'
ns = {}
exec(compile(faqs_src, '<faqs>', 'exec'), ns)
FAQS = ns['FAQS']
print(f"Parsed {len(FAQS)} FAQ entries from seed_data.py")

db_path = os.path.join('instance', 'campus.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Wipe all existing FAQs
cur.execute('DELETE FROM faq')
deleted = cur.rowcount
conn.commit()
print(f"Cleared {deleted} existing FAQ rows")

# Insert clean data
inserted = 0
for entry in FAQS:
    category, question, answer, language = entry
    cur.execute(
        'INSERT INTO faq (category, question, answer, language) VALUES (?, ?, ?, ?)',
        (category, question, answer, language)
    )
    inserted += 1

conn.commit()
print(f"Inserted {inserted} new FAQ rows")

# Breakdown
cur.execute('SELECT category, COUNT(*) FROM faq GROUP BY category ORDER BY category')
rows = cur.fetchall()
total = sum(r[1] for r in rows)
print("\nCategory breakdown:")
for cat, cnt in rows:
    print(f"  {cat:<26}: {cnt}")
print(f"  {'TOTAL':<26}: {total}")

conn.close()
print("\nDatabase rebuild complete. All dummy data removed.")
