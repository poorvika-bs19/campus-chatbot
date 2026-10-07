"""
build_doc_chunks.py  --  Stage 2 Document Chunk Builder
RIT Hassan Campus Chatbot

Reads  : extraction_output.json   (already created by test_extract.py)
Writes : doc_chunks.json          (input for app.py document retrieval)

Rules (validated against actual documents in validate_stage2.py):
  Scholarship: corrected boundary rule — boundary triggers only when
               "How to Apply" line has been seen OR 2+ blank lines precede
               a new title.  Produces exactly 18 chunks from 80 non-empty
               paragraphs of SCHOLARSHIP.docx.
  Faculty PDF: split raw page text on numbered-entry pattern to produce
               1 header chunk + 18 per-faculty chunks = 19 total.

No text is rewritten, translated, summarized, or fabricated.
Missing-information flags (NO-APPLY, NO-ELIGIBILITY, NO-AMOUNT) are
preserved as metadata; they reflect the source document, not errors.
"""

import os, sys, json, re

PROJECT   = os.path.dirname(os.path.abspath(__file__))
INPUT_F   = os.path.join(PROJECT, "extraction_output.json")
OUTPUT_F  = os.path.join(PROJECT, "doc_chunks.json")


# ── Load extraction output ─────────────────────────────────────
if not os.path.exists(INPUT_F):
    print("ERROR: extraction_output.json not found. Run test_extract.py first.")
    sys.exit(1)

with open(INPUT_F, encoding="utf-8") as f:
    results = json.load(f)

scholarship_result = next(
    (r for r in results if "SCHOLARSHIP" in r.get("rel_path", "")), None)
faculty_result = next(
    (r for r in results if "computerscience" in r.get("rel_path", "")), None)

if not scholarship_result or scholarship_result["status"] != "OK":
    print("ERROR: SCHOLARSHIP.docx extraction missing or failed.")
    sys.exit(1)
if not faculty_result or faculty_result["status"] != "OK":
    print("ERROR: Faculty PDF extraction missing or failed.")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════
#  SCHOLARSHIP CHUNKING
# ══════════════════════════════════════════════════════════════════

BODY_MARKERS = (
    "Eligibility:",
    "What do you get",
    "How to Apply",
    "Students through only CET",
    "Applicable only for",
    "Only for students",
    "Only for children",
    "No limit on annual income",
    "The annual family income",
    "The annual income",
    "(E-attestation",
)

def is_body_line(text):
    return any(text.startswith(m) for m in BODY_MARKERS)

def buffer_has_body(buf):
    return any(is_body_line(p["text"]) for p in buf if p["char_count"] > 0)

def buffer_has_apply(buf):
    return any(p["text"].startswith("How to Apply") for p in buf
               if p["char_count"] > 0)

def prev_blanks(buf, n=2):
    recent = buf[-n:] if len(buf) >= n else buf
    return len(recent) == n and all(p["char_count"] == 0 for p in recent)

def chunk_scholarship(paragraphs):
    """
    Apply corrected boundary rule:
      - a chunk boundary fires when a non-body-line title appears AND
        the current buffer is complete (has_apply or 2+ blank lines before title).
    Returns list of chunks, each chunk being a list of non-empty para dicts.
    """
    buffer, chunks = [], []
    for p in paragraphs:
        if p["char_count"] == 0:
            buffer.append(p)
            continue
        is_body     = is_body_line(p["text"])
        scheme_done = buffer_has_apply(buffer) or prev_blanks(buffer, n=2)
        new_title   = not is_body and buffer_has_body(buffer) and scheme_done
        if new_title:
            ne = [x for x in buffer if x["char_count"] > 0]
            if ne:
                chunks.append(ne)
            buffer = [p]
        else:
            buffer.append(p)
    ne = [x for x in buffer if x["char_count"] > 0]
    if ne:
        chunks.append(ne)
    return chunks

scholarship_paras  = scholarship_result["paragraphs"]
scholarship_chunks = chunk_scholarship(scholarship_paras)

# Validate paragraph coverage
non_empty_paras = {p["para_index"] for p in scholarship_paras if p["char_count"] > 0}
in_chunks       = {p["para_index"] for c in scholarship_chunks for p in c}
lost            = non_empty_paras - in_chunks
if lost:
    print("FATAL: %d scholarship paragraphs lost in chunking: %s" % (len(lost), lost))
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════
#  FACULTY PDF CHUNKING
# ══════════════════════════════════════════════════════════════════

faculty_raw_text = faculty_result["pages"][0]["text"]

# Split on numbered entries: line starts with 1–2 digits + dot/space
faculty_segs = re.split(r'\n(?=\d{1,2}\.?\s+)', faculty_raw_text)
# faculty_segs[0] = header; faculty_segs[1..18] = one per faculty member


