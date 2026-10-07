"""
patch_faqs.py
Adds 3 missing question variants that caused Q2 and Q5 to match
wrong FAQs. Direct SQLite insert — no model load needed.
"""
import sqlite3, os

DB = os.path.join('instance', 'campus.db')
conn = sqlite3.connect(DB)
cur  = conn.cursor()

PATCHES = [
    # Q2 fix: "CSE HOD yaru?" was matching ECE HOD entry.
    # Add a tighter Kannada variant specifically for CSE HOD.
    (
        "Faculty",
        "CSE HOD yaru? CSE department na head yaru?",
        "CSE HOD: Dr. Suresha D (Professor & Head of Department, Computer Science & Engineering, RIT Hassan).",
        "Mixed"
    ),
    # Extra variant with common typo/alternate phrasing
    (
        "Faculty",
        "cse head yaru? computer science hod hesaru kodi",
        "CSE HOD: Dr. Suresha D — Professor & Head, Dept of Computer Science & Engineering, RIT Hassan.",
        "Mixed"
    ),
    # Q5 fix: "bus facility ideya?" matched a specific route FAQ.
    # Add a direct Kannada query for overall bus availability.
    (
        "Transport",
        "bus facility ideya? college ge bus ide?",
        "Haan! RIT Hassan nalli 5 bus routes ide.\n"
        "Route 2: Bittagodanahalli → New Bus Stand → College 8:50 AM (Driver Chonnakesava, Ph: 9483529679)\n"
        "Route 3: Aralikatte Circle → Dairy Circle → College (Driver Ranganath, Ph: 9900693953)\n"
        "Route 4: 80 Feet Road → MCE College → New Bus Stand → College 9:00 AM (Driver Maganegowda, Ph: 9900871814)\n"
        "Route 5: New Bus Stand → College 8:45 AM — FREE transport (Driver Ravi, Ph: 9353032762)\n"
        "Route 6: Vidhya Nagar → Railway Station → Dairy Circle → College 8:50 AM (Driver Kande Gowda, Ph: 8722649446)\n"
        "Evening return: Routes 2,3,5,6 at 5:15 PM | Route 4 at 4:30 PM.",
        "Mixed"
    ),
    # Extra Hindi variant for bus facility
    (
        "Transport",
        "college mein bus facility hai kya? RIT mein bus hai?",
        "Haan! RIT Hassan mein 5 bus routes hain.\n"
        "Route 2: Bittagodanahalli → New Bus Stand → College 8:50 AM (Driver Chonnakesava, 9483529679)\n"
        "Route 3: Aralikatte Circle → Dairy Circle → College (Driver Ranganath, 9900693953)\n"
        "Route 4: 80 Feet Road → New Bus Stand → College 9:00 AM (Driver Maganegowda, 9900871814)\n"
        "Route 5: New Bus Stand → College 8:45 AM — FREE (Driver Ravi, 9353032762)\n"
        "Route 6: Vidhya Nagar → Railway Station → College 8:50 AM (Driver Kande Gowda, 8722649446)\n"
        "Wapas: 5:15 PM (Route 4: 4:30 PM).",
        "Mixed"
    ),
]

# Only insert if question doesn't already exist
inserted = 0
for category, question, answer, language in PATCHES:
    cur.execute("SELECT id FROM faq WHERE LOWER(question) = ?", (question.lower(),))
    if cur.fetchone():
        print(f"  SKIP (already exists): {question[:60]}")
        continue
    cur.execute(
        "INSERT INTO faq (category, question, answer, language) VALUES (?, ?, ?, ?)",
        (category, question, answer, language)
    )
    inserted += 1
    print(f"  ADDED: [{category}] {question[:60]}")

conn.commit()
cur.execute("SELECT COUNT(*) FROM faq")
total = cur.fetchone()[0]
conn.close()

print(f"\nInserted {inserted} patch FAQs. Total FAQs now: {total}")
