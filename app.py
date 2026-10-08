from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sentence_transformers import SentenceTransformer, util
from deep_translator import GoogleTranslator, MyMemoryTranslator
from datetime import datetime
import re
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Keep the SQLite connection alive across requests and allow reuse
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'check_same_thread': False},
    'pool_pre_ping': True,
}
db = SQLAlchemy(app)

# ---------- MODELS ----------

class FAQ(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    category   = db.Column(db.String(50),  nullable=False)
    question   = db.Column(db.Text,        nullable=False)
    answer     = db.Column(db.Text,        nullable=False)
    language   = db.Column(db.String(20),  default="English")
    source_doc = db.Column(db.String(120), default=None)    # source document label

class User(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    email        = db.Column(db.String(120), unique=True, nullable=False)
    password_hash= db.Column(db.String(300), nullable=False)
    is_admin     = db.Column(db.Boolean, default=False)

class ChatMessage(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    user_email       = db.Column(db.String(120), nullable=False)
    question         = db.Column(db.Text,        nullable=False)
    answer           = db.Column(db.Text,        nullable=False)
    category         = db.Column(db.String(50))
    sub_intent       = db.Column(db.String(50))
    confidence       = db.Column(db.Float)
    detected_language= db.Column(db.String(20))
    feedback         = db.Column(db.String(10), default=None)
    timestamp        = db.Column(db.DateTime,    default=datetime.utcnow)
    source_doc       = db.Column(db.Text,        nullable=True)

class UnansweredQuestion(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120))
    question   = db.Column(db.Text,    nullable=False)
    best_score = db.Column(db.Float)
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)

print("Loading AI model... please wait")
model = SentenceTransformer(
    'paraphrase-multilingual-MiniLM-L12-v2',
    device='cpu'
)
print("Model loaded!")

# Document chunk loading deferred to after all functions are defined.
# _load_doc_chunks() is called at the bottom of this file before app.run().

# ==========================================================
#  LANGUAGE DETECTION
# ==========================================================
KANNADA_RANGE = re.compile(r'[\u0C80-\u0CFF]')
HINDI_RANGE   = re.compile(r'[\u0900-\u097F]')

KANNADA_HINTS = {
    # Core question words
    "enu", "yenu", "yavaga", "hege", "yaru", "yaaru", "yavaru",
    "yavavu", "yellide", "eshtu", "yestu", "naavu",
    # Verbs / actions
    "beku", "madabeku", "maadabeku", "iruthe", "irutte", "aagutte",
    "kattalu", "kodi", "kodi", "siguthade", "irbekku",
    "thalupathare", "baruttade", "barthade", "maadthare",
    # Postpositions / particles
    "ide", "idiya", "alli", "nalli", "inda", "mele", "bagge",
    "hesaru", "avare", "haan", "illa",
    # Common Kannada words
    "yenu", "yavavu", "saha", "mattu", "adu", "avru",
    # Common chatbot tokens
    "kodi", "kelo", "heli",
}

HINDI_HINTS = {
    # Core question words
    "kya", "kab", "kaise", "kaun", "kahan", "kyun", "kitna", "kitne",
    # Verbs / helpers
    "hai", "hain", "tha", "thi", "hoga", "karna", "chahiye",
    "milega", "milti", "batao", "bataye", "bataiye",
    # Postpositions / particles
    "mein", "ka", "ki", "ke", "se", "ko", "par", "aur",
    # Conversational
    "bharna", "hai", "hain", "nahi", "nahin", "wahan",
}

def detect_language(text: str) -> str:
    if KANNADA_RANGE.search(text):
        return "Kannada"
    if HINDI_RANGE.search(text):
        return "Hindi"
    # Strip punctuation and normalise for romanized word matching
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    words = set(clean.split())
    has_k = bool(words & KANNADA_HINTS)
    has_h = bool(words & HINDI_HINTS)
    has_en = any(w.isascii() and w.isalpha() and len(w) > 1 for w in words)
    if has_k and has_h:
        return "Mixed"          # both Kannada and Hindi cues → Mixed
    if (has_k or has_h) and has_en:
        return "Mixed"
    if has_k:
        return "Kannada (Romanized)"
    if has_h:
        return "Hindi (Romanized)"
    return "English"

# ==========================================================
#  INTENT ENGINE
# ==========================================================
# Each entry: (primary_intent, sub_intent, [keyword_triggers])
# Triggers are matched against lowercased, whitespace-normalised query.
# Order matters — more specific rules come first.

INTENT_RULES = [

    # ── TRANSPORT sub-intents ──────────────────────────────
    ("Transport", "bus_count",
     ["how many bus", "how many buses", "kitne bus", "eshtu bus",
      "yestu bus", "total bus", "number of bus", "bus count",
      "rit mein kitne bus", "rit alli eshtu bus", "college ge yestu bus",
      "college bus kitne", "rit has how many", "how many college bus"]),

    ("Transport", "bus_timing",
     ["bus timing", "bus time", "bus kab", "bus yavaga", "bus aagutte",
      "bus reach", "what time bus", "bus arrive", "bus departure",
      "bus start time", "bus return", "bus evening", "bus morning",
      "bus kab aata", "bus ka time", "bus kitne baje",
      "bus bejege", "morning bus", "evening bus"]),

    ("Transport", "bus_stops",
     ["bus stop", "bus route", "bus stops", "bus routes",
      "which stops", "bus pass through", "bus yavavu", "routes yavavu",
      "bus stop list", "route list", "bus jaata hai", "bus kahan se",
      "kahan se bus", "konsa route", "route details",
      "bus alli yavavu", "bus alli routes"]),

    ("Transport", "bus_availability",
     ["is there a bus", "bus ide", "bus iddiya", "bus available",
      "bus from hassan", "hassan bus", "bus stand se", "bus stand inda",
      "new bus stand bus", "bus stand bus", "bus facility",
      "college ge bus", "bus facility ideya", "bus idiya",
      "bus stand inda college", "transport available",
      "how to reach college by bus", "reach college by bus"]),

    ("Transport", "transport_contact",
     ["bus driver", "driver contact", "driver number", "driver mobile",
      "transport office", "bus helpline", "bus driver number",
      "driver phone", "contact bus", "bus no.", "bus number"]),

    ("Transport", "bus_general",
     ["bus", "transport", "college vehicle", "college cab",
      "college bus", "rit bus", "bus facility", "pick up", "pickup",
      "drop", "commute"]),

    # ── FACULTY sub-intents ────────────────────────────────
    ("Faculty", "hod",
     ["hod", "head of department", "department head", "head of dept",
      "department hod", "hod yaru", "hod hesaru", "hod kaun hai",
      "vibhaga mukhya", "principal of dept"]),

    ("Faculty", "cse_faculty",
     ["cse faculty", "cse teacher", "cse staff", "cse professor",
      "computer science faculty", "cse department faculty",
      "cse faculty list", "cse teachers", "who teaches cse"]),

    ("Faculty", "aiml_faculty",
     ["aiml faculty", "aiml teacher", "ai ml faculty", "ai & ml faculty",
      "artificial intelligence faculty", "machine learning faculty",
      "aiml staff", "aiml professor", "csaiml faculty"]),

    ("Faculty", "ise_faculty",
     ["ise faculty", "ise teacher", "information science faculty",
      "ise staff", "ise professor"]),

    # ── SCHOLARSHIP — teachers (inserted before Faculty/faculty_general) ──
    # "Is there a scholarship for government teachers' children?" contains
    # "teachers" which fires Faculty/faculty_general before reaching
    # Scholarships. This entry ensures that compound phrases containing
    # both "scholarship" and "teacher/teachers" route to Scholarships first.
    # Added: code-mixed compound forms e.g. "government teachers children's ke
    # scholarship ideya" — the key combinations are government+teacher+scholarship
    # or teacher+children+scholarship appearing together in any order.
    ("Scholarships", "scholarship_general",
     ["teachers scholarship", "scholarship for teachers",
      "scholarship for government teachers",
      "teachers children scholarship",
      "scholarship for teachers children",
      "government teachers scholarship",
      "government teacher scholarship",
      "teachers children ke scholarship",
      "teachers children's ke scholarship",
      "govt teachers scholarship",
      "government teachers children scholarship",
      "teachers ke scholarship",
      "teachers ka scholarship",
      "teachers children's scholarship",
      "government teachers children's scholarship",
      "teachers children ge scholarship",
      "government teachers children ge scholarship"]),

    ("Faculty", "faculty_general",
     ["faculty", "teacher", "professor", "staff", "lecturer",
      "faculty list", "faculty details", "faculty kodi",
      "teachers list", "faculty members"]),

    # ── PRINCIPAL ─────────────────────────────────────────
    ("General", "principal",
     ["principal", "principal yaru", "principal kaun hai",
      "principal hesaru", "rit principal", "college principal",
      "principal name", "principal of rit",
      "who is the principal", "principal of the college",
      "principal of college", "college ka principal",
      "college principal kaun", "college ke principal"]),

    # ── ADMISSIONS & SEATS ────────────────────────────────
    ("Admissions", "seats",
     ["seats", "seat availability", "seat count", "how many seats",
      "seats ide", "seats eshtu", "intake", "total seats",
      "yestu seats", "cse seats", "ece seats", "eee seats",
      "ise seats", "vlsi seats", "civil seats", "mech seats",
      "aiml seats", "branch seats", "quota seats",
      # singular "seat" patterns for code-mixed queries like "cse alli yestu seat ide"
      "seat ide", "seat eshtu", "yestu seat", "eshtu seat",
      "how many seat", "total seat"]),

    ("Admissions", "quota",
     ["quota", "cet quota", "comedk quota", "management quota",
      "cet seats", "comedk seats", "mgmt seats", "45%", "30%", "25%"]),

    ("Admissions", "admission_process",
     ["how to join", "join rit", "admission process",
      "how to get admission", "how to take admission",
      "entrance test", "cet rank", "comedk rank",
      "admission details", "apply for admission",
      "apply to rit", "rit admission"]),

    # ── HOSTEL ────────────────────────────────────────────
    ("Hostel", "hostel_fees",
     ["hostel fee", "hostel fees", "hostel cost", "hostel kitna",
      "hostel eshtu", "hostel charge", "hostel amount",
      "hostel rate", "how much hostel", "hostel pay"]),

    ("Hostel", "hostel_timing",
     ["hostel timing", "hostel time", "hostel open", "hostel close",
      "hostel gate time", "hostel entry", "hostel exit",
      "hostel hours", "hostel bejege"]),

    ("Hostel", "hostel_mess",
     ["mess timing", "food timing", "breakfast time", "lunch time",
      "dinner time", "hostel food", "mess time", "hostel meal",
      "hostel breakfast", "hostel lunch", "hostel dinner",
      "mess bejege", "food time"]),

    ("Hostel", "hostel_rooms",
     ["hostel rooms", "hostel block", "girls hostel", "boys hostel",
      "kaveri hostel", "hemavathi hostel", "hostel name",
      "hostel blocks", "hostel sharing", "how many rooms"]),

    ("Hostel", "hostel_visiting",
     ["parents visit", "parents visiting", "visit hostel", "meet students hostel",
      "parents day", "visitor day", "parents hostel",
      "parents yavaga", "parents meet"]),

    ("Hostel", "hostel_general",
     ["hostel", "accommodation", "stay", "boarding", "residence",
      "hostel details", "hostel facility", "hostel bagge",
      "hostel info"]),

    # ── ATTENDANCE ────────────────────────────────────────
    ("Attendance", "attendance_minimum",
     ["minimum attendance", "attendance required", "attendance percentage",
      "how much attendance", "attendance rule", "attendance criteria",
      "attendance beku", "attendance eshtu", "attendance percentage eshtu",
      "attendance minimum", "eligibility attendance"]),

    ("Attendance", "attendance_shortage",
     ["attendance shortage", "less attendance", "low attendance",
      "attendance below", "attendance not enough", "condonation",
      "attendance short", "attendance problem", "attendance issue",
      "85 se kam", "below 85", "attendance kam"]),

    ("Attendance", "attendance_general",
     ["attendance", "present", "absent", "leave", "class attendance",
      "daily attendance", "attendance record"]),

    # ── PLACEMENTS ────────────────────────────────────────
    ("Placements", "placement_stats",
     ["placement statistics", "placement stats", "placement data",
      "placement record", "placement percentage", "placement rate",
      "placement history", "how many placed", "placement numbers",
      "placement summary", "placement kodi"]),

    ("Placements", "highest_salary",
     ["highest salary", "max salary", "maximum salary", "best salary",
      "highest package", "top salary", "highest ctc",
      "highest pay", "maximum package"]),

    ("Placements", "placement_process",
     ["placement process", "how to get placed", "placement registration",
      "placement steps", "campus placement", "how placement works",
      "placement procedure"]),

    ("Placements", "placement_general",
     ["placement", "job", "recruit", "company", "campus", "hired",
      "placement cell", "internship", "offer letter",
      "placed students", "placement bagge"]),

    # ── SCHOLARSHIPS ──────────────────────────────────────
    ("Scholarships", "obc_scholarship",
     ["obc scholarship", "obc students scholarship", "backward class scholarship",
      "obc fee", "ssp obc", "obc financial aid"]),

    ("Scholarships", "sc_st_scholarship",
     ["sc st scholarship", "sc/st scholarship", "scheduled caste",
      "scheduled tribe", "sc scholarship", "st scholarship",
      "social welfare scholarship"]),

    ("Scholarships", "minority_scholarship",
     ["minority scholarship", "nsp scholarship", "nsp minority",
      "national scholarship", "minority students"]),

    ("Scholarships", "sports_scholarship",
     ["sports scholarship", "athlete scholarship", "youth empowerment",
      "district competition scholarship", "state competition scholarship"]),

    ("Scholarships", "scholarship_apply",
     ["how to apply scholarship", "scholarship apply", "apply scholarship",
      "apply for scholarship", "apply ssp", "apply nsp",
      "ssp scholarship", "nsp scholarship apply",
      "scholarship application", "scholarship madabeku",
      "scholarship form", "how to get scholarship",
      "scholarship eligibility", "ssp apply", "nsp apply"]),

    ("Scholarships", "scholarship_general",
     ["scholarship", "financial aid", "stipend", "bursary", "grant",
      "scholarship details", "scholarship bagge", "scholarship kodi",
      "scholarship list", "scholarship yenu",
      # Kannada-English: "is scholarship available"
      "scholarship sigutta", "scholarship sigaratte", "scholarship irutte",
      "scholarship available", "scholarship ide",
      # Hindi-English
      "scholarship available hai", "scholarship milega", "scholarship hai kya"]),

    # ── FEES ──────────────────────────────────────────────
    ("Fees", "fee_structure",
     ["fee structure", "fee details", "how much fee", "fees eshtu",
      "semester fee", "annual fee", "total fee", "fee amount",
      "tuition fee", "fees kitna", "fee keshtu", "fee kittla"]),

    ("Fees", "fee_payment",
     ["fee payment", "pay fees", "fee kattalu", "fees kattabeku",
      "how to pay fee", "fee online", "fee due date",
      "late fee", "fee fine", "fee deadline"]),

    ("Fees", "fees_general",
     ["fee", "fees", "payment", "accounts"]),

    # ── EXAMS ─────────────────────────────────────────────
    ("Exams", "exam_results",
     ["exam result", "results", "result yavaga", "vtu result",
      "marks", "grades", "score", "result portal",
      "result check", "result kodi"]),

    ("Exams", "revaluation",
     ["revaluation", "rechecking", "recheck", "re-evaluation",
      "revaluation apply", "revaluation process"]),

    # ── ACADEMIC CALENDAR — CIE date queries (inserted before Exams/cie) ──
    # "CIE exam date yavaga?" and "exam timetable kodi" are stored in
    # Academic Calendar (IDs 168, 170). The compound phrases below are more
    # specific than the bare "cie"/"exam" Exams triggers and must come first
    # so that Academic Calendar wins for date/schedule queries.
    ("Academic Calendar", "timetable",
     ["cie exam date", "cie date", "internal exam schedule",
      "exam timetable", "semester exam date"]),

    ("Exams", "cie",
     ["cie", "internal exam", "internal assessment", "internals",
      "internal marks", "internal test", "cie date",
      "1st cie", "2nd cie", "first cie", "second cie"]),

    ("Exams", "exam_general",
     ["exam", "examination", "test", "paper", "vtu exam",
      "semester exam", "theory exam", "practical exam",
      "supplementary", "back exam", "exam schedule"]),

    # ── ACADEMIC CALENDAR ─────────────────────────────────
    ("Academic Calendar", "timetable",
     ["timetable", "time table", "class schedule", "academic schedule",
      "academic calendar", "schedule", "class timetable",
      "cse timetable", "department timetable"]),

    ("Academic Calendar", "holidays",
     ["holiday", "holidays", "holiday list", "college holiday",
      "leave", "vacation", "holiday schedule", "saturday holiday",
      "holiday yavaga", "no class days"]),

    ("Academic Calendar", "semester_dates",
     ["semester start", "class start", "when do classes", "semester begin",
      "when does college", "college reopen", "next semester",
      "semester dates", "class yavaga", "college kab shuru"]),

    ("Academic Calendar", "events",
     ["events", "college events", "upcoming events", "fest",
      "technical event", "coding contest", "codeathon",
      "industrial visit", "project exhibition", "placement training"]),

    ("Academic Calendar", "calendar_general",
     ["calendar", "academic year", "odd semester", "even semester"]),

    # ── LIBRARY ───────────────────────────────────────────
    ("Library", "library_timing",
     ["library timing", "library time", "library open", "library hours",
      "library bejege", "library yavaga", "library yenu"]),

    ("Library", "library_general",
     ["library", "book", "borrow", "library card", "library fine",
      "library rules", "library facility"]),

    # ── CONTACT ───────────────────────────────────────────
    ("General", "contact",
     ["contact", "phone number", "phone no", "email", "address",
      "contact details", "contact number", "college phone",
      "reach college", "college address", "contact kodi",
      "phone kodi", "mail id", "email id", "helpline"]),

    # ── GENERAL ───────────────────────────────────────────
    ("General", "college_info",
     ["about rit", "about college", "what is rit", "rit hassan",
      "rajeev institute", "college name", "college info",
      "college details", "about rajeev", "college affiliated",
      "vtu affiliated", "naac", "aicte"]),
]

# Pre-built flat structure for fast lookup
_INTENT_LOOKUP = []  # list of (primary, sub, triggers_list)
for primary, sub, triggers in INTENT_RULES:
    _INTENT_LOOKUP.append((primary, sub, [t.lower() for t in triggers]))


def classify_intent(query: str):
    """
    Returns (primary_intent, sub_intent) by keyword matching.
    Falls back to (None, None) if no rule fires.
    Normalizes common code-mixed words before scanning triggers.
    """
    q = query.lower().strip()
    # Normalise common mixed-script words so triggers fire correctly
    q = q.replace("yestu", "eshtu").replace("yenu", "enu")
    q = q.replace("yaaru", "yaru").replace("hegide", "details")
    for primary, sub, triggers in _INTENT_LOOKUP:
        for t in triggers:
            if t in q:
                return primary, sub
    return None, None


# ==========================================================
#  QUERY NORMALISATION FOR EMBEDDING
# ==========================================================
# Code-mixed queries contain Kannada/Hindi function words that carry
# NO semantic meaning for the sentence-transformer (which was trained
# on natural language text, not code-mixed text).
#
# This function replaces those tokens with plain English equivalents
# ONLY for the embedding step. The original query is preserved
# everywhere else: DB storage, chat display, language detection,
# and intent classification all still use the original text.
#
# Ordered longest → shortest so multi-word patterns fire before
# their sub-parts.

_CODE_MIXED_REPLACEMENTS = [
    # ── Kannada-script CSE+HOD voice-input transliterations ─────
    #
    # When the voice language selector is set to kn-IN, the Google
    # Web Speech API transcribes "CSE HOD yaru?" as Kannada-script
    # characters spelling the letters phonetically. These compound
    # patterns match the COMPLETE CSE + HOD sequence in one shot —
    # no individual character substitution — so they cannot fire on
    # unrelated Kannada queries that happen to contain one of the
    # same characters.
    #
    # Verified against real transcripts from campus.db:
    #   ID=236  ಸಿಎಸ್ಸಿ ಎಚ್ ಓ ಡಿ ಯಾರು  → CSE HOD who  (was correct)
    #   ID=276  ಸಿಎಸ್ಸಿ ಎಚ್ ಒ ಡಿ ಯಾರು  → CSE HOD who  (was WRONG)
    #   ID=279  ಸಿಎಸ್ಸಿ ಹೆಚ್ ಓ ಡಿ ಯಾರು  → CSE HOD who  (was WRONG)
    #   ID=283  ಸಿಎಸ್ಸಿ ಹೆಚ್ ಓ ಡಿ ಯಾರು  → CSE HOD who  (was WRONG)
    #   ID=278  ಎಸ್ ಇ ಎಚ್ ಓ ಡಿ ಯಾರು   → CSE HOD who  (was correct)
    #
    # ID=275  ಗೆ ಯಾರು ಹೆಚ್ಚು ಓಡಿ  (Academic Calendar) → unchanged ✓
    #
    # All codepoints are in the Kannada Unicode block (U+0C80–U+0CFF).
    # These patterns can never match any ASCII typed query.
    #
    # Pattern 1: ಸಿಎಸ್ಸಿ (CSE) + space + (ಹೆಚ್|ಎಚ್) (H) + space + (ಓ|ಒ) (O) + space + ಡಿ (D) [+ space + ಯಾರು]
    (
        '\u0CB8\u0CBF\u0C8E\u0CB8\u0CCD\u0CB8\u0CBF'        # ಸಿಎಸ್ಸಿ — CSE
        r'\s+'
        r'(?:\u0CB9\u0CC6\u0C9A\u0CCD|\u0C8E\u0C9A\u0CCD)'  # ಹೆಚ್ or ಎಚ್ — H
        r'\s+(?:\u0C93|\u0C92)'                              # ಓ or ಒ — O
        r'\s+\u0CA1\u0CBF'                                   # ಡಿ — D
        r'(?:\s+\u0CAF\u0CBE\u0CB0\u0CC1)?',                 # ಯಾರು — who (optional)
        'CSE HOD who'
    ),
    # Pattern 2: ಎಸ್ ಇ (C S E spelled separately) + same HOD sequence
    (
        '\u0C8E\u0CB8\u0CCD'                                 # ಎಸ್ — CS
        r'\s+\u0C87\s+'                                      # ಇ — E
        r'(?:\u0CB9\u0CC6\u0C9A\u0CCD|\u0C8E\u0C9A\u0CCD)'  # ಹೆಚ್ or ಎಚ್ — H
        r'\s+(?:\u0C93|\u0C92)'                              # ಓ or ಒ — O
        r'\s+\u0CA1\u0CBF'                                   # ಡಿ — D
        r'(?:\s+\u0CAF\u0CBE\u0CB0\u0CC1)?',                 # ಯಾರು — who (optional)
        'CSE HOD who'
    ),

    # ── Kannada-script Principal normalisation ────────────────────
    #
    # When kn-IN voice recognition hears "principal" (an English
    # loanword used in Kannada speech), the Speech API may return
    # ಪ್ರಿನ್ಸಿಪಲ್ (U+0CAB 0CCD 0CB0 0CBF 0CA8 0CCD 0CB8 0CBF 0CAA 0CB2 0CCD).
    # ಹೆಸರು (U+0CB9 0CC6 0CB8 0CB0 0CC1) = "name" / "hesaru".
    #
    # Compound pattern: ಪ್ರಿನ್ಸಿಪಲ್ [+ optional space + ಹೆಸರು]
    #   → 'principal name'  (covers both alone and with ಹೆಸರು)
    #
    # Verified regression tests: principal, principal name,
    # Who is the principal of RIT Hassan?, CSE HOD — all unchanged.
    # ಪ್ರಿನ್ಸಿಪಲ್ alone → 'principal'  (via the same pattern with optional part absent)
    #
    # All codepoints are in U+0C80–U+0CFF (Kannada block).
    # Cannot match any ASCII query.
    (
        '\u0CAB\u0CCD\u0CB0\u0CBF\u0CA8\u0CCD\u0CB8\u0CBF\u0CAA\u0CB2\u0CCD'  # ಪ್ರಿನ್ಸಿಪಲ್
        r'(?:\s+\u0CB9\u0CC6\u0CB8\u0CB0\u0CC1)?',                             # optional ಹೆಸರು
        'principal name'
    ),

    # ── Kannada-script Hostel Fee voice queries ───────────────────
    #
    # kn-IN speech produces Kannada-script for hostel/fees/how-much.
    # ಹಾಸ್ಟೆಲ್ = hostel (0CB9 0CBE 0CB8 0CCD 0C9F 0CC6 0CB2 0CCD)
    # ಫೀಸ್    = fees   (0CAB 0CC0 0CB8 0CCD)
    # ಶುಲ್ಕ   = fee/charges (0CB6 0CC1 0CB2 0CCD 0C95)
    # ಎಷ್ಟು   = how much   (0C8E 0CB7 0CCD 0C9F 0CC1)  — optional
    # ಎಷ್ಟಿದೆ = how much is (0C8E 0CB7 0CCD 0C9F 0CBF 0CA6 0CC6) — optional
    # ಇದೆ     = is/are     (0C87 0CA6 0CC6) — optional
    #
    # Pattern A: ಹಾಸ್ಟೆಲ್ ಫೀಸ್ [+ optional amount suffix]
    # Pattern B: ಹಾಸ್ಟೆಲ್ ಶುಲ್ಕ [+ optional amount suffix]
    # → both normalise to 'hostel fees' which matches FAQ id=100
    #
    # These are compound multi-word patterns. No individual character
    # replacements are made. Cannot match any ASCII or Transport query.
    (
        '\u0CB9\u0CBE\u0CB8\u0CCD\u0C9F\u0CC6\u0CB2\u0CCD'   # ಹಾಸ್ಟೆಲ್
        r'\s+\u0CAB\u0CC0\u0CB8\u0CCD'                        # ಫೀಸ್
        r'(?:\s+(?:'
        r'\u0C8E\u0CB7\u0CCD\u0C9F\u0CBF\u0CA6\u0CC6'        # ಎಷ್ಟಿದೆ
        r'|\u0C8E\u0CB7\u0CCD\u0C9F\u0CC1\s+\u0C87\u0CA6\u0CC6'  # ಎಷ್ಟು ಇದೆ
        r'|\u0C8E\u0CB7\u0CCD\u0C9F\u0CC1'                    # ಎಷ್ಟು
        r'))?',
        'hostel fees'
    ),
    (
        '\u0CB9\u0CBE\u0CB8\u0CCD\u0C9F\u0CC6\u0CB2\u0CCD'   # ಹಾಸ್ಟೆಲ್
        r'\s+\u0CB6\u0CC1\u0CB2\u0CCD\u0C95'                  # ಶುಲ್ಕ
        r'(?:\s+(?:'
        r'\u0C8E\u0CB7\u0CCD\u0C9F\u0CBF\u0CA6\u0CC6'        # ಎಷ್ಟಿದೆ
        r'|\u0C8E\u0CB7\u0CCD\u0C9F\u0CC1\s+\u0C87\u0CA6\u0CC6'  # ಎಷ್ಟು ಇದೆ
        r'|\u0C8E\u0CB7\u0CCD\u0C9F\u0CC1'                    # ಎಷ್ಟು
        r'))?',
        'hostel fees'
    ),

    # ── Kannada-script Teachers Scholarship voice query ───────────
    #
    # When kn-IN speech produces Kannada-script loanwords for
    # "government teachers children's ke scholarship vidya":
    # ಟೀಚರ್ಸ್ = teachers (0C9F 0CC0 0C9A 0CB0 0CCD 0CB8 0CCD)
    # ಸ್ಕಾಲರ್ಶಿಪ್ = scholarship (0CB8 0CCD 0C95 0CBE 0CB2 0CB0 0CCD 0CB6 0CBF 0CAA 0CCD)
    # ವಿದ್ಯಾ = vidya/is-there (0CB5 0CBF 0CA6 0CCD 0CAF 0CBE)
    #
    # Pattern: ಟೀಚರ್ಸ್ ... ಸ್ಕಾಲರ್ಶಿಪ್ (teachers + scholarship anywhere in query)
    # → 'teachers scholarship' so the Scholarships intent fires.
    # Compound: both tokens must be present.
    (
        r'(?=.*\u0C9F\u0CC0\u0C9A\u0CB0\u0CCD\u0CB8\u0CCD)'    # must contain ಟೀಚರ್ಸ್
        r'(?=.*\u0CB8\u0CCD\u0C95\u0CBE\u0CB2\u0CB0\u0CCD\u0CB6\u0CBF\u0CAA\u0CCD)'  # must contain ಸ್ಕಾಲರ್ಶಿಪ್
        r'.+',                                                    # match the full string
        'scholarship for government teachers children'
    ),

    # ── AIML HOD normalisation (ASCII and Kannada-spaced variants) ─
    #
    # Problem: lowercase "aiml hod yaru" normalises to "aiml hod who"
    # which the embedding maps to EEE HOD instead of AIML HOD.
    # "AIML HOD" (uppercase) works correctly — so we normalise all
    # case variants and code-mixed forms to the canonical "AIML HOD who".
    #
    # ASCII patterns (must come BEFORE generic Kannada patterns):
    (r'\baiml\s+hod\b',        'AIML HOD'),   # aiml hod → AIML HOD
    (r'\bai\s+ml\s+hod\b',     'AIML HOD'),   # ai ml hod → AIML HOD
    (r'\baiml\s+head\b',       'AIML HOD'),   # aiml head → AIML HOD
    #
    # ME / Mechanical HOD normalisation
    # "ME HOD yaru", "me hod yaru", "mechanical HOD yaru" all score against
    # EEE HOD (similar 2-letter abbreviation) instead of Mechanical HOD.
    # Normalise to "Mechanical HOD who" so the embedding correctly matches
    # the Mechanical Engineering HOD FAQ (id=30/31) — Dr. Kuldeep B.
    # ASCII: ME/me/mechanical + hod/head variants.
    (r'\bme\s+hod\b',                    'Mechanical HOD'),
    (r'\bme\s+head\b',                   'Mechanical HOD'),
    (r'\bmechanical\s+hod\b',            'Mechanical HOD'),
    (r'\bmechanical\s+head\b',           'Mechanical HOD'),
    (r'\bmechanical\s+engineering\s+hod\b', 'Mechanical HOD'),
    #
    # Kannada-spaced A-I-M-L: ಎ ಐ ಎಂ ಎಲ್
    # ಎ=0C8E, ಐ=0C90, ಎಂ=0C8E 0C82, ಎಲ್=0C8E 0CB2 0CCD
    # Pattern: ಎ ಐ ಎಂ ಎಲ್ (the letters A I M L spelt in Kannada)
    # followed by any HOD marker (ಎಚ್/ಹೆಚ್/HOD/hod/ಎಚ್ ...)
    # → "AIML HOD who"
    (
        r'\u0C8E\s+\u0C90\s+\u0C8E\u0C82\s+\u0C8E\u0CB2\u0CCD'  # ಎ ಐ ಎಂ ಎಲ್
        r'(?:\s+.*)?'                                              # optional HOD/hod/ಎಚ್... tail
        r'\s*\u0CAF\u0CBE\u0CB0\u0CC1',                           # ಯಾರು at end
        'AIML HOD who'
    ),
    # Same without ಯಾರು — ಎ ಐ ಎಂ ಎಲ್ + HOD marker
    (
        r'\u0C8E\s+\u0C90\s+\u0C8E\u0C82\s+\u0C8E\u0CB2\u0CCD'  # ಎ ಐ ಎಂ ಎಲ್
        r'\s+(?:[Hh][Oo][Dd]'                                      # HOD/hod (ASCII)
        r'|\u0C8E\u0C9A\u0CCD'                                     # ಎಚ್
        r'|\u0CB9\u0CC6\u0C9A\u0CCD)',                             # ಹೆಚ್
        'AIML HOD'
    ),

    # ── Additional Kannada-script CSE+HOD voice variants ─────────
    #
    # Covers three new speech-recognition transcript shapes
    # observed from kn-IN voice input that were not matched by
    # the existing compound patterns above.
    #
    # NEW-1: Spaced CSE — speech splits 'ಸಿಎಸ್ಸಿ' into three tokens
    #   'ಸಿ ಎಸ್ ಸಿ ಎಚ್ ಒಡಿ ಯಾರು' / 'ಸಿ ಎಸ್ ಸಿ ಎಚ್ ಓಡಿ ಯಾರು'
    #   (ಒಡಿ / ಓಡಿ = O+DI concatenated, no space between O and D)
    (
        '\u0CB8\u0CBF'                                       # ಸಿ  — S-i
        r'\s+\u0C8E\u0CB8\u0CCD\s+'                         # ಎಸ್ — E-S
        r'\u0CB8\u0CBF\s+'                                   # ಸಿ  — S-i
        r'(?:\u0CB9\u0CC6\u0C9A\u0CCD|\u0C8E\u0C9A\u0CCD)'  # ಹೆಚ್ or ಎಚ್
        r'\s+(?:\u0C93\u0CA1\u0CBF|\u0C92\u0CA1\u0CBF)'      # ಓಡಿ or ಒಡಿ (concat)
        r'(?:\s+\u0CAF\u0CBE\u0CB0\u0CC1)?',                 # optional ಯಾರು
        'CSE HOD who'
    ),
    # NEW-2: Combined CSE, ಹೆಚ್ಚು (hechchu = "more/excess"),
    #   concatenated OD: 'ಸಿಎಸ್ಸಿ ಹೆಚ್ಚು ಓಡಿ ಯಾರು'
    (
        '\u0CB8\u0CBF\u0C8E\u0CB8\u0CCD\u0CB8\u0CBF'        # ಸಿಎಸ್ಸಿ
        r'\s+\u0CB9\u0CC6\u0C9A\u0CCD\u0C9A\u0CC1'          # ಹೆಚ್ಚು
        r'\s+(?:\u0C93\u0CA1\u0CBF|\u0C92\u0CA1\u0CBF)'      # ಓಡಿ or ಒಡಿ (concat)
        r'(?:\s+\u0CAF\u0CBE\u0CB0\u0CC1)?',                 # optional ಯಾರು
        'CSE HOD who'
    ),
    # NEW-3: Combined CSE, split H, concatenated OD:
    #   'ಸಿಎಸ್ಸಿ ಹೆಚ್ ಓಡಿ ಯಾರು' / 'ಸಿಎಸ್ಸಿ ಎಚ್ ಒಡಿ ಯಾರು'
    (
        '\u0CB8\u0CBF\u0C8E\u0CB8\u0CCD\u0CB8\u0CBF'        # ಸಿಎಸ್ಸಿ
        r'\s+(?:\u0CB9\u0CC6\u0C9A\u0CCD|\u0C8E\u0C9A\u0CCD)'  # ಹೆಚ್ or ಎಚ್
        r'\s+(?:\u0C93\u0CA1\u0CBF|\u0C92\u0CA1\u0CBF)'      # ಓಡಿ or ಒಡಿ (concat)
        r'(?:\s+\u0CAF\u0CBE\u0CB0\u0CC1)?',                 # optional ಯಾರು
        'CSE HOD who'
    ),

    # ── Kannada-script Principal alt-spelling (long-A vowel) ─────
    #
    # Speech API sometimes returns ಪ್ರಿನ್ಸಿಪಾಲ್ (with long-A: ಪಾ)
    # instead of the already-handled ಪ್ರಿನ್ಸಿಪಲ್ (with short-a: ಪ).
    # Covers alone, with ಹೆಸರು (name), and with ಯಾರು (who).
    (
        '\u0CAB\u0CCD\u0CB0\u0CBF\u0CA8\u0CCD\u0CB8\u0CBF\u0CAA\u0CBE\u0CB2\u0CCD'  # ಪ್ರಿನ್ಸಿಪಾಲ್
        r'(?:\s+(?:\u0CB9\u0CC6\u0CB8\u0CB0\u0CC1|\u0CAF\u0CBE\u0CB0\u0CC1))?',     # optional ಹೆಸರು or ಯಾರು
        'principal name'
    ),

    # ── Hindi Devanagari CSE+HOD compound ────────────────────────
    #
    # सीएससी होड़ कौन है → 'CSE HOD who'
    # सीएससी = CSE phonetic (0938 0940 090F 0938 0938 0940)
    # होड़   = HOD with nukta (0939 094B 0921 093C) or without (0939 094B 0921)
    # कौन   = who (0915 094C 0928)
    # है/हैं = is/are (optional)
    # All codepoints in Devanagari block (U+0900–U+097F).
    # Cannot match any Kannada-script or ASCII query.
    (
        '\u0938\u0940\u090F\u0938\u0938\u0940'               # सीएससी
        r'\s+(?:\u0939\u094B\u0921\u093C|\u0939\u094B\u0921)' # होड़ or होड
        r'\s+\u0915\u094C\u0928'                              # कौन
        r'(?:\s+(?:\u0939\u0948\u0902|\u0939\u0948))?',       # optional है/हैं
        'CSE HOD who'
    ),

    # ── Kannada multi-word patterns (longest first) ─────────────
    (r'\balli\s+yestu\s+seats\s+ide\b',    'how many seats are available in'),
    (r'\balli\s+eshtu\s+seats\s+ide\b',    'how many seats are available in'),
    (r'\balli\s+yestu\s+ide\b',            'how many are available in'),
    (r'\balli\s+eshtu\s+ide\b',            'how many are available in'),
    (r'\bbagge\s+information\s+kodi\b',    'give information about'),
    (r'\bbagge\s+details\s+kodi\b',        'give details about'),
    (r'\bdetails\s+kodi\b',                'give details'),
    (r'\blist\s+kodi\b',                   'give list'),
    (r'\bhesaru\s+kodi\b',                 'tell me the name'),
    (r'\byavaga\s+shuru\s+aagutte\b',      'when does it start'),

    # ── Kannada single-word patterns ─────────────────────────────
    (r'\byaru\b',         'who'),
    (r'\byaaru\b',        'who'),
    (r'\byavaru\b',       'who'),
    (r'\beshtu\b',        'how much'),
    (r'\byestu\b',        'how much'),
    (r'\benu\b',          'what'),
    (r'\byenu\b',         'what'),
    (r'\bideya\b',        'is available'),
    (r'\bidiya\b',        'is available'),
    (r'\bide\b',          'is there'),
    (r'\bkodi\b',         'give'),
    (r'\bhegide\b',       'how is'),
    (r'\bsigutta\b',      'is available'),
    (r'\birutte\b',       'will be'),
    (r'\biruthe\b',       'is'),
    (r'\baagutte\b',      'will happen'),
    (r'\balli\b',         'in'),
    (r'\bnalli\b',        'in'),
    (r'\bge\b',           'for'),
    (r'\binda\b',         'from'),
    (r'\bmele\b',         'on'),
    (r'\billa\b',         'not'),
    (r'\bhaan\b',         'yes'),
    (r'\bbeku\b',         'required'),
    (r'\bkattalu\b',      'to pay'),
    (r'\bbaruttade\b',    'comes'),
    (r'\bherthade\b',     'returns'),
    (r'\bmattu\b',        'and'),
    (r'\bsaha\b',         'and'),
    (r'\bheli\b',         'tell'),
    (r'\bkelo\b',         'ask'),

    # ── Hindi multi-word patterns (longest first) ────────────────
    (r'\bavailable\s+hai\s+kya\b',     'is available'),
    (r'\bhain\s+kya\b',               'are there'),
    (r'\bhai\s+kya\b',                'is available'),
    (r'\bke\s+baare\s+mein\b',        'about'),
    (r'\bkitni\s+hai\b',              'how much is'),
    (r'\bkitna\s+hai\b',              'how much is'),
    (r'\bkitne\s+hain\b',             'how many are'),
    (r'\bkab\s+se\b',                 'from when'),
    (r'\bkaise\s+hai\b',              'how is'),
    (r'\bdetails\s+batao\b',          'give details'),
    (r'\bbata\s+do\b',                'tell me'),

    # ── Hindi single-word patterns ───────────────────────────────
    (r'\bkaun\b',         'who'),
    (r'\bkitna\b',        'how much'),
    (r'\bkitne\b',        'how many'),
    (r'\bkitni\b',        'how much'),
    (r'\bkya\b',          'what'),
    (r'\bbatao\b',        'tell'),
    (r'\bbataiye\b',      'tell'),
    (r'\bbataye\b',       'tell'),
    (r'\bmilega\b',       'available'),
    (r'\bmilti\b',        'available'),
    (r'\bnahi\b',         'not'),
    (r'\bnahin\b',        'not'),
    (r'\bmein\b',         'in'),
    (r'\bka\b',           'of'),
    (r'\bki\b',           'of'),
    (r'\bke\b',           'of'),
    (r'\bse\b',           'from'),
    (r'\bko\b',           'to'),
    (r'\bpar\b',          'on'),
    (r'\baur\b',          'and'),
    (r'\bhoga\b',         'will be'),
    (r'\bhai\b',          'is'),
    (r'\bhain\b',         'are'),
    (r'\bkab\b',          'when'),
    (r'\bkahan\b',        'where'),
    (r'\bkaise\b',        'how'),
    (r'\bkyun\b',         'why'),

    # ── Principal "of the college" normalisation ─────────────────
    # "who is the principal of the college" → "principal of RIT Hassan"
    # so it matches the principal FAQ (id=15) rather than the college-info FAQ.
    (r'\bprincipal\s+of\s+the\s+college\b', 'principal of RIT Hassan'),
    (r'\bprincipal\s+of\s+college\b',       'principal of RIT Hassan'),
]

# Pre-compile all patterns once at startup for performance
_COMPILED_REPLACEMENTS = [
    (re.compile(pat, re.IGNORECASE), repl)
    for pat, repl in _CODE_MIXED_REPLACEMENTS
]

_MULTI_SPACE = re.compile(r'[ \t]{2,}')


# ==========================================================
#  ANSWER ENGLISH CLEANER
# ==========================================================
# Some older FAQ answers stored in the DB contain Kannada/Hindi
# phrases (e.g. "CSE ke HOD:", "avare", "nalli", etc.) because
# they were written as code-mixed answers for code-mixed questions.
# The chatbot must always reply in clear English.
# This function cleans those phrases from the final answer text.

_ANSWER_CLEANUPS = [
    # ==============================================================
    # CONTEXT-AWARE PHRASE REPLACEMENTS
    # Ordered longest/most-specific first so multi-word patterns
    # fire before their component words are touched.
    # All patterns derived from exact occurrences in the 42 affected
    # FAQ answer rows. No short or ambiguous tokens are included.
    # ==============================================================

    # ── Group A: Attendance/Exam — Kannada full clauses ───────────
    # A12 placed first: more specific (includes "RIT Hassan nalli" prefix),
    # must fire before the shorter A1 pattern which would otherwise partially
    # consume the same sentence and leave "nalli" un-replaced.
    (r'RIT Hassan nalli exam bardabeku minimum 85% attendance beku\.',
     'RIT Hassan requires a minimum of 85% attendance to write the exam.'),

    (r'Exam bardabeku minimum 85% attendance beku\.',
     'A minimum of 85% attendance is required to write the exam.'),

    (r'85% below:\s*Exam bardabeku eligible alla\.',
     'Below 85% attendance: Students are not eligible to write the exam.'),

    (r'Medical reason idre:\s*Condonation apply madabeku\.',
     'If there is a medical reason, students can apply for condonation.'),

    (r'College,\s*attendance bagge parents ge message kaltatte\.',
     'The college will send a message to parents about attendance.'),

    (r'Attendance 85% below aadre exam bardabeku eligible alla\.',
     'If attendance falls below 85%, students are not eligible to write the exam.'),

    (r'Medical reason idre doctor certificate jathe condonation apply madabeku\.',
     "If there is a medical reason, apply for condonation with a doctor's certificate."),

    (r'College parents ge message kaltatte\.',
     'The college will send a message to parents.'),

    (r'Medical reason indaga attendance shortage idre condonation apply madabeku\.',
     'If attendance is short due to a medical reason, apply for condonation.'),

    (r'Doctor certificate beku\.',
     "A doctor's certificate is required."),

    (r'Department HOD ge contact madabeku\.',
     'Contact your department HOD for the process.'),

    (r'Attendance shortfall idre college parents ge message kaltatte \(registered mobile number ge\)\.',
     'If there is an attendance shortfall, the college will send a message to parents on their registered mobile number.'),

    # ── Group B: Attendance — Hindi full clauses ──────────────────
    (r'RIT Hassan mein minimum 85% attendance zaroori hai exam dene ke liye\.',
     'RIT Hassan requires a minimum attendance of 85% to write the exam.'),

    (r'85% se kam ho to exam nahi de sakte\.',
     'Students with less than 85% attendance cannot write the exam.'),

    (r'Medical reason pe condonation milta hai\.',
     'Students can apply for condonation for a valid medical reason.'),

    (r'85% se kam attendance ho to semester exam nahi de sakte\.',
     'Students with less than 85% attendance cannot write the semester exam.'),

    (r'Medical reason ho to condonation apply kar sakte hain\.',
     'Students can apply for condonation for a medical reason.'),

    (r'College parents ko message karke inform karta hai\.',
     'The college informs parents through messages.'),

    # ── Group C: Scholarships — Kannada full clauses ──────────────
    (r'Annual income Rs\.1\.5 lakh below irbekku\.',
     'Annual family income must be below Rs.1.5 lakh.'),

    (r'Rs\.19,200 per year siguthade\.',
     'Rs.19,200 is provided per year.'),

    (r'Online apply madabeku\.',
     'Apply online.'),

    (r'CET through admission irbekku',
     'Admission must be through CET'),

    (r'Income Rs\.1\.5 lakh below irbekku\.',
     'Annual income must be below Rs.1.5 lakh.'),

    (r'Rs\.50,000 per year siguthade\.',
     'Rs.50,000 is provided per year.'),

    (r'District/State level competition represent maadida students ge eligible\.',
     'Students who have represented in District/State level competitions are eligible.'),

    (r'CET mattu Management students ge applicable\.',
     'Applicable for both CET and Management quota students.'),

    (r'Income Rs\.2\.5 lakh below irbekku\.',
     'Annual income must be below Rs.2.5 lakh.'),

    (r'SSP scholarship apply maadalu:',
     'To apply for SSP scholarship:'),

    (r'Karnataka student aagirbekku',
     'Must be a Karnataka student'),

    (r'Engineering nalli minimum 50% score irbekku',
     'Must have minimum 50% score in Engineering'),

    (r'SSP portal mele online apply maadabeku',
     'Apply online on the SSP portal'),

    (r'OBC ge:',
     'OBC:'),

    (r'SC/ST ge:',
     'SC/ST:'),

    # ── Group D: Faculty / Admissions — Kannada clauses ──────────
    (r'CSE department nalli 18 faculty members idare - 5 Professors \(HOD Dr\. Suresha D saha\) mattu 13 Assistant Professors\.',
     'There are 18 faculty members in the CSE department — 5 Professors (including HOD Dr. Suresha D) and 13 Assistant Professors.'),

    (r'AIML department nalli 10 faculty members idare - HOD Dr\. Prathibha G mattu 9 Assistant Professors\.',
     'There are 10 faculty members in the AIML department — HOD Dr. Prathibha G and 9 Assistant Professors.'),

    (r'ISE department nalli 7 faculty members idare\.',
     'There are 7 faculty members in the ISE department.'),

    (r'RIT Hassan ge admission: CET or COMEDK entrance exam nalli qualifying rank irbekku\.',
     'For admission to RIT Hassan, a qualifying rank in CET or COMEDK entrance exam is required.'),

    (r'CSE nalli 120 seats ide:',
     'CSE has 120 seats:'),

    (r'ECE nalli 120 seats -',
     'ECE has 120 seats —'),

    (r'CSE \(AIML\) nalli 60 seats -',
     'CSE (AIML) has 60 seats —'),

    # ── Group E: Transport — Kannada/Hindi clauses ────────────────
    (r'RIT Hassan nalli 5 bus routes ide \(Route 2, 3, 4, 5 mattu 6\)\.',
     'RIT Hassan has 5 bus routes (Route 2, 3, 4, 5 and 6).'),

    (r'Haan! RIT Hassan nalli 5 bus routes ide\.',
     'Yes! RIT Hassan has 5 bus routes.'),

    (r'RIT Hassan mein 5 bus routes hain - Route 2, 3, 4, 5 aur 6\.',
     'RIT Hassan has 5 bus routes — Route 2, 3, 4, 5 and 6.'),

    (r'Haan! RIT Hassan mein 5 bus routes hain\.',
     'Yes! RIT Hassan has 5 bus routes.'),

    (r'RIT Hassan ke 5 bus routes:',
     'RIT Hassan has 5 bus routes:'),

    (r'Haan! Route 5 - New Bus Stand se college free transport\.',
     'Yes! Route 5 provides free transport from New Bus Stand to college.'),

    (r'Haan! Eradu routes Dairy Circle nalli nillutte:',
     'Yes! Two routes stop at Dairy Circle:'),

    (r'Haan! Route 6 Railway Station nalli 8:30 AM ge nillutte\.',
     'Yes! Route 6 stops at Railway Station at 8:30 AM.'),

    # ── Group F: Hostel — Hindi clause ────────────────────────────
    (r'Parents Sunday ko hostel visit kar sakte hain\.',
     'Parents can visit the hostel on Sunday.'),

    # ── Group G: Faculty — Hindi clauses ─────────────────────────
    (r'CSE \(AIML\) department mein 10 faculty hain - 1 HOD \(Dr\. Prathibha G\) aur 9 Assistant Professors\.',
     'There are 10 faculty members in the CSE (AIML) department — 1 HOD (Dr. Prathibha G) and 9 Assistant Professors.'),

    (r'ISE department mein 7 faculty hain - HOD Dr\. Prathibha G aur 6 Assistant Professors\.',
     'There are 7 faculty members in the ISE department — HOD Dr. Prathibha G and 6 Assistant Professors.'),

    # ── Group H: General / Placements / Fees / Library / Exams ───
    (r'RIT Hassan ke principal Dr\. Mahesh P K hain\.',
     'The principal of RIT Hassan is Dr. Mahesh P K.'),

    (r'Highest salary package: Rs\.9,00,000 per annum \(2022-23 nalli\)\.',
     'Highest salary package: Rs.9,00,000 per annum (in 2022-23).'),

    (r'RIT Hassan mein sabse zyada salary Rs\.9,00,000 per annum thi - year 2022-23 mein\.',
     'The highest salary at RIT Hassan was Rs.9,00,000 per annum in the year 2022-23.'),

    (r'Fee details document nalli information ililla\. Accounts Office ge directly contact madabeku\.',
     'Fee details are not available in the document. Please contact the Accounts Office directly.'),

    (r'Fee document mein information nahi thi\. Accounts Office se directly pata karein\.',
     'Fee details are not available in the document. Please contact the Accounts Office directly.'),

    (r'Library timing document nalli information ililla\. College ge directly contact madabeku\.',
     'Library timing details are not available in the document. Please contact the college directly.'),

    (r'Library details document mein information nahi thi\. College se directly pata karein\.',
     'Library details are not available in the document. Please contact the college directly.'),

    (r'VTU results: results\.vtu\.ac\.in website nalli check madabeku\. USN number beku\.',
     'VTU results: Check on results.vtu.ac.in. Your USN number is required.'),

    (r'VTU results check karne ke liye: results\.vtu\.ac\.in website visit karein\. USN number chahiye\.',
     'To check VTU results: Visit results.vtu.ac.in. Your USN number is required.'),

    # ── Group I: Academic Calendar ────────────────────────────────
    (r'Pratiya 1st mattu 3rd Saturday holiday\. 2nd mattu 4th Saturday working day\.',
     'The 1st and 3rd Saturdays are holidays. The 2nd and 4th Saturdays are working days.'),

    # ── Group J: Admissions — Hindi ───────────────────────────────
    (r'CSE mein kul 120 seats -',
     'CSE has a total of 120 seats —'),

    # ==============================================================
    # RESIDUAL SINGLE-WORD SAFETY NET
    # These fire AFTER all phrase patterns above.
    # Only words ≥ 5 characters with zero English collision risk.
    # They catch any remaining occurrences not covered by the
    # phrase patterns above, and provide forward safety for new
    # FAQ rows added in future with the same tokens.
    # ==============================================================
    (r'\bsiguthade\b',   'is provided'),
    (r'\birbekku\b',     'is required'),
    (r'\bmaadabeku\b',   'is required'),
    (r'\bmadabeku\b',    'is required'),
    (r'\bililla\b',      'is not available'),
    (r'\bidare\b',       'are'),
    (r'\bmattu\b',       'and'),
    (r'\bWapas\b',       'Return'),

    # ==============================================================
    # ORIGINAL PATTERNS (retained — still handle edge cases)
    # ==============================================================
    # Hindi HOD/Principal prefix patterns
    (r'\bke\s+HOD\b',          'HOD'),
    (r'\bke\s+hod\b',          'HOD'),
    (r'\bke\s+Principal\b',    'Principal'),
    (r'\bka\s+HOD\b',          'HOD'),
    (r'\bka\s+hod\b',          'HOD'),
    # Kannada structural words
    (r'\bavare\b',             ''),
    (r'\bnalli\b',             'in'),
    (r'\balli\b',              'in'),
    (r'\birutte\b',            ''),
    (r'\biruthe\b',            ''),
    # Common code-mixed answer starters
    (r'^CSE\s+ke\s+HOD\s*:',   'CSE HOD:'),
    (r'^CSE\s+ke\s+hod\s*:',   'CSE HOD:'),
    (r'^ECE\s+ke\s+HOD\s*:',   'ECE HOD:'),
    (r'^ISE\s+ke\s+HOD\s*:',   'ISE HOD:'),
]

_COMPILED_ANSWER_CLEANUPS = [
    (re.compile(pat, re.IGNORECASE | re.MULTILINE), repl)
    for pat, repl in _ANSWER_CLEANUPS
]


def answer_to_english(text: str) -> str:
    """
    Remove stray Kannada/Hindi words from a stored FAQ answer so that
    the final response shown to the user is always clean English.
    Only fixes known patterns — does not translate whole answers.
    """
    result = text
    for pat, repl in _COMPILED_ANSWER_CLEANUPS:
        result = pat.sub(repl, result)
    result = _MULTI_SPACE.sub(' ', result).strip()
    return result


def normalize_for_embedding(query: str) -> str:
    """
    Convert code-mixed (Kannada-English / Hindi-English) text into a
    cleaner English-like string for better semantic embedding matching.

    Examples:
      "CSE HOD yaru?"            → "CSE HOD who?"
      "Hostel fees eshtu?"        → "Hostel fees how much?"
      "CSE alli yestu seats ide?" → "CSE how many seats are available in?"
      "Principal kaun hai?"       → "Principal who is?"
      "Scholarship available hai kya?" → "Scholarship is available?"

    The original query string is NOT modified anywhere else in the pipeline.
    Only the string passed to model.encode() in semantic_search() uses this.
    """
    result = query.strip()
    for compiled_pat, repl in _COMPILED_REPLACEMENTS:
        result = compiled_pat.sub(repl, result)
    result = _MULTI_SPACE.sub(' ', result).strip()
    return result


# ==========================================================
#  CONTEXT WINDOW  (stored in Flask session)
# ==========================================================
CONTEXT_WINDOW = 3   # number of previous turns to remember

# Pronouns / anaphora that signal a follow-up question
FOLLOWUP_SIGNALS = re.compile(
    r'\b(their|its|those|these|them|the same|it|that|this|'
    r'avu|adhu|avru|avar|yendu|adu|yenu)\b',
    re.IGNORECASE
)

def get_context() -> list:
    return session.get('chat_context', [])

def push_context(primary: str, sub: str, question: str):
    ctx = get_context()
    ctx.append({'primary': primary, 'sub': sub, 'question': question})
    session['chat_context'] = ctx[-CONTEXT_WINDOW:]

def resolve_intent_with_context(query: str, primary: str, sub: str):
    """
    If the current query has no detected intent but contains anaphoric
    references, inherit the last intent from context.
    """
    if primary is not None:
        return primary, sub
    ctx = get_context()
    if ctx and FOLLOWUP_SIGNALS.search(query):
        last = ctx[-1]
        return last['primary'], last['sub']
    return None, None


# ==========================================================
#  FOCUSED ANSWER EXTRACTION
# ==========================================================
# For certain sub-intents we want a short, direct sentence rather
# than the entire FAQ answer.

def extract_focused_answer(full_answer: str, sub_intent: str, query: str) -> str:
    """
    Pull out the most relevant portion of the answer for specific sub-intents.
    If extraction is not possible, return the full answer unchanged.
    """
    lines = [l.strip() for l in full_answer.split('\n') if l.strip()]

    if sub_intent == 'bus_count':
        # Read the count answer from the DB rather than a hardcoded string
        # so it stays correct if the DB is ever updated.
        for l in lines:
            if any(k in l.lower() for k in ['5 bus', 'five bus', '5 college bus',
                                             'five college bus', 'routes ide',
                                             'operates 5', 'runs 5']):
                return l
        # Fallback: first sentence of the answer
        return lines[0] if lines else full_answer

    if sub_intent == 'bus_timing':
        relevant = [l for l in lines if any(
            t in l.lower() for t in ['am', 'pm', ':00', ':10', ':15', ':20',
                                      ':25', ':30', ':35', ':40', ':45', ':50',
                                      ':55', 'return', 'depart', 'arrive',
                                      'morning', 'evening', '8:', '9:',
                                      '5:15', '4:30']
        )]
        if relevant:
            return '\n'.join(relevant[:12])

    if sub_intent == 'bus_stops':
        relevant = [l for l in lines if '→' in l or 'via' in l.lower()
                    or 'route' in l.lower() or '🚌' in l]
        if relevant:
            return '\n'.join(relevant)

    if sub_intent == 'transport_contact':
        relevant = [l for l in lines if any(
            t in l for t in ['📱', 'mob', 'contact', 'Driver', 'driver',
                              '9483', '9900', '9353', '8722']
        )]
        if relevant:
            return 'Bus driver contact numbers:\n' + '\n'.join(relevant)

    if sub_intent == 'hostel_fees':
        relevant = [l for l in lines if any(
            t in l.lower() for t in ['fee', 'rs.', '₹', 'sharing', 'cost',
                                      '75,000', '81,000']
        )]
        if relevant:
            return '\n'.join(relevant[:6])

    if sub_intent == 'hostel_timing':
        relevant = [l for l in lines if any(
            t in l.lower() for t in ['timing', 'time', 'am', 'pm', '6:30',
                                      'open', 'close', 'gate']
        )]
        if relevant:
            return '\n'.join(relevant[:4])

    if sub_intent == 'hostel_mess':
        relevant = [l for l in lines if any(
            t in l.lower() for t in ['breakfast', 'lunch', 'dinner', 'mess',
                                      'meal', 'food', 'am', 'pm']
        )]
        if relevant:
            return '\n'.join(relevant[:5])

    if sub_intent == 'hostel_rooms':
        relevant = [l for l in lines if any(
            t in l.lower() for t in ['room', 'block', 'kaveri', 'hemavathi',
                                      'boys', 'girls', 'sharing', '59', '143']
        )]
        if relevant:
            return '\n'.join(relevant[:6])

    if sub_intent == 'hostel_visiting':
        relevant = [l for l in lines if any(
            t in l.lower() for t in ['parent', 'visit', 'sunday', 'day']
        )]
        if relevant:
            return '\n'.join(relevant[:3])

    if sub_intent == 'attendance_minimum':
        relevant = [l for l in lines if any(
            t in l.lower() for t in ['85%', 'minimum', 'required', 'eligible',
                                      'eligibility', 'beku', 'minimum']
        )]
        if relevant:
            return '\n'.join(relevant[:4])

    if sub_intent == 'highest_salary':
        relevant = [l for l in lines if any(
            t in l for t in ['9,00,000', 'highest', 'Highest', '₹9',
                              'highest salary', 'max']
        )]
        if relevant:
            return '\n'.join(relevant[:3])

    if sub_intent == 'seats':
        q_lower = query.lower()
        # Normalize for branch detection (handle code-mixed forms)
        q_norm = normalize_for_embedding(q_lower)

        branch_map = {
            'cse': 'CSE', 'computer science': 'CSE',
            'ece': 'ECE', 'electronics': 'ECE',
            'eee': 'EEE', 'electrical': 'EEE',
            'ise': 'ISE', 'information science': 'ISE',
            'civil': 'Civil', 'mech': 'Mechanical',
            'mechanical': 'Mechanical',
            'vlsi': 'VLSI', 'aiml': 'AIML', 'ai ml': 'AIML',
            'ai & ml': 'AIML', 'artificial intelligence': 'AIML',
        }
        for key, branch in branch_map.items():
            if key in q_lower or key in q_norm:
                # CSE-specific guard: if query only says "cse" (not aiml),
                # skip lines that belong to the AI/ML programme.
                is_pure_cse = (
                    branch == 'CSE' and
                    not any(x in q_lower for x in
                            ['aiml', 'ai ml', 'ai &', 'artificial', 'machine learning'])
                )
                for l in lines:
                    l_lower = l.lower()
                    # Skip AIML lines when user asked for plain CSE
                    if is_pure_cse and any(
                            x in l_lower for x in
                            ['artificial', 'machine learning', 'ai &', 'aiml']):
                        continue
                    if branch.lower() in l_lower and (
                            'seat' in l_lower or '120' in l or '60' in l
                            or '30' in l or 'intake' in l_lower):
                        return l
        # No specific branch line found — return the full answer
        return full_answer

    if sub_intent == 'hod':
        q_lower = query.lower()
        # Also check the normalized version for code-mixed queries like
        # "CSE ka HOD kaun hai?" → normalized contains "who"
        q_norm  = normalize_for_embedding(q_lower)

        dept_map = [
            (['cse aiml', 'cs aiml', 'aiml', 'ai ml', 'artificial intelligence',
              'machine learning'],                                  'AIML'),
            (['cse', 'computer science'],                          'CSE'),
            (['ise', 'information science'],                       'ISE'),
            (['ece', 'electronics'],                               'ECE'),
            (['eee', 'electrical'],                                'EEE'),
            (['civil'],                                            'Civil'),
            (['mechanical', 'mech'],                               'Mechanical'),
            (['mba'],                                              'MBA'),
        ]
        for keywords, dept_tag in dept_map:
            if any(kw in q_lower or kw in q_norm for kw in keywords):
                # Strategy: collect candidate lines (heading + name lines)
                # then prefer a line that contains a person's name (Dr./Mr./Mrs./Ms.)
                candidates = []
                for i, l in enumerate(lines):
                    if dept_tag.lower() in l.lower() and any(
                            hk in l.lower() for hk in ['hod', 'head', 'professor']):
                        candidates.append(l)
                        # Also grab the immediately following line (usually has the name)
                        if i + 1 < len(lines):
                            candidates.append(lines[i + 1])

                if candidates:
                    # Prefer a line containing a person's name prefix
                    for c in candidates:
                        if any(p in c for p in ['Dr.', 'Mr.', 'Mrs.', 'Ms.',
                                                  'Dr ', 'Mr ', 'Mrs ', 'Ms ']):
                            return c
                    # Fallback: join all candidates
                    return '\n'.join(dict.fromkeys(candidates))  # deduplicated

                # No candidate found in this answer — return full
                return full_answer
        return full_answer

    return full_answer


# ==========================================================
#  CLARIFICATION MESSAGES
# ==========================================================
CLARIFICATIONS = {
    "Transport": (
        "I want to make sure I give you the right information about college transport. "
        "Are you asking about:\n"
        "• 🚌 How many buses RIT has\n"
        "• 🗺 Bus routes and stops\n"
        "• ⏰ Bus timings (morning/evening)\n"
        "• 📞 Bus driver contact numbers\n"
        "• 🔎 Whether a bus is available from a specific area\n\n"
        "Please rephrase your question and I'll answer right away!"
    ),
    "Faculty": (
        "Could you clarify which department you need faculty details for? "
        "For example:\n"
        "• CSE faculty list\n"
        "• AIML (AI & ML) faculty list\n"
        "• ISE faculty list\n"
        "• HOD of a specific department\n\n"
        "Just mention the department and I'll give you the details!"
    ),
    "Scholarships": (
        "There are many scholarships available at RIT Hassan! Could you tell me more about what you need?\n"
        "• OBC / SC / ST scholarship details\n"
        "• Minority (NSP) scholarship\n"
        "• Sports / differently-abled / ex-army scholarships\n"
        "• Non-government scholarships (Sitaram Jindal, Arihant Trust, etc.)\n"
        "• How to apply for a scholarship\n\n"
        "Let me know which one interests you!"
    ),
    "Hostel": (
        "I can help with hostel information. What specifically would you like to know?\n"
        "• 🏠 Hostel fees (girls / boys)\n"
        "• ⏰ Hostel timings\n"
        "• 🍽 Mess / food timings\n"
        "• 🛏 Room types and blocks\n"
        "• 👪 Parents visiting day\n\n"
        "Please specify and I'll give you the exact details!"
    ),
    "Exams": (
        "I can help with exam-related queries. What do you need?\n"
        "• 📅 CIE (internal exam) dates\n"
        "• 📖 Semester theory / practical exam schedule\n"
        "• 📊 How to check VTU results\n"
        "• 🔄 Revaluation process\n"
        "• 📝 Supplementary / back exam info\n\n"
        "Please be more specific!"
    ),
    "Academic Calendar": (
        "I can help with academic calendar details. Are you asking about:\n"
        "• 📅 Semester start/end dates\n"
        "• 🎉 Holiday list\n"
        "• 📋 Upcoming events and competitions\n"
        "• 📆 Pre-placement training schedule\n\n"
        "Tell me what you need!"
    ),
}

DEFAULT_CLARIFICATION = (
    "I'm not quite sure what you're asking. Could you be more specific? "
    "I can help with:\n"
    "🎓 Admissions & Seats  |  👨‍🏫 Faculty & HOD\n"
    "🚌 Bus / Transport     |  🏠 Hostel\n"
    "📚 Library             |  📅 Academic Calendar\n"
    "💼 Placements          |  🎁 Scholarships\n"
    "📋 Attendance          |  💰 Fees\n"
    "📞 Contact Details\n\n"
    "Just ask your question in English, Kannada, or Hindi!"
)


# ==========================================================
#  SEMANTIC SEARCH (intent-filtered)
# ==========================================================
# _faq_cache stores plain Python dicts (NOT SQLAlchemy ORM objects).
# Storing ORM objects across requests causes DetachedInstanceError
# because Flask-SQLAlchemy closes the session at the end of each
# request — any cached ORM object becomes detached and raises
# DetachedInstanceError when accessed in the next request.
#
# Plain dicts have no session binding, so they survive across
# requests safely. The cache is rebuilt whenever the FAQ count
# changes (initial count -1 always forces rebuild on first call).
_faq_cache = {
    'count':      -1,    # -1 forces rebuild on first request
    'rows':       [],    # list of plain dicts: {id, category, question, answer, language}
    'embeddings': None,  # torch tensor — safe to cache across requests
}


def _refresh_cache():
    """
    Rebuild the embedding cache when FAQ count changes.
    Stores plain dicts instead of ORM objects to avoid
    DetachedInstanceError across Flask request boundaries.
    """
    # Use a lightweight count query first to check if rebuild needed
    live_count = FAQ.query.count()
    if live_count == _faq_cache['count'] and _faq_cache['embeddings'] is not None:
        return  # nothing changed, cache is valid

    # Query all FAQs and immediately convert to plain dicts
    faqs = FAQ.query.all()
    rows = [
        {
            'id':         f.id,
            'category':   f.category,
            'question':   f.question,
            'answer':     f.answer,
            'language':   f.language,
            'source_doc': f.source_doc,   # source document label (may be None)
        }
        for f in faqs
    ]

    questions = [r['question'] for r in rows]
    _faq_cache['rows']       = rows
    _faq_cache['embeddings'] = model.encode(
    questions,
    convert_to_tensor=True,
    device='cpu'
)
    _faq_cache['count']      = live_count


def semantic_search(query: str, primary_intent: str, sub_intent: str):
    """
    Returns (best_row_dict, score).
    best_row_dict is a plain dict with keys: id, category, question, answer, language.
    Falls back to global search if no category match is confident enough.

    Uses normalize_for_embedding() on the query so that code-mixed
    Kannada-English and Hindi-English queries produce better vector matches.
    The original `query` string is unchanged — only the embedding input is
    normalized. DB storage, display, and language detection all keep the
    original text.
    """
    _refresh_cache()
    rows           = _faq_cache['rows']
    all_embeddings = _faq_cache['embeddings']

    if not rows:
        return None, 0.0

    # Normalize for embedding — converts code-mixed tokens to English
    # equivalents so the multilingual model scores better FAQ matches.
    embedding_query = normalize_for_embedding(query)

    user_emb = model.encode(
    embedding_query,
    convert_to_tensor=True,
    device='cpu'
)

    # ── Filtered search within category ──────────────────────────
    if primary_intent:
        cat_indices = [
            i for i, r in enumerate(rows)
            if r['category'].lower() == primary_intent.lower()
        ]
        if cat_indices:
            cat_embeddings   = all_embeddings[cat_indices]
            sims             = util.cos_sim(user_emb, cat_embeddings)[0]
            best_local_idx   = sims.argmax().item()
            best_local_score = sims[best_local_idx].item()

            if best_local_score >= 0.38:
                best_row = rows[cat_indices[best_local_idx]]

                # ── Branch-mismatch guard for seats sub-intent ────────
                # If user asked about a specific non-AIML branch (e.g. "CSE")
                # but the top match is the AIML FAQ, re-rank to prefer
                # a branch-specific FAQ question.
                if sub_intent == 'seats':
                    q_lower = query.lower()
                    q_norm  = normalize_for_embedding(q_lower)

                    # Determine which branch the user asked about
                    AIML_KEYWORDS = {'aiml', 'ai ml', 'ai &', 'artificial intelligence',
                                     'machine learning'}
                    asked_aiml = any(k in q_lower for k in AIML_KEYWORDS)

                    BRANCH_KEYWORDS = {
                        'cse': 'cse', 'computer science': 'cse',
                        'ece': 'ece', 'electronics': 'ece',
                        'eee': 'eee', 'electrical': 'eee',
                        'ise': 'ise', 'information science': 'ise',
                        'civil': 'civil', 'mechanical': 'mechanical', 'mech': 'mechanical',
                        'vlsi': 'vlsi',
                    }
                    asked_branch = None
                    for kw, br in BRANCH_KEYWORDS.items():
                        if kw in q_lower or kw in q_norm:
                            asked_branch = br
                            break

                    if asked_branch and asked_branch == 'cse' and not asked_aiml:
                        # Check if returned FAQ is about AIML (wrong branch)
                        matched_q = best_row['question'].lower()
                        if any(k in matched_q for k in ['aiml', 'ai & m', 'artificial']):
                            # Find the best CSE (non-AIML) seats FAQ.
                            # Prefer FAQ id=55 "How many seats are available in CSE at RIT Hassan?"
                            # or id=56 "CSE alli yestu seats ide?" — both answer 120.
                            for idx in cat_indices:
                                r = rows[idx]
                                rq = r['question'].lower()
                                ra = r['answer'].lower()
                                if ('cse' in rq and
                                        not any(k in rq for k in
                                                ['aiml', 'ai &', 'artificial', 'machine'])
                                        and any(k in rq for k in
                                                ['seat', 'seats', 'intake'])
                                        and '120' in ra):
                                    best_row = r
                                    break

                # ── Scholarship-mismatch guard ─────────────────────────
                # If sub-intent is scholarship_general (user wants to know
                # if scholarships are available at all) but the top match
                # is a specific scholarship FAQ (e.g. Differently Abled),
                # replace with the general scholarship list FAQ.
                #
                # Exception: if the match score is >= 0.95 the query is an
                # almost-exact match for that specific scholarship FAQ (e.g.
                # "Is there a scholarship for government teachers' children?"
                # scoring 0.9952 against ID=157). In that case keep the
                # specific FAQ — the user is clearly asking about it.
                elif sub_intent == 'scholarship_general':
                    matched_q = best_row['question'].lower()
                    matched_a = best_row['answer'].lower()
                    # Specific scholarship FAQs contain "is there a scholarship for"
                    # or mention a single scholarship type; the general list FAQ
                    # contains "obc", "sc/st", "nsp" etc. (multiple types).
                    is_specific = any(k in matched_q for k in [
                        'is there a scholarship for', 'differently abled',
                        'ex-army', 'ksrtc', 'coffee board', 'railway',
                        'sitaram jindal', 'arihant', 'jalappa', 'arya vysya',
                        'dharamshala', 'sports scholarship', 'minority scholarship',
                        'obc scholarship', 'sc st scholarship', 'teachers scholarship',
                    ])
                    if is_specific and best_local_score < 0.90:
                        # Score is below near-exact threshold: broad query matched a
                        # specific FAQ by chance — replace with the general list FAQ.
                        for idx in cat_indices:
                            r = rows[idx]
                            rq = r['question'].lower()
                            # The general FAQ asks "what scholarships are available"
                            # or "scholarship bagge information kodi"
                            if any(k in rq for k in [
                                'what scholarships are available',
                                'scholarship bagge information kodi',
                                'scholarship kya kya hain',
                                'scholarships at rit hassan',
                                'scholarships available for students',
                            ]):
                                best_row = r
                                break
                    # If is_specific AND score >= 0.95: keep best_row unchanged
                    # (the query is a near-exact match for this specific FAQ).

                return best_row, best_local_score

    # ── Global fallback ───────────────────────────────────────────
    sims      = util.cos_sim(user_emb, all_embeddings)[0]
    best_idx  = sims.argmax().item()
    best_score= sims[best_idx].item()
    return rows[best_idx], best_score


# ==========================================================
#  DOCUMENT CHUNK RETRIEVAL  (additive — does not affect FAQ)
# ==========================================================
# This block adds parallel document-based retrieval on top of the
# existing FAQ system. The FAQ cache, FAQ search, and all FAQ routing
# remain completely unchanged. If doc_chunks.json is absent, malformed,
# or fails to embed, every /ask request falls through to normal FAQ
# behaviour exactly as before.

_doc_cache = {
    'chunks':     [],    # list of chunk dicts from doc_chunks.json
    'embeddings': None,  # torch tensor
    'loaded':     False, # True once a load attempt (success or failure) completes
}

# ── Evidence-check vocabulary ──────────────────────────────────
_EVIDENCE_EQUIVALENTS = {
    'hod':          {'hod', 'head', 'head of department', 'dept head', 'department head', 'department'},
    'faculty':      {'faculty', 'professor', 'teacher', 'staff',
                     'lecturer', 'teaches', 'who teaches'},
    'scholarship':  {'scholarship', 'scheme', 'stipend', 'financial aid'},
    'obc':          {'obc', 'backward class', 'backward classes'},
    'sst':          {'sc', 'st', 'scheduled caste', 'scheduled tribe'},
    'nsp':          {'nsp', 'national scholarship', 'minority'},
    'ssp':          {'ssp', 'state scholarship'},
    'eligibility':  {'eligible', 'eligibility', 'criteria'},
    'amount':       {'amount', 'rs.', 'rupees', 'stipend'},
    'apply':        {'apply', 'application', 'offline', 'online', 'portal'},
    'ksrtc':        {'ksrtc', 'rtc'},
    'army':         {'army', 'ex-army', 'defence'},
    'railway':      {'railway', 'railways', 'rail'},
    'sports':       {'sports', 'athlete', 'competition', 'district'},
    'labour':       {'labour', 'daily wage', 'worker'},
    'disabled':     {'disabled', 'differently abled', 'abled'},
    'teacher':      {'teacher', 'government teacher'},
    'coffee':       {'coffee', 'coffee board', 'curing'},
    'jalappa':      {'jalappa', 'veerashaiva', 'lingayat'},
    'arihant':      {'arihant', 'charitable trust'},
    'dharamshala':  {'dharamshala', 'dharmasthala'},
    'sitaram':      {'sitaram jindal', 'jindal'},
    'principal':    {'principal', 'head of institution'},
    'programming':  {'programming', 'program', 'lab', 'c program'},
}

_EVIDENCE_STOP = {
    'who', 'what', 'how', 'when', 'where', 'which', 'the', 'are',
    'for', 'and', 'give', 'tell', 'much', 'many', 'can', 'you',
    'this', 'that', 'about', 'from', 'with', 'have', 'does',
    'yaru', 'eshtu', 'kya', 'hai', 'kodi', 'details', 'mein', 'ka',
    'ki', 'ke', 'is', 'of', 'in', 'at', 'on', 'to', 'a', 'an',
    'information', 'batao', 'beku', 'ide', 'enu', 'bagge',
}

_MULTI_BLANK = re.compile(r'\n{3,}')


def evidence_check(query: str, chunk: dict) -> bool:
    """
    Returns True if chunk contains meaningful evidence for the query.
    Receives the full chunk dict (uses 'text', 'doc_label', 'section').

    Design principles:
    1. Empty / whitespace-only chunks are always rejected — they cannot
       provide a document answer.
    2. Named-scheme queries must match the SPECIFIC scheme in the chunk.
       A query naming OBC must not accept an NSP or Ex-Army chunk.
    3. Named-person / faculty queries must not accept scholarship chunks.
    4. Specific batch queries must match the specific batch in the chunk.
    5. Broad category queries (no specific scheme named) use token-based
       matching — at least 1 content-token hit (2 hits when 3+ content tokens).
    6. All-stopword queries without any content token do not block.
    """
    chunk_text = chunk.get('text', '')

    # ── GUARD 0: empty chunk — always reject ──────────────────────────────
    if not chunk_text.strip():
        return False

    q_lower = query.lower()
    c_lower = chunk_text.lower()

    # ── GUARD 1: faculty/person query must not match a scholarship chunk ──
    # If the query contains a person's name prefix (Dr., Mr., Mrs., Ms.) or
    # a clear faculty-only term, and the chunk is a scholarship chunk,
    # reject immediately.
    is_scholarship_chunk = 'scholarship' in chunk.get('doc_label', '').lower()
    has_person_prefix = bool(re.search(
        r'\b(dr|mr|mrs|ms)\b\.?\s+\w', q_lower
    ))
    faculty_only_terms = {'who teaches', 'who is the', 'lecturer', 'professor name',
                          'faculty name', 'faculty list'}
    has_faculty_only = any(t in q_lower for t in faculty_only_terms)

    if is_scholarship_chunk and (has_person_prefix or has_faculty_only):
        return False

    # ── GUARD 2: specific batch queries vs faculty chunks ──────────────────
    # If the query specifies a batch number, the chunk must contain that batch.
    batch_match = re.search(r'\bbatch[-\s]?(\d)\b', q_lower)
    if batch_match:
        batch_num = batch_match.group(1)
        # Look for "batch-N" or "batch N" in chunk (case-insensitive)
        if not re.search(r'\bbatch[-\s]?' + re.escape(batch_num) + r'\b',
                         c_lower):
            return False

    # ── GUARD 3: named-scheme matching ────────────────────────────────────
    # Map each recognisable scheme identifier to tokens that MUST appear
    # in the chunk text for the chunk to be accepted.
    # Each entry: (query_triggers, required_chunk_tokens)
    # At least one required_chunk_token must be present in c_lower.
    SCHEME_RULES = [
        # OBC / Backward Classes
        (['obc', 'backward class', 'backward classes'],
         ['obc', 'backward class']),
        # NSP / National Scholarship / Minority
        (['nsp', 'national scholarship', 'minority scholarship', 'minority students'],
         ['nsp', 'national scholarship', 'minority']),
        # SSP / State Scholarship
        (['ssp', 'state scholarship', 'state scholarship portal'],
         ['ssp', 'state scholarship']),
        # SC / ST
        (['sc/st', 'sc st', 'scheduled caste', 'scheduled tribe',
          'sc scholarship', 'st scholarship', 'social welfare scholarship'],
         ['sc', 'st', 'scheduled caste', 'scheduled tribe', 'social welfare']),
        # Ex-Army
        (['ex-army', 'ex army', 'army scholarship', 'children of ex-army',
          'army staff', 'defence scholarship'],
         ['ex-army', 'army']),
        # Coffee Board
        (['coffee board', 'coffee scholarship', 'coffee curing'],
         ['coffee', 'coffee board', 'coffee curing']),
        # KSRTC
        (['ksrtc', 'ksrtc scholarship', 'ksrtc employees'],
         ['ksrtc']),
        # Railways
        (['railway scholarship', 'railway employees', 'children of railway'],
         ['railway', 'railways']),
        # Labour / Daily wage
        (['labour scholarship', 'daily wage scholarship', 'labour welfare'],
         ['labour', 'daily wage', 'daily wages']),
        # Sports / Youth Empowerment
        (['sports scholarship', 'athlete scholarship', 'youth empowerment',
          'district competition', 'state competition scholarship'],
         ['sports', 'youth empowerment', 'district', 'competition']),
        # Differently Abled
        (['differently abled', 'disabled scholarship', 'empowerment of differently'],
         ['differently abled', 'disabled']),
        # Teachers scholarship
        (['teachers scholarship', 'teacher scholarship', 'government teacher scholarship'],
         ['teacher', 'government teacher']),
        # Sitaram Jindal
        (['sitaram', 'sitaram jindal', 'jindal scholarship'],
         ['sitaram', 'jindal']),
        # Dharamshala / Sujnana Nidhi
        (['dharamshala', 'dharmasthala', 'sujnana nidhi'],
         ['dharamshala', 'dharmasthala', 'sujnana']),
        # Jalappa / Lingayat
        (['jalappa', 'veerashaiva', 'lingayat'],
         ['jalappa', 'veerashaiva', 'lingayat']),
        # Arihant
        (['arihant', 'arihant trust'],
         ['arihant']),
        # Arya Vysya / Ediga / Arasu
        (['arya vysya', 'ediga', 'arasu community'],
         ['arya vysya', 'ediga', 'arasu']),
        # HOD / Head of Department (faculty queries)
        # Triggers cover all common phrasings including reversed word order
        # and code-mixed variants. The chunk must contain 'head' or '& head'.
        (['hod', 'head of department', 'department head', 'head of dept',
          'dept head', 'head of cse', 'head of ece', 'head of ise',
          'who is the head', 'head of the'],
         ['head', 'hod', 'professor & head', '& head']),
    ]

    # Check if the query names ANY specific scheme
    named_scheme = None
    required_tokens = None
    for triggers, req_tokens in SCHEME_RULES:
        if any(trigger in q_lower for trigger in triggers):
            named_scheme = triggers[0]
            required_tokens = req_tokens
            break

    if named_scheme is not None:
        # A specific scheme is named — the chunk MUST contain at least one
        # of the required tokens for that scheme.
        if not any(tok in c_lower for tok in required_tokens):
            return False
        # Chunk passes scheme filter.
        # For scheme-specific queries the scheme guard is the primary gate;
        # the token check below needs only 1 concept hit to confirm relevance.
        _scheme_verified = True
    else:
        _scheme_verified = False

    # ── TOKEN-BASED CHECK ────────────────────────────────────────────────
    # Extract meaningful tokens from the query, expand via synonyms,
    # remove stopwords, then count hits in chunk text.
    #
    # We count by CONCEPT GROUP (each synonym set counts as one concept).
    # This means "hod" in the query expands to include "head", so a chunk
    # containing "& Head" registers a hit for the HOD concept even though
    # the literal word "hod" is not in the chunk.
    #
    # The required-hit threshold uses the raw non-stopword token count
    # (same as the original code), NOT the number of concept groups.
    # This prevents short chunks from being rejected because they cannot
    # contain every synonym in the query.
    raw_tokens = set(re.findall(r'[a-z][a-z0-9.]{2,}', q_lower))

    group_hits  = {}   # group_key → bool (any synonym in chunk text)
    covered_raw = set()

    for token in raw_tokens:
        for key, synonyms in _EVIDENCE_EQUIVALENTS.items():
            if token in synonyms or token == key:
                found = any(syn in c_lower for syn in synonyms)
                group_hits[key] = group_hits.get(key, False) or found
                covered_raw.add(token)

    # Tokens not in any synonym group — check them directly
    for token in (raw_tokens - covered_raw - _EVIDENCE_STOP):
        if len(token) >= 3:
            group_hits['_raw_' + token] = (token in c_lower)

    content_groups = {k: v for k, v in group_hits.items()
                      if k not in _EVIDENCE_STOP}

    if not content_groups:
        return True  # all stopwords — do not block broad queries

    group_hit_count = sum(1 for v in content_groups.values() if v)

    # Use raw non-stopword token count (not group count) for the threshold.
    # Requiring 2 hits only when there are 3+ distinct meaningful raw tokens
    # AND the scheme guard has not already verified chunk relevance.
    # When a named scheme was already confirmed via GUARD 3, 1 concept hit
    # is sufficient — the scheme check is the primary evidence gate.
    n_raw_non_stop = len(raw_tokens - _EVIDENCE_STOP)
    if _scheme_verified:
        required_hits = 1
    else:
        required_hits = 2 if n_raw_non_stop >= 3 else 1
    return group_hit_count >= required_hits


def format_doc_answer(chunk: dict) -> str:
    """
    Prepare document chunk text for display.
    Does NOT call answer_to_english() — document text must not be altered.
    Only strips whitespace and collapses 3+ consecutive blank lines to 1.
    """
    text = chunk.get('text', '').strip()
    text = _MULTI_BLANK.sub('\n\n', text)
    return text


def compose_doc_source(chunk: dict) -> str:
    """
    Build a source citation string from chunk metadata.
    Examples:
      "CSE Faculty List (PDF) — Page 1"
      "Scholarship Details (DOCX) — For All Category OBC Students"
    """
    label   = chunk.get('doc_label', 'College Document')
    page    = chunk.get('page')
    section = chunk.get('section', '')

    if page is not None:
        return '%s — Page %d' % (label, page)
    if section:
        return '%s — %s' % (label, section[:50])
    return label


def _load_doc_chunks():
    """
    Load doc_chunks.json and pre-compute embeddings using the already-loaded
    sentence-transformer model. Called once at server startup.

    All failures are caught; in every failure case the chatbot continues
    using normal FAQ retrieval with zero change to existing behaviour.
    """
    import json as _json
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'doc_chunks.json')
    try:
        if not os.path.exists(path):
            print('[doc_chunks] doc_chunks.json not found — document retrieval disabled.')
            return

        with open(path, encoding='utf-8') as f:
            data = _json.load(f)

        if not isinstance(data, list) or not data:
            print('[doc_chunks] doc_chunks.json is empty — document retrieval disabled.')
            return

        texts = [c.get('text', '').strip() for c in data]
        texts = [t for t in texts if t]
        if not texts:
            print('[doc_chunks] No text content in doc_chunks.json — document retrieval disabled.')
            return

        _doc_cache['chunks']     = data
        _doc_cache['embeddings'] = model.encode(texts, convert_to_tensor=True)
        print('[doc_chunks] Loaded %d document chunks.' % len(data))

    except Exception as e:
        import traceback
        print('[doc_chunks] Load error — document retrieval disabled:', e)
        traceback.print_exc()
    finally:
        _doc_cache['loaded'] = True


