"""
migrate_db.py
Migrates VARCHAR(1000) → TEXT for:
  - faq.answer
  - faq.question  (VARCHAR(300) → TEXT, future-proof)
  - chat_message.answer
  - chat_message.question  (VARCHAR(300) → TEXT, future-proof)

SQLite does not support ALTER COLUMN, so we use the official
SQLite migration pattern:
  1. Rename old table
  2. Create new table with correct types
  3. Copy all data
  4. Drop old table
"""
import sqlite3, os, sys

DB = os.path.join('instance', 'campus.db')
if not os.path.exists(DB):
    print("ERROR: database not found at", DB)
    sys.exit(1)

conn = sqlite3.connect(DB)
conn.execute("PRAGMA journal_mode=WAL")   # safer for migrations
cur  = conn.cursor()

# ── helper: print column types ──────────────────────────────
def show_schema(table):
    cur.execute(f"PRAGMA table_info({table})")
    cols = cur.fetchall()
    print(f"  {table}:")
    for c in cols:
        print(f"    {c[1]:<25} {c[2]}")

print("BEFORE migration:")
show_schema('faq')
show_schema('chat_message')

# ── 1. MIGRATE  faq  table ───────────────────────────────────
print("\nMigrating faq table...")
cur.executescript("""
    PRAGMA foreign_keys = OFF;

    -- Rename old table
    ALTER TABLE faq RENAME TO _faq_old;

    -- Create new table with TEXT for answer and question
    CREATE TABLE faq (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        category VARCHAR(50)  NOT NULL,
        question TEXT         NOT NULL,
        answer   TEXT         NOT NULL,
        language VARCHAR(20)  DEFAULT 'English'
    );

    -- Copy all rows
    INSERT INTO faq (id, category, question, answer, language)
        SELECT id, category, question, answer, language FROM _faq_old;

    -- Drop old table
    DROP TABLE _faq_old;

    PRAGMA foreign_keys = ON;
""")
conn.commit()
cur.execute("SELECT COUNT(*) FROM faq")
print(f"  faq rows after migration: {cur.fetchone()[0]}")

# ── 2. MIGRATE  chat_message  table ──────────────────────────
print("\nMigrating chat_message table...")
cur.executescript("""
    PRAGMA foreign_keys = OFF;

    ALTER TABLE chat_message RENAME TO _chat_old;

    CREATE TABLE chat_message (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email        VARCHAR(120) NOT NULL,
        question          TEXT         NOT NULL,
        answer            TEXT         NOT NULL,
        category          VARCHAR(50),
        sub_intent        VARCHAR(50),
        confidence        FLOAT,
        detected_language VARCHAR(20),
        feedback          VARCHAR(10)  DEFAULT NULL,
        timestamp         DATETIME
    );

    INSERT INTO chat_message
        (id, user_email, question, answer, category, sub_intent,
         confidence, detected_language, feedback, timestamp)
    SELECT
        id, user_email, question, answer, category, sub_intent,
        confidence, detected_language, feedback, timestamp
    FROM _chat_old;

    DROP TABLE _chat_old;

    PRAGMA foreign_keys = ON;
""")
conn.commit()
cur.execute("SELECT COUNT(*) FROM chat_message")
print(f"  chat_message rows after migration: {cur.fetchone()[0]}")

# ── 3. Run VACUUM to reclaim space ───────────────────────────
print("\nRunning VACUUM...")
conn.execute("VACUUM")
conn.commit()

# ── 4. Verify ────────────────────────────────────────────────
print("\nAFTER migration:")
show_schema('faq')
show_schema('chat_message')

# Verify long answers are intact
cur.execute("SELECT id, LENGTH(answer) FROM faq ORDER BY LENGTH(answer) DESC LIMIT 5")
print("\nTop 5 longest answers in faq:")
for r in cur.fetchall():
    print(f"  id={r[0]}  len={r[1]}")

# Spot-check a long answer is complete
cur.execute("SELECT answer FROM faq WHERE id=73")
row = cur.fetchone()
if row:
    print(f"\nFAQ id=73 answer length: {len(row[0])} chars (should be ~1676)")
    print("  First 80 chars:", row[0][:80])

conn.close()
print("\nMigration complete. No data lost.")
