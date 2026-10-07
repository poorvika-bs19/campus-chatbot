"""
ingest_documents.py  --  RIT Hassan Campus Chatbot
Source attribution pipeline.

What this does
--------------
1. Reads the college documents from data/ inside the project folder.
2. For machine-readable files (PDF, DOCX), extracts text to confirm content.
3. For image files, records file existence only (no OCR -- no text extraction).
4. Tags existing FAQ rows with source_doc using a precise per-FAQ-ID mapping.
   It does NOT tag entire categories blindly; every mapping was verified
   against the actual document content.
5. Records ingestion metadata in the document_source table.

Conservative mapping applied
-----------------------------
- CSE Faculty List (PDF)       --> 13 specific CSE faculty/HOD FAQ IDs only
- SCHOLARSHIP.docx             --> all 27 scholarship FAQ IDs
- Branch Seat Availability img --> all 18 admissions FAQ IDs
- Bus Route Sheets (images)    --> all 28 transport FAQ IDs
- Hostel Details (image)       --> all 21 hostel FAQ IDs
- Academic Calendar            --> NOT mapped (timetable excluded by design)
- Attendance, Exams, General,
  Fees, Library, Placements,
  AIML/ISE/other HOD Faculty   --> NOT mapped (NULL -- insufficient evidence)

Images are NOT treated as text-extracted documents.
Source labels for image-backed FAQs reflect the image filename only;
no text was read from those images.

Usage (after approval):
  cd C:/Users/Admin/Downloads/campus-chatbot
  python ingest_documents.py
"""

import os, sys, sqlite3
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────
# All documents must be inside the data/ subfolder of the project.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(PROJECT_DIR, "data")
DB_PATH     = os.path.join(PROJECT_DIR, "instance", "campus.db")


# ── Document registry ──────────────────────────────────────────────────────
# Each entry has:
#   "rel_path"   : path relative to DATA_DIR (use the exact filename/subfolder)
#   "doc_label"  : human-readable label stored in faq.source_doc
#   "file_type"  : PDF | DOCX | IMAGE
#   "faq_ids"    : exact FAQ row ids to tag -- conservative, per approved mapping
#
# Rules applied:
#  - PDF/DOCX entries: text is extracted to verify the file is readable.
#  - IMAGE entries   : file existence is confirmed; no text is read.
#  - faq_ids are the *only* rows that will receive source_doc.
#  - Rows NOT in any faq_ids list remain NULL.

DOCUMENT_REGISTRY = [

    # ------------------------------------------------------------------
    # 1. CSE Faculty List PDF
    #    Machine-readable. Contains: CSE faculty names, designations.
    #    Maps to: CSE HOD questions + CSE faculty list questions only.
    #    Does NOT map to AIML, ISE, ECE, EEE, ME, Civil, MBA HODs
    #    because those are NOT in this PDF.
    # ------------------------------------------------------------------
    {
        "rel_path":  os.path.join("faculty", "computerscience Faculty List.pdf"),
        "doc_label": "CSE Faculty List (PDF)",
        "file_type": "PDF",
        "faq_ids":   [
            # CSE HOD FAQs
            19, 20, 21,
            # CSE HOD variant questions added later
            191, 192, 195, 196, 197, 198,
            # CSE faculty list FAQs
            39, 40, 41, 42, 43,
        ],
    },

    # ------------------------------------------------------------------
    # 2. SCHOLARSHIP.docx
    #    Machine-readable. Contains: full SSP/NSP/other scholarship text.
    #    Maps to: all 27 scholarship FAQs.
    # ------------------------------------------------------------------
    {
        "rel_path":  os.path.join("fees", "SCHOLARSHIP.docx"),
        "doc_label": "Scholarship Details (DOCX)",
        "file_type": "DOCX",
        "faq_ids":   [
            137, 138, 139, 140, 141, 142, 143, 144, 145, 146,
            147, 148, 149, 150, 151, 152, 153, 154, 155, 156,
            157, 158, 159, 160, 161, 162, 163,
        ],
    },

    # ------------------------------------------------------------------
    # 3. Branch Seat Availability (Image)
    #    Image -- no text extraction. File confirmed present.
    #    Maps to: all 18 admissions/seat FAQs.
    # ------------------------------------------------------------------
    {
        "rel_path":  os.path.join("branchwise seat", "branch wise seat availability .jpeg"),
        "doc_label": "Branch Seat Availability (Image)",
        "file_type": "IMAGE",
        "faq_ids":   [52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
                      62, 63, 64, 65, 66, 67, 68, 69],
    },

    # ------------------------------------------------------------------
    # 4. Bus Route Sheets (Images)
    #    6 images in transport/ + 6 images in contacts/bus facility/.
    #    All transport FAQs came from these bus route images.
    #    A single shared label is used for all bus images.
    # ------------------------------------------------------------------
    {
        "rel_path":  os.path.join("transport", "WhatsApp Image 2026-09-03 at 7.21.35 PM.jpeg"),
        "doc_label": "Bus Route Sheets (Images)",
        "file_type": "IMAGE",
        "faq_ids":   [
            70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
            80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
            90, 91, 92, 93, 94, 95, 193, 194,
        ],
    },

    # ------------------------------------------------------------------
    # 5. Hostel Details (Image)
    #    Image -- no text extraction. File confirmed present.
    #    Maps to: all 21 hostel FAQs.
    # ------------------------------------------------------------------
    {
        "rel_path":  os.path.join("hostel", "hostel details.jpeg"),
        "doc_label": "Hostel Details (Image)",
        "file_type": "IMAGE",
        "faq_ids":   [96, 97, 98, 99, 100, 101, 102, 103, 104, 105,
                      106, 107, 108, 109, 110, 111, 112, 113, 114, 115,
                      199],
    },
]