def doc_chunk_search(query: str):
    """
    Returns (chunk_dict, score) or (None, 0.0).

    For SPECIFIC queries (query names a scheme, batch, person, or HOD):
      1. Compute cosine similarity against all chunks.
      2. Build a candidate list of chunks that pass evidence_check().
      3. Among those candidates, return the one with the highest similarity.
      4. If NO chunk passes evidence_check(), return (None, 0.0) so that
         route_answer() cannot accidentally pick an unrelated chunk.

    For GENERAL / broad queries (no specific entity named):
      Return the globally highest-scoring chunk unchanged (same as before).
      evidence_check() is still called in route_answer() to gate final use.

    This prevents a query like "What is the OBC scholarship amount?" from
    being served by the SSP/general chunk that happens to have a higher
    cosine score than the short OBC chunk.

    Never raises — all errors return (None, 0.0).
    """
    try:
        if not _doc_cache.get('loaded') or not _doc_cache['chunks']:
            return None, 0.0
        if _doc_cache['embeddings'] is None:
            return None, 0.0

        q_emb = model.encode(normalize_for_embedding(query),
                             convert_to_tensor=True)
        sims  = util.cos_sim(q_emb, _doc_cache['embeddings'])[0]

        chunks = _doc_cache['chunks']

        if _query_is_specific(query):
            # ── Specific query: filter to evidence-passing candidates first ──
            # Build list of (index, score) for chunks that pass evidence_check.
            candidates = []
            for i, chunk in enumerate(chunks):
                if evidence_check(query, chunk):
                    candidates.append((i, float(sims[i].item())))

            if not candidates:
                # No chunk passes evidence — do not return a guess.
                return None, 0.0

            # ── HOD preference: when query asks for HOD/head, prefer chunks
            # that actually contain "head" or "hod" in their text, not a
            # generic table-header chunk like "CSE Faculty List SL NO...".
            # The header chunk may pass evidence_check because it contains
            # "faculty" + "cse", but it names nobody — it is not a useful answer.
            q_lower = query.lower()
            is_hod_query = any(t in q_lower for t in
                               ['hod', 'head of department', 'department head',
                                'dept head', 'head of dept'])
            if is_hod_query:
                hod_candidates = [
                    (i, s) for i, s in candidates
                    if any(kw in chunks[i].get('text', '').lower()
                           for kw in ['& head', 'professor & head', 'head of department'])
                ]
                if hod_candidates:
                    candidates = hod_candidates

            # Return the highest-scoring evidence-passing candidate.
            best_i, best_score = max(candidates, key=lambda x: x[1])
            return chunks[best_i], best_score

        else:
            # ── General query: global best (existing behaviour) ──
            best  = sims.argmax().item()
            score = float(sims[best].item())
            return chunks[best], score

    except Exception as e:
        print('[doc_chunk_search] Error:', e)
        return None, 0.0


