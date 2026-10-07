"""
migrate_source.py
Safely adds the source_doc column to the faq table.
Uses SQLite ALTER TABLE ADD COLUMN which is non-destructive:
- If the column already exists it reports that and exits.
- Existing rows get NULL for source_doc (expected — ingest_documents.py fills them).
- No existing data is modified or deleted.
"""
import sqlite3, os

DB = os.path.join('instance', 'campus.db')
conn = sqlite3.connect(DB)
cur  = conn.cursor()

# Check if column already exists
cur.execute('PRAGMA table_info(faq)')
cols = [c[1] for c in cur.fetchall()]

if 'source_doc' in cols:
    print('source_doc column already exists. Nothing to do.')
else:
    cur.execute("ALTER TABLE faq ADD COLUMN source_doc VARCHAR(120) DEFAULT NULL")
    conn.commit()
    print('Added source_doc column to faq table.')

# Verify
cur.execute('PRAGMA table_info(faq)')
print('\nCurrent faq schema:')
for c in cur.fetchall():
    print('  %s  %s' % (c[1], c[2]))

cur.execute('SELECT COUNT(*) FROM faq')
print('\nTotal FAQs (unchanged):', cur.fetchone()[0])

conn.close()
print('\nMigration complete. No data was modified.')