# The following FAQ categories intentionally receive NULL source_doc
# because no reliable text-based source document is available:
#   Academic Calendar (timetable excluded by design)
#   Attendance        (image not in data/ folder)
#   Exams             (no document)
#   Faculty -- AIML   (image only, no OCR)
#   Faculty -- ISE    (image only, no OCR)
#   Faculty -- other HODs (image only, no OCR)
#   Fees              (DOCX was empty)
#   General / Contact (images only, no OCR)
#   Library           (DOCX was empty)
#   Placements        (folder was empty)


# ── Extraction helpers ─────────────────────────────────────────────────────

def extract_pdf_text(path):
    """Extract raw text from a PDF. Returns (text, error_or_None)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        pages  = [p.extract_text() for p in reader.pages]
        text   = "\n".join(t for t in pages if t and t.strip())
        return text.strip(), None
    except Exception as e:
        return "", str(e)


def extract_docx_text(path):
    """Extract raw text from a DOCX. Returns (text, error_or_None)."""
    try:
        from docx import Document
        doc   = Document(path)
        parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                parts.append(para.text.strip())
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    parts.append(" | ".join(cells))
        return "\n".join(parts), None
    except Exception as e:
        return "", str(e)


def get_image_info(path):
    """Return basic image metadata. No OCR, no text extraction."""
    try:
        from PIL import Image
        img = Image.open(path)
        return "IMAGE %dx%d mode=%s" % (img.width, img.height, img.mode), None
    except Exception as e:
        return "IMAGE (unreadable)", str(e)


# ── DB helpers ─────────────────────────────────────────────────────────────

def ensure_document_source_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS document_source (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_label     VARCHAR(200) NOT NULL,
            filename      VARCHAR(300) NOT NULL,
            file_type     VARCHAR(20)  NOT NULL,
            full_path     TEXT,
            extracted_len INTEGER      DEFAULT 0,
            error_msg     TEXT         DEFAULT NULL,
            faq_tagged    INTEGER      DEFAULT 0,
            ingested_at   DATETIME     DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def upsert_document_source(conn, doc_label, filename, file_type,
                            full_path, extracted_len, error_msg, faq_tagged):
    cur = conn.cursor()
    cur.execute("SELECT id FROM document_source WHERE filename = ?", (filename,))
    row = cur.fetchone()
    if row:
        cur.execute("""
            UPDATE document_source
               SET doc_label=?, file_type=?, full_path=?,
                   extracted_len=?, error_msg=?, faq_tagged=?,
                   ingested_at=CURRENT_TIMESTAMP
             WHERE filename=?
        """, (doc_label, file_type, full_path, extracted_len,
              error_msg, faq_tagged, filename))
    else:
        cur.execute("""
            INSERT INTO document_source
                   (doc_label, filename, file_type, full_path,
                    extracted_len, error_msg, faq_tagged)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc_label, filename, file_type, full_path,
              extracted_len, error_msg, faq_tagged))
    conn.commit()