# ══════════════════════════════════════════════════════════════════
#  BUILD OUTPUT CHUNKS
# ══════════════════════════════════════════════════════════════════

chunks_out = []
global_idx = 0

# ── Scholarship chunks ─────────────────────────────────────────
for chunk_idx, chunk_paras in enumerate(scholarship_chunks):
    text    = "\n".join(p["text"] for p in chunk_paras)
    section = chunk_paras[0]["text"]  # first non-empty line = section label

    # Content flags (metadata only — never added to text)
    has_apply = any(p["text"].startswith("How to Apply") for p in chunk_paras)
    has_amt   = any("What do you get" in p["text"] or "Rs." in p["text"]
                    for p in chunk_paras)
    has_elig  = any(
        p["text"].startswith("Eligibility:") or
        "annual" in p["text"].lower() or
        "No limit" in p["text"] or
        p["text"].startswith("Students through") or
        p["text"].startswith("Applicable only") or
        p["text"].startswith("Only for")
        for p in chunk_paras)

    flags = []
    if not has_apply: flags.append("NO-APPLY-METHOD")
    if not has_amt:   flags.append("NO-AMOUNT")
    if not has_elig:  flags.append("NO-ELIGIBILITY")

    chunks_out.append({
        "chunk_id":    "scholarship_docx_%03d" % chunk_idx,
        "source_file": scholarship_result["rel_path"].replace("\\", "/"),
        "doc_label":   scholarship_result["doc_label"],
        "file_type":   "DOCX",
        "page":        None,
        "section":     section[:80],     # first line as section label
        "chunk_index": chunk_idx,
        "text":        text,             # verbatim, no rewriting
        "char_count":  len(text),
        "content_flags": flags,          # metadata only
    })
    global_idx += 1

# ── Faculty PDF chunks ─────────────────────────────────────────
for seg_idx, seg_text in enumerate(faculty_segs):
    text    = seg_text.strip()
    section = text.split("\n")[0][:80]   # first line of segment

    chunks_out.append({
        "chunk_id":    "faculty_pdf_%03d" % seg_idx,
        "source_file": faculty_result["rel_path"].replace("\\", "/"),
        "doc_label":   faculty_result["doc_label"],
        "file_type":   "PDF",
        "page":        1,                # single-page PDF
        "section":     section,
        "chunk_index": seg_idx,
        "text":        text,             # verbatim, no rewriting
        "char_count":  len(text),
        "content_flags": [],
    })
    global_idx += 1


# ══════════════════════════════════════════════════════════════════
#  WRITE OUTPUT
# ══════════════════════════════════════════════════════════════════

with open(OUTPUT_F, "w", encoding="utf-8") as f:
    json.dump(chunks_out, f, indent=2, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════
#  VALIDATION
# ══════════════════════════════════════════════════════════════════

scholarship_count = len(scholarship_chunks)
faculty_count     = len(faculty_segs)
total             = len(chunks_out)

# Faculty name check
KNOWN_NAMES = [
    "H N Prakash", "H.S. Mohana", "Suresha D", "S A Quadri", "Ramesh B",
    "Dinesh S", "Anil Kumar K N", "Kannika Lakshmi", "Shashikala M K",
    "Ruksar Parveen", "Usha C D", "Vishnu Navali", "Shravya M S",
    "Rohith K", "Kusuma H M", "Prakruthi H V", "Shalini H B", "Archana J B",
]
missing_names = [n for n in KNOWN_NAMES if n not in faculty_raw_text]

print("=" * 60)
print("  build_doc_chunks.py  —  Results")
print("=" * 60)
print("  Scholarship chunks  : %d  (expected 18)  %s" % (
    scholarship_count, "OK" if scholarship_count == 18 else "FAIL"))
print("  Faculty chunks      : %d  (expected 19)  %s" % (
    faculty_count, "OK" if faculty_count == 19 else "FAIL"))
print("  Total chunks        : %d  (expected 37)  %s" % (
    total, "OK" if total == 37 else "FAIL"))
print("  Para coverage (80)  : %d/80  %s" % (
    len(in_chunks), "OK" if len(in_chunks) == len(non_empty_paras) else "FAIL"))
print("  Missing faculty     : %s" % (missing_names or "none"))
print()

if scholarship_count == 18 and faculty_count == 19 and total == 37 \
        and not missing_names and not lost:
    print("  ALL VALIDATIONS PASSED")
    print("  Output: %s" % OUTPUT_F)
else:
    print("  VALIDATION FAILURES — do not proceed with implementation")
    sys.exit(1)