# Routing thresholds (INITIAL PROPOSED VALUES — not yet calibrated against live data)
_FAQ_HIGH_CONF        = 0.70   # [PROPOSED] FAQ score above this → FAQ wins (unless specific-entity rule fires)
_DOC_USE_THRESHOLD    = 0.50   # [ADJUSTED from 0.60] minimum doc score for specific-entity CASE B;
                                # safe because CASE B also requires is_specific=True AND ev_ok=True.
                                # Unrelated-query doc scores observed: 0.087–0.432 (all below 0.50).
_DOC_PREFER_THRESHOLD = 0.75   # [PROPOSED] legacy threshold for broad doc-prefer cases


def _query_is_specific(query: str) -> bool:
    """
    Return True if the query names a SPECIFIC scheme, person, batch, or
    other identifiable detail that makes the document a better source than
    a general FAQ answer.

    This is the key gate for CASE D (doc overrides mid-confidence FAQ):
    a broad query like "scholarship details" should NOT trigger the override,
    but "OBC scholarship amount" or "batch 3 C program who teaches" should.

    We do NOT use topic keywords alone (e.g. "scholarship" by itself is not
    specific enough). The query must contain at least one identifier that
    maps to a specific chunk.
    """
    q = query.lower()
    # Specific scheme names
    specific_schemes = [
        'obc', 'backward class', 'backward classes',
        'nsp', 'national scholarship', 'minority scholarship',
        'ssp', 'state scholarship',
        'sc/st', 'sc st', 'scheduled caste', 'scheduled tribe',
        'ex-army', 'ex army', 'army scholarship',
        'coffee board', 'coffee scholarship',
        'ksrtc',
        'railway scholarship', 'children of railway',
        'labour scholarship', 'daily wage',
        'sports scholarship', 'youth empowerment',
        'differently abled', 'disabled scholarship',
        'teachers scholarship', 'teacher scholarship',
        'sitaram', 'sitaram jindal',
        'dharamshala', 'dharmasthala', 'sujnana nidhi',
        'jalappa', 'veerashaiva', 'lingayat',
        'arihant',
        'arya vysya', 'ediga', 'arasu community',
    ]
    if any(s in q for s in specific_schemes):
        return True
    # Specific batch reference
    if re.search(r'\bbatch[-\s]?\d\b', q):
        return True
    # Specific person name (Dr./Mr./Mrs./Ms. prefix)
    if re.search(r'\b(dr|mr|mrs|ms)\b\.?\s+\w', q):
        return True
    # HOD / head of department (faculty-document specific)
    # 'department head' catches "CSE department head yaaru?" which has the
    # words in reverse order compared to "head of department".
    if any(t in q for t in ['hod', 'head of department', 'department head',
                             'dept head', 'head of dept',
                             'head of cse', 'who is the head',
                             'head of the department']):
        return True
    return False