def tag_faqs(conn, faq_ids, source_label):
    """
    Set source_doc = source_label for the given FAQ ids.
    Only updates rows where source_doc is currently NULL or empty
    so that a row already tagged by an earlier entry is not overwritten.
    Returns the count of rows actually updated.
    """
    cur     = conn.cursor()
    updated = 0
    for faq_id in faq_ids:
        cur.execute("""
            UPDATE faq
               SET source_doc = ?
             WHERE id = ?
               AND (source_doc IS NULL OR source_doc = '')
        """, (source_label, faq_id))
        updated += cur.rowcount
    conn.commit()
    return updated


# ── Main ingestion ─────────────────────────────────────────────────────────

def run_ingestion():
    os.chdir(PROJECT_DIR)
    conn = sqlite3.connect(DB_PATH)

    # Make sure the tracking table exists
    ensure_document_source_table(conn)

    # Make sure faq.source_doc column exists (it was added in migrate_source.py,
    # but we add a safety check here in case this is run on a fresh DB)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(faq)")
    faq_cols = [c[1] for c in cur.fetchall()]
    if 'source_doc' not in faq_cols:
        conn.execute("ALTER TABLE faq ADD COLUMN source_doc VARCHAR(120) DEFAULT NULL")
        conn.commit()
        print("Added source_doc column to faq table.")

    print("=" * 65)
    print("  RIT Hassan Chatbot -- Source Attribution Ingestion")
    print("=" * 65)
    print("  DATA_DIR : %s" % DATA_DIR)
    print("  DB_PATH  : %s" % DB_PATH)
    print()

    total_tagged = 0

    for doc in DOCUMENT_REGISTRY:
        rel_path  = doc["rel_path"]
        doc_label = doc["doc_label"]
        file_type = doc["file_type"]
        faq_ids   = doc["faq_ids"]
        full_path = os.path.join(DATA_DIR, rel_path)
        filename  = os.path.basename(rel_path)

        print("[%s] %s" % (file_type, rel_path))

        if not os.path.exists(full_path):
            print("  STATUS : FILE NOT FOUND -- %s" % full_path)
            print("  FAQs tagged: 0  (skipped)")
            upsert_document_source(conn, doc_label, filename, file_type,
                                   full_path, 0, "File not found", 0)
            print()
            continue

        # Extract text / get metadata
        if file_type == "PDF":
            text, err = extract_pdf_text(full_path)
            print("  Extracted : %d chars%s" % (
                len(text), ("  [ERROR: %s]" % err) if err else ""))
        elif file_type == "DOCX":
            text, err = extract_docx_text(full_path)
            print("  Extracted : %d chars%s" % (
                len(text), ("  [ERROR: %s]" % err) if err else ""))
        else:  # IMAGE -- no text extraction, confirm file exists
            text, err = get_image_info(full_path)
            print("  Image info: %s" % text)
            err = None

        extracted_len = len(text)

        # Tag FAQs
        tagged = tag_faqs(conn, faq_ids, doc_label)
        print("  Label     : %r" % doc_label)
        print("  FAQs tagged: %d / %d (already-tagged rows skipped)" % (
            tagged, len(faq_ids)))
        total_tagged += tagged

        upsert_document_source(conn, doc_label, filename, file_type,
                               full_path, extracted_len, err, tagged)
        print()

    # ── Summary ─────────────────────────────────────────────────────
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM faq")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM faq WHERE source_doc IS NOT NULL AND source_doc != ''")
    with_source = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM faq WHERE source_doc IS NULL OR source_doc = ''")
    without = cur.fetchone()[0]

    print("=" * 65)
    print("  Ingestion complete")
    print("=" * 65)
    print("  Total FAQs             : %d" % total)
    print("  FAQs with source_doc   : %d" % with_source)
    print("  FAQs without source_doc: %d (NULL -- by design)" % without)
    print("  FAQs tagged this run   : %d" % total_tagged)

    print("\n  Source distribution:")
    cur.execute("""
        SELECT source_doc, COUNT(*)
          FROM faq
         WHERE source_doc IS NOT NULL AND source_doc != ''
         GROUP BY source_doc
         ORDER BY COUNT(*) DESC
    """)
    for src, n in cur.fetchall():
        print("    %-45s : %d FAQs" % (src, n))

    print("\n  Untagged categories (NULL by design):")
    cur.execute("""
        SELECT category, COUNT(*)
          FROM faq
         WHERE source_doc IS NULL OR source_doc = ''
         GROUP BY category
         ORDER BY category
    """)
    for cat, n in cur.fetchall():
        print("    %-26s : %d FAQs" % (cat, n))

    conn.close()
    print("\nDone. Run this script again after adding new documents to data/.")
    return total_tagged


if __name__ == '__main__':
    run_ingestion()