def route_answer(faq_row, faq_score, doc_chunk, doc_score,
                 user_question, sub_intent):
    """
    Deterministic routing function. Returns:
      ('faq',  None,       None)          — use existing FAQ path
      ('doc',  chunk_dict, citation_str)  — use document chunk
      ('none', None,       None)          — fall through to clarification

    Cases are evaluated in strict order; first matching case fires.
    No later case can override an earlier decision.

    CASE A — document retrieval unavailable → FAQ path (existing behaviour)
    CASE B — FAQ highly confident (>= FAQ_HIGH_CONF = 0.70) → FAQ wins.
              Exception: if the query is SPECIFIC and the doc score exceeds
              DOC_PREFER_THRESHOLD and evidence passes, document wins.
              This handles cases like "What is the OBC scholarship amount?"
              where faq=0.93 but the document has the authoritative detail.
    CASE C — FAQ acceptable (>= 0.42), doc weak or evidence fails → FAQ
    CASE D — FAQ acceptable (>= 0.42), doc strongly preferred
              (>= DOC_PREFER_THRESHOLD), query is specific, evidence passes
              → document wins (provides more specific information)
    CASE E — FAQ weak/absent (< 0.42), doc solid (>= DOC_USE_THRESHOLD),
              evidence passes → document
    CASE F — neither source useful → fall through to clarification
    """
    # CASE A: document retrieval unavailable
    if doc_chunk is None:
        return 'faq', None, None

    ev_ok       = evidence_check(user_question, doc_chunk)
    is_specific = _query_is_specific(user_question)

    # HOD SPECIAL CASE: CSE HOD queries specifically.
    # The HOD chunk (faculty_pdf_003: "Dr. Suresha D Professor & Head") is
    # only 55 chars. Its embedding score is structurally very low (0.24–0.36)
    # regardless of how well it matches the query. The score threshold cannot
    # be met, but the chunk is unambiguously the correct answer for CSE HOD.
    #
    # IMPORTANT: This override fires ONLY for CSE-specific HOD queries.
    # Non-CSE departments (AIML, ISE, ECE, EEE, Mechanical, Civil, MBA) and
    # general HOD-list queries must NOT hit this path — they have correct FAQ
    # answers that score 1.000 and should be returned via the normal FAQ route.
    #
    # CSE-specific means: query contains 'cse' or 'computer science'
    # AND does NOT contain AIML/AI ML identifiers (CSE AIML is not pure CSE).
    _hod_triggers = ['hod', 'head of department', 'department head',
                     'dept head', 'head of dept', 'head of cse',
                     'who is the head', 'head of the department']
    _cse_hod_words  = {'cse', 'computer science'}
    _aiml_hod_words = {'aiml', 'ai ml', 'ai & ml',
                       'artificial intelligence', 'machine learning'}
    q_lower_hod = user_question.lower()
    is_hod_query = any(t in q_lower_hod for t in _hod_triggers)
    is_cse_hod   = (any(t in q_lower_hod for t in _cse_hod_words) and
                    not any(t in q_lower_hod for t in _aiml_hod_words))
    chunk_is_hod = (doc_chunk is not None and
                    any(kw in doc_chunk.get('text', '').lower()
                        for kw in ['& head', 'professor & head']))
    if (is_hod_query and is_cse_hod and chunk_is_hod and ev_ok):
        return 'doc', doc_chunk, compose_doc_source(doc_chunk)

    # CASE B: specific-entity document rule.
    # When all three conditions hold simultaneously:
    #   1. Query names a specific scheme/entity (_query_is_specific = True)
    #   2. evidence_check confirms this chunk matches the query
    #   3. doc score >= DOC_USE_THRESHOLD (rules out noise; 0.60 is well above
    #      unrelated-query scores of 0.08–0.43)
    # then the document wins regardless of FAQ score.
    #
    # Rationale: for specific-entity queries the FAQ answers are curated
    # general-purpose text that overlaps semantically but is not more specific
    # than the source document. evidence_check + _query_is_specific together
    # confirm the chunk is the authoritative source for this exact entity.
    #
    # Safety: this does NOT fire for broad queries ("scholarship details",
    # "what scholarships exist?") because those fail _query_is_specific().
    # It also does NOT fire when evidence_check is False (wrong chunk).
    # It does NOT fire when doc_score < 0.60 (noise / poor match).
    if (is_specific and
            ev_ok and
            doc_score >= _DOC_USE_THRESHOLD):
        return 'doc', doc_chunk, compose_doc_source(doc_chunk)

    # CASE C: FAQ highly confident and query did not qualify for CASE B
    if faq_score >= _FAQ_HIGH_CONF:
        return 'faq', None, None

    # CASE D: FAQ acceptable (>= 0.42), doc weak or evidence fails → FAQ
    if faq_score >= 0.42 and (doc_score < _DOC_USE_THRESHOLD or not ev_ok):
        return 'faq', None, None

    # CASE E: FAQ acceptable, doc strongly preferred, specific, evidence OK
    # (kept as a safety net; most cases now handled by CASE B)
    if (faq_score >= 0.42 and
            doc_score >= _DOC_PREFER_THRESHOLD and
            is_specific and
            ev_ok):
        return 'doc', doc_chunk, compose_doc_source(doc_chunk)

    # CASE F: FAQ weak/absent, doc solid, evidence OK
    if (faq_score < 0.42 and
            doc_score >= _DOC_USE_THRESHOLD and
            ev_ok):
        return 'doc', doc_chunk, compose_doc_source(doc_chunk)

    # CASE G: neither useful
    return 'none', None, None


# Load document chunks now (module-level call).
# Works for both direct run (python app.py) and WSGI imports.
# If doc_chunks.json is absent, this is a no-op.
_load_doc_chunks()


# ==========================================================
#  AUTH ROUTES
# ==========================================================
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        existing = User.query.filter_by(email=email).first()
        if existing:
            return render_template('signup.html',
                                   error="An account with this email already exists.")
        hashed_pw = generate_password_hash(password)
        db.session.add(User(email=email, password_hash=hashed_pw))
        db.session.commit()
        session['user_email'] = email
        return redirect(url_for('chat_page'))
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login():
    email    = request.form.get('email')
    password = request.form.get('password')
    user     = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_email'] = email
        return redirect(url_for('chat_page'))
    return render_template('login.html', error="Incorrect email or password.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ==========================================================
#  CHAT ROUTES
# ==========================================================
@app.route('/chat')
def chat_page():
    if 'user_email' not in session:
        return redirect(url_for('home'))
    history = ChatMessage.query.filter_by(
        user_email=session['user_email']
    ).order_by(ChatMessage.timestamp.asc()).all()
    return render_template('chat.html', history=history)


def translate_voice_answer(answer: str, input_mode: str, speech_lang: str) -> str:
    if input_mode != 'voice':
        return answer
    # MyMemory language codes for Kannada and Hindi.
    # 'en-IN' is not in this map so it falls through to the early return below.
    target_language = {'kn-IN': 'kn-IN', 'hi-IN': 'hi-IN'}.get(speech_lang)
    if not target_language:
        return answer
    try:
        translated = MyMemoryTranslator(source='en-US', target=target_language).translate(answer)
        return translated if translated else answer
    except Exception:
        return answer


@app.route('/ask', methods=['POST'])
def ask():
    if 'user_email' not in session:
        return jsonify({"answer": "Please log in first."}), 401

    user_question = request.json.get('question', '').strip()
    input_mode = request.json.get('input_mode', 'typed')
    speech_lang = request.json.get('speech_lang', 'en-IN')
    if not user_question:
        return jsonify({"answer": "Please type a question."})

    detected_lang = detect_language(user_question)

    # Initialise so they're always defined even if an exception fires late
    final_category = None
    final_sub      = None
    answer_text    = DEFAULT_CLARIFICATION
    best_faq       = None
    best_score     = 0.0
    doc_source_out = None   # source citation for document-retrieved answers

    try:
        # ── Step 1: Classify intent ──
        primary, sub = classify_intent(user_question)

        # ── Step 2: Resolve via context (follow-up questions) ──
        primary, sub = resolve_intent_with_context(user_question, primary, sub)

        # ── Step 3: Semantic search (intent-filtered) ──
        best_faq, best_score = semantic_search(user_question, primary, sub)

        # ── Step 3b: Document chunk search (parallel, additive) ──
        doc_chunk, doc_score = doc_chunk_search(user_question)

        # ── Step 3c: Routing decision ──
        route, chosen_chunk, doc_citation = route_answer(
            best_faq, best_score, doc_chunk, doc_score,
            user_question, sub
        )

        # ── Step 4: Decide response ──
        LOW_CONFIDENCE = 0.35
        MED_CONFIDENCE = 0.42

        if route == 'doc':
            # ── Document chunk answer ──────────────────────────
            answer_text    = format_doc_answer(chosen_chunk)
            final_category = chosen_chunk.get('doc_label', 'Document')
            final_sub      = None
            doc_source_out = doc_citation
            push_context(final_category, sub or '', user_question)

        elif route == 'faq' or route == 'none':
            # ── Normal FAQ path (completely unchanged) ─────────
            doc_source_out = None
            if best_faq is None or best_score < LOW_CONFIDENCE:
                answer_text    = DEFAULT_CLARIFICATION
                final_category = None
                final_sub      = None
                db.session.add(UnansweredQuestion(
                    user_email = session['user_email'],
                    question   = user_question,
                    best_score = round(best_score, 2)
                ))

            elif best_score < MED_CONFIDENCE:
                cat            = best_faq['category']
                answer_text    = CLARIFICATIONS.get(cat, DEFAULT_CLARIFICATION)
                final_category = cat
                final_sub      = sub

            else:
                answer_text    = answer_to_english(
                    extract_focused_answer(best_faq['answer'], sub or '', user_question)
                )
                final_category = best_faq['category']
                final_sub      = sub
                push_context(final_category, sub or '', user_question)

        answer_text = translate_voice_answer(answer_text, input_mode, speech_lang)
        message_source_doc = doc_source_out or (
            (best_faq.get('source_doc') or None) if best_faq else None
        )

        # ── Step 5: Persist chat entry ──
        chat_entry = ChatMessage(
            user_email        = session['user_email'],
            question          = user_question,
            answer            = answer_text,
            category          = final_category,
            sub_intent        = final_sub,
            confidence        = round(best_score, 2),
            detected_language = detected_lang,
            source_doc        = message_source_doc
        )
        db.session.add(chat_entry)
        db.session.commit()

    except Exception as e:
        # Roll back any partial DB write so the session stays healthy
        db.session.rollback()
        # Log the real error to the terminal so it appears in server output
        import traceback
        print("\n[/ask ERROR]", repr(e))
        traceback.print_exc()
        return jsonify({
            "answer"          : "Sorry, something went wrong on the server. Please try again.",
            "detected_language": detected_lang,
            "message_id"      : None
        }), 500

    return jsonify({
        "answer"          : answer_text,
        "matched_question": best_faq['question'] if best_faq else None,
        "category"        : final_category,
        "sub_intent"      : final_sub,
        "confidence"      : round(best_score, 2),
        "detected_language": detected_lang,
        "source_doc"      : doc_source_out if doc_source_out else (
                                (best_faq.get('source_doc') or None) if best_faq else None
                            ),
        "message_id"      : chat_entry.id
    })


@app.route('/feedback', methods=['POST'])
def feedback():
    if 'user_email' not in session:
        return jsonify({"status": "error"}), 401
    message_id = request.json.get('message_id')
    vote       = request.json.get('vote')
    msg        = ChatMessage.query.get(message_id)
    if msg and msg.user_email == session['user_email']:
        msg.feedback = vote
        db.session.commit()
        return jsonify({"status": "ok"})
    return jsonify({"status": "not_found"}), 404


# ==========================================================
#  SUGGESTED QUESTIONS  (shown as quick-start pills in chat UI)
# ==========================================================
SUGGESTED_QUESTIONS = [
    "Who is the principal of RIT Hassan?",
    "CSE HOD yaru?",
    "Who are the CSE faculty members?",
    "Hostel fees eshtu?",
    "How many seats in CSE?",
    "College bus facility ideya?",
    "Placement statistics kodi",
    "Scholarship details kodi",
    "What is the minimum attendance?",
    "Library details kodi",
    "What are the college contact details?",
    "CIE exam dates kodi",
]

@app.route('/suggest')
def suggest():
    if 'user_email' not in session:
        return jsonify({"questions": []}), 401
    return jsonify({"questions": SUGGESTED_QUESTIONS})


# ==========================================================
#  ADMIN ROUTES
# ==========================================================
def require_admin():
    if 'user_email' not in session:
        return None
    user = User.query.filter_by(email=session['user_email']).first()
    return user if (user and user.is_admin) else None

@app.route('/admin')
def admin_panel():
    if not require_admin():
        return "Access denied. Admins only.", 403

    all_faqs        = FAQ.query.all()
    total_queries   = ChatMessage.query.count()
    thumbs_up       = ChatMessage.query.filter_by(feedback="up").count()
    thumbs_down     = ChatMessage.query.filter_by(feedback="down").count()
    avg_conf_row    = db.session.query(db.func.avg(ChatMessage.confidence)).scalar()
    avg_confidence  = round(avg_conf_row, 2) if avg_conf_row else 0

    category_counts = db.session.query(
        ChatMessage.category, db.func.count(ChatMessage.id)
    ).filter(ChatMessage.category.isnot(None)).group_by(
        ChatMessage.category
    ).order_by(db.func.count(ChatMessage.id).desc()).all()

    unanswered = UnansweredQuestion.query.order_by(
        UnansweredQuestion.timestamp.desc()
    ).limit(30).all()

    return render_template(
        'admin.html',
        faqs            = all_faqs,
        total_queries   = total_queries,
        thumbs_up       = thumbs_up,
        thumbs_down     = thumbs_down,
        avg_confidence  = avg_confidence,
        category_counts = category_counts,
        unanswered      = unanswered
    )

@app.route('/admin/add', methods=['POST'])
def admin_add_faq():
    if not require_admin():
        return "Access denied. Admins only.", 403
    db.session.add(FAQ(
        category = request.form.get('category'),
        question = request.form.get('question'),
        answer   = request.form.get('answer'),
        language = request.form.get('language')
    ))
    db.session.commit()
    _faq_cache['count'] = -1   # force rebuild on next request
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete/<int:faq_id>', methods=['POST'])
def admin_delete_faq(faq_id):
    if not require_admin():
        return "Access denied. Admins only.", 403
    faq = FAQ.query.get(faq_id)
    if faq:
        db.session.delete(faq)
        db.session.commit()
        _faq_cache['count'] = -1   # force rebuild on next request
    return redirect(url_for('admin_panel'))

@app.route('/admin/unanswered/delete/<int:uq_id>', methods=['GET', 'POST'])
def admin_delete_unanswered(uq_id):
    if not require_admin():
        return "Access denied. Admins only.", 403
    uq = UnansweredQuestion.query.get(uq_id)
    if uq:
        db.session.delete(uq)
        db.session.commit()
    return redirect(url_for('admin_panel'))


@app.route('/admin/edit/<int:faq_id>', methods=['POST'])
def admin_edit_faq(faq_id):
    if not require_admin():
        return "Access denied. Admins only.", 403
    faq = FAQ.query.get(faq_id)
    if faq:
        faq.category = request.form.get('category', faq.category).strip()
        faq.question = request.form.get('question', faq.question).strip()
        faq.answer   = request.form.get('answer',   faq.answer).strip()
        faq.language = request.form.get('language', faq.language)
        db.session.commit()
        _faq_cache['count'] = -1   # force full cache rebuild
    return redirect(url_for('admin_panel'))


@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Allow a logged-in user to delete their own chat history."""
    if 'user_email' not in session:
        return jsonify({"status": "error"}), 401
    try:
        ChatMessage.query.filter_by(user_email=session['user_email']).delete()
        db.session.commit()
        session.pop('chat_context', None)   # also clear the in-session context window
        return jsonify({"status": "ok"})
    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        return jsonify({"status": "error", "detail": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    _load_doc_chunks()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
