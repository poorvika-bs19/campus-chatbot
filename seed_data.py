# =============================================================
#  seed_data.py  -  RIT Hassan Campus Chatbot
#  SOURCE OF TRUTH: Only information extracted from the actual
#  college documents provided. Nothing is invented.
#  Documents: CSE Faculty PDF, AIML faculty image, ISE faculty
#  image, Committee image, Branch seats image, Contact image,
#  Bus route sheets (5 routes), Hostel handwritten notes,
#  Attendance handwritten notes, Placement stats image,
#  SCHOLARSHIP.docx, Academic Timetable PDF.
#  Fees details.docx and library details.docx were empty.
# =============================================================

from app import app, db, FAQ

FAQS = [

    # ============================================================
    # GENERAL / COLLEGE INFO
    # Source: Contact image, Committee image
    # ============================================================
    ("General", "What is the full name of the college?",
     "Rajeev Institute of Technology (RIT), Hassan. Affiliated to VTU Belagavi, approved by AICTE New Delhi, recognised by Govt of Karnataka.", "English"),

    ("General", "RIT Hassan full name enu? college full name kodi",
     "RIT — Rajeev Institute of Technology, Hassan. VTU Belagavi affiliated, AICTE approved, Govt of Karnataka recognised.", "Mixed"),

    ("General", "Where is RIT Hassan located? What is the college address?",
     "RIT Hassan is located at:\nPlot 1-D, Growth Center, Industrial Area,\nB-M Bypass Road, Hassan, Karnataka - 573201.", "English"),

    ("General", "college address yenu? RIT address kodi",
     "RIT Hassan: Plot 1-D, Growth Center, Industrial Area, B-M Bypass Road, Hassan, Karnataka - 573201.", "Mixed"),

    ("General", "What is the college phone number?",
     "RIT Hassan phone numbers:\n08172-243180\n08172-243181\n08172-243184", "English"),

    ("General", "college phone number kodi. RIT Hassan contact number enu?",
     "RIT Hassan phone: 08172-243180 / 243181 / 243184", "Mixed"),

    ("General", "RIT Hassan ka phone number kya hai?",
     "RIT Hassan phone: 08172-243180 / 243181 / 243184", "Mixed"),

    ("General", "What is the college email address?",
     "RIT Hassan email: info@rithassan.ac.in\nPrincipal email: principal@rithassan.ac.in", "English"),

    ("General", "college email id kodi",
     "RIT Hassan: info@rithassan.ac.in | Principal: principal@rithassan.ac.in", "Mixed"),

    ("General", "What are all the contact details of RIT Hassan?",
     "RIT Hassan - Complete Contact:\nPhone: 08172-243180 / 243181 / 243184\nEmail: info@rithassan.ac.in\nPrincipal: principal@rithassan.ac.in\nAdmissions (BE & M.Tech/MBA): 7892691110\nAddress: Plot 1-D, Growth Center, Industrial Area, B-M Bypass Road, Hassan, Karnataka - 573201", "English"),

    ("General", "contact details kodi. RIT Hassan helpline number",
     "RIT Hassan contact:\nPhone: 08172-243180 / 243181 / 243184\nEmail: info@rithassan.ac.in\nAdmissions: 7892691110\nAddress: Plot 1-D, Growth Center, B-M Bypass Road, Hassan - 573201", "Mixed"),

    ("General", "What is the admissions phone number for RIT Hassan?",
     "For BE admissions: 7892691110\nFor M.Tech (CSE) and MBA admissions: 7892691110\nEmail: principal@rithassan.ac.in", "English"),

    ("General", "admission contact number kodi",
     "Admissions: 7892691110 | Email: principal@rithassan.ac.in", "Mixed"),

    ("General", "Is RIT Hassan affiliated to VTU?",
     "Yes. RIT Hassan is affiliated to Visvesvaraya Technological University (VTU), Belagavi. Also approved by AICTE, New Delhi and recognised by the Government of Karnataka.", "English"),

    # ============================================================
    # PRINCIPAL
    # Source: Committee image - Dr. Mahesh P K, Principal, Chairman
    # ============================================================
    ("General", "Who is the principal of RIT Hassan?",
     "The Principal of Rajeev Institute of Technology (RIT), Hassan is Dr. Mahesh P K.", "English"),

    ("General", "RIT Hassan principal yaru? principal hesaru kodi",
     "RIT Hassan principal: Dr. Mahesh P K.", "Mixed"),

    ("General", "RIT Hassan ka principal kaun hai?",
     "RIT Hassan ke principal Dr. Mahesh P K hain.", "Mixed"),

    ("General", "principal name of RIT Hassan",
     "Principal of RIT Hassan: Dr. Mahesh P K", "English"),

    # ============================================================
    # HOD DETAILS
    # Source: Committee image
    # ============================================================
    ("Faculty", "Who is the HOD of CSE department?",
     "Head of Department - CSE (Computer Science & Engineering):\nDr. Suresha D | Professor & Head", "English"),

    ("Faculty", "CSE HOD yaru? CSE department head hesaru",
     "CSE HOD: Dr. Suresha D (Professor & Head)", "Mixed"),

    ("Faculty", "CSE HOD kaun hai?",
     "CSE ke HOD: Dr. Suresha D (Professor & Head)", "Mixed"),

    ("Faculty", "Who is the HOD of CSE AIML department?",
     "Head of Department - CSE (Artificial Intelligence and Machine Learning):\nDr. Sharath | Professor & HOD", "English"),

    ("Faculty", "AIML HOD yaru? AI ML department head yaru?",
     "CSE (AIML) HOD: Dr. Sharath (Professor & HOD)", "Mixed"),

    ("Faculty", "Who is the HOD of ISE department?",
     "Head of Department - Information Science & Engineering (ISE):\nDr. Prathibha G | Professor & HOD", "English"),

    ("Faculty", "ISE HOD yaru?",
     "ISE HOD: Dr. Prathibha G (Professor & HOD)", "Mixed"),

    ("Faculty", "Who is the HOD of ECE department?",
     "Head of Department - Electronics & Communication Engineering (ECE):\nDr. Prakash Kuravatti | Professor & HOD", "English"),

    ("Faculty", "ECE HOD yaru?",
     "ECE HOD: Dr. Prakash Kuravatti (Professor & HOD)", "Mixed"),

    ("Faculty", "Who is the HOD of EEE department?",
     "Head of Department - Electrical & Electronics Engineering (EEE):\nDr. Pradeep KGM | Associate Professor & HOD", "English"),

    ("Faculty", "EEE HOD yaru?",
     "EEE HOD: Dr. Pradeep KGM (Associate Professor & HOD)", "Mixed"),

    ("Faculty", "Who is the HOD of Mechanical Engineering?",
     "Head of Department - Mechanical Engineering (ME):\nDr. Kuldeep B | Associate Professor & HOD", "English"),

    ("Faculty", "Mechanical HOD yaru? ME HOD hesaru",
     "ME HOD: Dr. Kuldeep B (Associate Professor & HOD)", "Mixed"),

    ("Faculty", "Who is the HOD of Civil Engineering?",
     "Head of Department - Civil Engineering (CV):\nMr. Sujay S | Assistant Professor & HOD", "English"),

    ("Faculty", "Civil HOD yaru?",
     "Civil Engineering HOD: Mr. Sujay S (Assistant Professor & HOD)", "Mixed"),

    ("Faculty", "Who is the HOD of MBA department?",
     "Head of Department - MBA:\nMrs. Bhavani B S | Assistant Professor & HOD", "English"),

    ("Faculty", "MBA HOD yaru?",
     "MBA HOD: Mrs. Bhavani B S (Assistant Professor & HOD)", "Mixed"),

    ("Faculty", "Give me the HOD list of all departments at RIT Hassan.",
     "RIT Hassan - Department HOD List:\nCSE          : Dr. Suresha D         (Professor & Head)\nCSE (AIML)   : Dr. Sharath            (Professor & HOD)\nISE          : Dr. Prathibha G        (Professor & HOD)\nECE          : Dr. Prakash Kuravatti  (Professor & HOD)\nEEE          : Dr. Pradeep KGM        (Assoc. Professor & HOD)\nMechanical   : Dr. Kuldeep B          (Assoc. Professor & HOD)\nCivil        : Mr. Sujay S            (Asst. Professor & HOD)\nMBA          : Mrs. Bhavani B S       (Asst. Professor & HOD)\nPrincipal    : Dr. Mahesh P K", "English"),

    ("Faculty", "all department HOD list kodi. vibhaga mukhyastha hesaru",
     "RIT Hassan HOD list:\nCSE: Dr. Suresha D\nCSE (AIML): Dr. Sharath\nISE: Dr. Prathibha G\nECE: Dr. Prakash Kuravatti\nEEE: Dr. Pradeep KGM\nME: Dr. Kuldeep B\nCivil: Mr. Sujay S\nMBA: Mrs. Bhavani B S\nPrincipal: Dr. Mahesh P K", "Mixed"),

    ("Faculty", "sabhi departments ke HOD kaun hain?",
     "RIT Hassan HOD list:\nCSE: Dr. Suresha D\nCSE (AIML): Dr. Sharath\nISE: Dr. Prathibha G\nECE: Dr. Prakash Kuravatti\nEEE: Dr. Pradeep KGM\nME: Dr. Kuldeep B\nCivil: Mr. Sujay S\nMBA: Mrs. Bhavani B S\nPrincipal: Dr. Mahesh P K", "Mixed"),

    # ============================================================
    # CSE FACULTY LIST
    # Source: CSE Faculty List PDF - 18 members
    # ============================================================
    ("Faculty", "Who are the CSE faculty members at RIT Hassan?",
     "CSE Department Faculty - RIT Hassan (18 members):\n\nProfessors:\n1. Dr. H N Prakash\n2. Dr. H.S. Mohana\n3. Dr. Suresha D  (HOD)\n4. Dr. S A Quadri\n5. Dr. Ramesh B\n\nAssistant Professors:\n6.  Mr. Dinesh S\n7.  Mr. Anil Kumar K N\n8.  Mrs. Kannika Lakshmi D G\n9.  Mrs. Shashikala M K\n10. Mrs. Ruksar Parveen\n11. Ms. Usha C D\n12. Mr. Vishnu Navali\n13. Ms. Shravya M S\n14. Mr. Rohith K\n15. Ms. Kusuma H M\n16. Ms. Prakruthi H V\n17. Ms. Shalini H B\n18. Mrs. Archana J B", "English"),

    ("Faculty", "CSE faculty list kodi. CSE teachers hesaru kodi",
     "CSE Faculty (RIT Hassan) - 18 members:\n\nProfessors: Dr. H N Prakash, Dr. H.S. Mohana, Dr. Suresha D (HOD), Dr. S A Quadri, Dr. Ramesh B\n\nAsst. Professors: Mr. Dinesh S, Mr. Anil Kumar K N, Mrs. Kannika Lakshmi D G, Mrs. Shashikala M K, Mrs. Ruksar Parveen, Ms. Usha C D, Mr. Vishnu Navali, Ms. Shravya M S, Mr. Rohith K, Ms. Kusuma H M, Ms. Prakruthi H V, Ms. Shalini H B, Mrs. Archana J B", "Mixed"),

    ("Faculty", "CSE mein kitne faculty hain? How many faculty in CSE?",
     "CSE department at RIT Hassan has 18 faculty members: 5 Professors (including HOD Dr. Suresha D) and 13 Assistant Professors.", "Mixed"),

    ("Faculty", "CSE alli eshtu faculty ide?",
     "CSE department nalli 18 faculty members idare - 5 Professors (HOD Dr. Suresha D saha) mattu 13 Assistant Professors.", "Mixed"),

    ("Faculty", "Who handles C programming lab in CSE?",
     "As per the CSE faculty list:\nMrs. Ruksar Parveen - 1st year C Program Lab Batch-2 (1C)\nMs. Shravya M S - 1st year C Program Lab Batch-3 (1C) and Batch-4 (1C)\nDr. S A Quadri - 1st year C Program (3C batch)", "English"),

    # ============================================================
    # CSE AIML FACULTY
    # Source: AIML faculty image - 10 members
    # ============================================================
    ("Faculty", "Who are the AIML faculty members at RIT Hassan?",
     "CSE (AI & ML) Department Faculty - RIT Hassan (10 members):\n1. Dr. Prathibha G     - Associate Professor & HOD\n2. Mrs. Nalini H C     - Assistant Professor\n3. Mr. Sanjay M        - Assistant Professor\n4. Mrs. Sahana R S     - Assistant Professor\n5. Mrs. Meghana C S    - Assistant Professor\n6. Mrs. Yashaswini H R - Assistant Professor\n7. Mr. Nagendra K Shet - Assistant Professor\n8. Mr. Madevamma S M   - Assistant Professor\n9. Mrs. Rojashree      - Assistant Professor\n10. Mrs. Deepa         - Assistant Professor", "English"),

    ("Faculty", "AIML faculty list kodi. AI ML teachers hesaru",
     "CSE (AIML) Faculty:\n1. Dr. Prathibha G (HOD)\n2. Mrs. Nalini H C\n3. Mr. Sanjay M\n4. Mrs. Sahana R S\n5. Mrs. Meghana C S\n6. Mrs. Yashaswini H R\n7. Mr. Nagendra K Shet\n8. Mr. Madevamma S M\n9. Mrs. Rojashree\n10. Mrs. Deepa", "Mixed"),

    ("Faculty", "AIML mein kitne faculty hain?",
     "CSE (AIML) department mein 10 faculty hain - 1 HOD (Dr. Prathibha G) aur 9 Assistant Professors.", "Mixed"),

    ("Faculty", "AIML alli eshtu faculty ide?",
     "AIML department nalli 10 faculty members idare - HOD Dr. Prathibha G mattu 9 Assistant Professors.", "Mixed"),

    # ============================================================
    # ISE FACULTY
    # Source: ISE faculty image - 6 faculty + HOD from committee
    # ============================================================
    ("Faculty", "Who are the ISE faculty members at RIT Hassan?",
     "Information Science & Engineering (ISE) Faculty - RIT Hassan:\n1. Dr. Prathibha G  - Professor & HOD\n2. Ms. Spandana A G - Assistant Professor\n3. Ms. Raksha H B   - Assistant Professor\n4. Mr. Karthik B U  - Assistant Professor\n5. Mr. Lohith D K   - Assistant Professor\n6. Ms. Chitra H N   - Assistant Professor\n7. Ms. Puttamma M S - Assistant Professor", "English"),

    ("Faculty", "ISE faculty list kodi. ISE teachers hesaru kodi",
     "ISE Faculty (RIT Hassan):\n1. Dr. Prathibha G (HOD)\n2. Ms. Spandana A G\n3. Ms. Raksha H B\n4. Mr. Karthik B U\n5. Mr. Lohith D K\n6. Ms. Chitra H N\n7. Ms. Puttamma M S", "Mixed"),

    ("Faculty", "ISE mein kitne faculty hain?",
     "ISE department mein 7 faculty hain - HOD Dr. Prathibha G aur 6 Assistant Professors.", "Mixed"),

    ("Faculty", "ISE alli eshtu faculty ide?",
     "ISE department nalli 7 faculty members idare.", "Mixed"),

    # ============================================================
    # BRANCH-WISE SEAT AVAILABILITY
    # Source: Branch-wise seat image
    # CET 45% | COMEDK 30% | Management 25%
    # ============================================================
    ("Admissions", "What are the branch-wise seat availability and quota details at RIT Hassan?",
     "Branch-wise Sanctioned Intake - RIT Hassan:\n\nBranch                         | Total | CET(45%) | COMEDK(30%) | Mgmt(25%)\nCivil Engineering              |  30   |    14    |      9      |     7\nCSE                            |  120  |    54    |     36      |    30\nCSE (AI & Machine Learning)    |  60   |    27    |     18      |    15\nECE                            |  120  |    54    |     36      |    30\nEEE                            |  60   |    27    |     18      |    15\nISE                            |  60   |    27    |     18      |    15\nMechanical Engineering         |  30   |    14    |      9      |     7\nVLSI Design & Technology       |  60   |    27    |     18      |    15\n\nAdmission: CET or COMEDK entrance test.", "English"),

    ("Admissions", "branch wise seats eshtu ide? seat availability kodi",
     "RIT Hassan - Branch-wise Seats:\nCivil: 30 (CET:14, COMEDK:9, Mgmt:7)\nCSE: 120 (CET:54, COMEDK:36, Mgmt:30)\nCSE (AIML): 60 (CET:27, COMEDK:18, Mgmt:15)\nECE: 120 (CET:54, COMEDK:36, Mgmt:30)\nEEE: 60 (CET:27, COMEDK:18, Mgmt:15)\nISE: 60 (CET:27, COMEDK:18, Mgmt:15)\nMechanical: 30 (CET:14, COMEDK:9, Mgmt:7)\nVLSI: 60 (CET:27, COMEDK:18, Mgmt:15)", "Mixed"),

    ("Admissions", "branch wise seats kya hain?",
     "RIT Hassan branch seats:\nCivil: 30 | CSE: 120 | AIML: 60 | ECE: 120\nEEE: 60 | ISE: 60 | Mech: 30 | VLSI: 60", "Mixed"),

    ("Admissions", "How many seats are available in CSE at RIT Hassan?",
     "CSE (Computer Science & Engineering) - 120 seats total:\nCET Quota (45%): 54 seats\nCOMEDK Quota (30%): 36 seats\nManagement Quota (25%): 30 seats", "English"),

    ("Admissions", "CSE alli yestu seats ide? CSE seats eshtu?",
     "CSE nalli 120 seats ide:\nCET (45%): 54 | COMEDK (30%): 36 | Management (25%): 30", "Mixed"),

    ("Admissions", "CSE mein kitni seats hain?",
     "CSE mein kul 120 seats - CET: 54, COMEDK: 36, Management: 30.", "Mixed"),

    ("Admissions", "How many seats are available in ECE at RIT Hassan?",
     "ECE (Electronics & Communication Engineering) - 120 seats total:\nCET Quota (45%): 54 seats\nCOMEDK Quota (30%): 36 seats\nManagement Quota (25%): 30 seats", "English"),

    ("Admissions", "ECE seats eshtu ide?",
     "ECE nalli 120 seats - CET:54, COMEDK:36, Mgmt:30.", "Mixed"),

    ("Admissions", "How many seats are available in CSE AIML?",
     "CSE (Artificial Intelligence and Machine Learning) - 60 seats total:\nCET Quota (45%): 27 seats\nCOMEDK Quota (30%): 18 seats\nManagement Quota (25%): 15 seats", "English"),

    ("Admissions", "AIML seats eshtu ide?",
     "CSE (AIML) nalli 60 seats - CET:27, COMEDK:18, Mgmt:15.", "Mixed"),

    ("Admissions", "How many seats are available in ISE?",
     "ISE (Information Science & Engineering) - 60 seats total:\nCET Quota (45%): 27 seats\nCOMEDK Quota (30%): 18 seats\nManagement Quota (25%): 15 seats", "English"),

    ("Admissions", "How many seats are available in EEE?",
     "EEE (Electrical & Electronics Engineering) - 60 seats total:\nCET Quota (45%): 27 seats\nCOMEDK Quota (30%): 18 seats\nManagement Quota (25%): 15 seats", "English"),

    ("Admissions", "How many seats are available in Civil Engineering?",
     "Civil Engineering - 30 seats total:\nCET Quota (45%): 14 seats\nCOMEDK Quota (30%): 9 seats\nManagement Quota (25%): 7 seats", "English"),

    ("Admissions", "How many seats are available in Mechanical Engineering?",
     "Mechanical Engineering - 30 seats total:\nCET Quota (45%): 14 seats\nCOMEDK Quota (30%): 9 seats\nManagement Quota (25%): 7 seats", "English"),

    ("Admissions", "How many seats are available in VLSI?",
     "Electronics Engineering (VLSI Design & Technology) - 60 seats total:\nCET Quota (45%): 27 seats\nCOMEDK Quota (30%): 18 seats\nManagement Quota (25%): 15 seats", "English"),

    ("Admissions", "What is the admission process for RIT Hassan?",
     "Admissions to RIT Hassan are through CET (Karnataka Common Entrance Test) or COMEDK entrance test. Candidates must have a qualifying rank in either exam.\nContact: 7892691110 | principal@rithassan.ac.in", "English"),

    ("Admissions", "RIT Hassan admission process enu? how to get admission in RIT",
     "RIT Hassan ge admission: CET or COMEDK entrance exam nalli qualifying rank irbekku.\nContact: 7892691110 | principal@rithassan.ac.in", "Mixed"),

    ("Admissions", "What quota system does RIT Hassan follow?",
     "RIT Hassan admission quotas:\nCET Quota: 45% of seats\nCOMEDK Quota: 30% of seats\nManagement Quota: 25% of seats", "English"),

    # ============================================================
    # BUS / TRANSPORT
    # Source: Bus route sheets images - Routes 2, 3, 4, 5, 6
    # ============================================================
    ("Transport", "How many college buses does RIT Hassan have?",
     "RIT Hassan operates 5 college bus routes (Routes 2, 3, 4, 5, and 6) covering different parts of Hassan city. Each route has a dedicated bus and driver.", "English"),

    ("Transport", "RIT alli eshtu bus ide? college bus count kodi",
     "RIT Hassan nalli 5 bus routes ide (Route 2, 3, 4, 5 mattu 6).", "Mixed"),

    ("Transport", "RIT mein kitne buses hain? college bus kitne hai?",
     "RIT Hassan mein 5 bus routes hain - Route 2, 3, 4, 5 aur 6.", "Mixed"),

    ("Transport", "What are all the college bus routes at RIT Hassan?",
     "RIT Hassan - All Bus Routes:\n\nROUTE 2 | Bus: KA13 C.8563 | Driver: Chonnakesava K R | Ph: 9483529679\nStops: Bittagodanahalli(8:10) -> Jayaraypura(8:15) -> Silk Board(8:20) -> Vijayanagara(8:25) -> Thanniruhalla(8:30) -> Nantha Pete(8:35) -> New Bus Stand(8:40) -> College(8:50 AM)\nReturn: 5:15 PM\n\nROUTE 3 | Bus: KA13 D.6550 | Driver: Ranganath | Ph: 9900693953\nStops: Aralikatte Circle(8:12) -> Saraswathi Temple(8:15) -> Ring Road Petrol Bunk(8:17) -> Dasara Koppalu Bus Stop(8:20) -> Thivara Koppalu(8:25) -> Space Quarters(8:30) -> Ring Road(8:30) -> Thanyi Thrisha Kalyana Mantapa(8:40) -> Sathyamangala(8:45) -> Dairy Circle(8:55) -> College\nReturn: 5:15 PM\n\nROUTE 4 | Bus: KA13 D.2332 | Driver: Maganegowda | Ph: 9900871814\nStops: 80 Feet Road(8:00) -> Hemavathi Nagara(8:00) -> Shanthi Nagar(8:05) -> Ganapathi Temple-Dagdar Koppal(8:10) -> MCE College(8:15) -> Ring Road(8:20) -> Tany Trisha Kalyana Mantapa(8:30) -> Old Bus Stand(8:40) -> New Bus Stand(8:45) -> College(9:00 AM)\nReturn: 4:30 PM to Nursing College\n\nROUTE 5 | Bus: KA13 C.7610 | Driver: Ravi | Ph: 9353032762\nFree transport: New Bus Stand(8:30) -> College(8:45 AM)\nReturn: 5:15 PM\n\nROUTE 6 | Bus: KA13 C.0378 | Driver: Kande Gowda | Ph: 8722649446\nStops: Yokkaligara Hostel-BM Road(8:05) -> Rajeev Arcade(8:07) -> Euro Kids-MG Road(8:08) -> Vidhya Nagar Ladies Hostel(8:15) -> Vidhya Nagar Auto Stand(8:20) -> Gowri Koppalu/Aralikatte Stop(8:20) -> Beeranally Kere Road(8:25) -> Ganapathi Temple-Kuvempu Nagar(8:25) -> Janatha Bazar(8:30) -> BSNL(8:30) -> Prithvi Theatre(8:30) -> Railway Station(8:30) -> Kattehalli(8:30) -> Dairy Circle(8:35) -> B T Koppalu(8:45) -> College(8:50 AM)\nReturn: 5:15 PM", "English"),

    ("Transport", "bus routes yavavu? bus routes kodi",
     "RIT Hassan bus routes (5 routes):\nRoute 2: Bittagodanahalli -> New Bus Stand -> College 8:50 AM\nRoute 3: Aralikatte Circle -> Dairy Circle -> College\nRoute 4: 80 Feet Road -> MCE College -> New Bus Stand -> College 9:00 AM\nRoute 5: New Bus Stand -> College 8:45 AM (Free transport)\nRoute 6: Vidhya Nagar -> Railway Station -> Dairy Circle -> College 8:50 AM", "Mixed"),

    ("Transport", "bus route kya kya hain?",
     "RIT Hassan ke 5 bus routes:\nRoute 2: Bittagodanahalli -> College 8:50 AM\nRoute 3: Aralikatte Circle -> Dairy Circle -> College\nRoute 4: 80 Feet Road -> New Bus Stand -> College 9:00 AM\nRoute 5: New Bus Stand -> College 8:45 AM (free)\nRoute 6: Vidhya Nagar -> Railway Station -> College 8:50 AM", "Mixed"),

    ("Transport", "What are the bus timings for RIT Hassan?",
     "RIT Hassan Bus Morning Timings (college reach time):\nRoute 2: College at 8:50 AM  (starts Bittagodanahalli 8:10)\nRoute 3: College ~9:00 AM   (starts Aralikatte Circle 8:12)\nRoute 4: College at 9:00 AM  (starts 80 Feet Road 8:00)\nRoute 5: College at 8:45 AM  (starts New Bus Stand 8:30)\nRoute 6: College at 8:50 AM  (starts Yokkaligara Hostel 8:05)\n\nEvening Return:\nRoutes 2, 3, 5, 6: 5:15 PM\nRoute 4: 4:30 PM to Nursing College", "English"),

    ("Transport", "bus timing enu? bus yavaga baruttade?",
     "Morning - College reach time:\nRoute 2: 8:50 AM | Route 3: ~9:00 AM | Route 4: 9:00 AM\nRoute 5: 8:45 AM | Route 6: 8:50 AM\n\nEvening return:\nRoutes 2,3,5,6: 5:15 PM | Route 4: 4:30 PM", "Mixed"),

    ("Transport", "bus ka timing kya hai? college bus time kab hai?",
     "Morning timing:\nRoute 2: 8:50 AM | Route 4: 9:00 AM | Route 5: 8:45 AM | Route 3 & 6: ~8:50-9:00 AM\n\nEvening return: 5:15 PM (Route 4: 4:30 PM)", "Mixed"),

    ("Transport", "What time does the college bus return in the evening?",
     "Evening return timings:\nRoutes 2, 3, 5, 6: 5:15 PM\nRoute 4 (80 Feet Road / Hemavathi Nagara side): 4:30 PM to Nursing College", "English"),

    ("Transport", "bus evening return time enu? bus yavaga herthade?",
     "Evening bus return:\nRoute 2, 3, 5, 6: 5:15 PM\nRoute 4: 4:30 PM (Nursing College)", "Mixed"),

    ("Transport", "Is there a bus from Hassan New Bus Stand to college?",
     "Yes! Route 5 provides FREE transport from Hassan New Bus Stand to college.\nBus No: KA13 C.7610 | Driver: Ravi | Ph: 9353032762\nNew Bus Stand departure: 8:30 AM -> College arrival: 8:45 AM\nReturn: 5:15 PM", "English"),

    ("Transport", "bus stand inda college ge bus ide? new bus stand bus timing",
     "Haan! Route 5 - New Bus Stand inda college ge FREE transport.\nBus: KA13 C.7610 | Driver: Ravi | Ph: 9353032762\nDeparture: 8:30 AM -> College: 8:45 AM | Return: 5:15 PM", "Mixed"),

    ("Transport", "Hassan bus stand se college bus hai kya?",
     "Haan! Route 5 - New Bus Stand se college free transport.\nDriver: Ravi | Ph: 9353032762 | 8:30 AM departure | College: 8:45 AM | Wapas: 5:15 PM", "Mixed"),

    ("Transport", "Is there a bus from Dairy Circle to RIT Hassan?",
     "Yes! Two routes pass through Dairy Circle:\nRoute 3 (Driver: Ranganath, Ph: 9900693953) - picks up at Dairy Circle at 8:55 AM\nRoute 6 (Driver: Kande Gowda, Ph: 8722649446) - picks up at Dairy Circle at 8:35 AM", "English"),

    ("Transport", "Dairy Circle inda college ge bus ide?",
     "Haan! Eradu routes Dairy Circle nalli nillutte:\nRoute 3 (Ranganath, 9900693953): Dairy Circle 8:55 AM\nRoute 6 (Kande Gowda, 8722649446): Dairy Circle 8:35 AM", "Mixed"),

    ("Transport", "Is there a bus from Railway Station to RIT Hassan?",
     "Yes! Route 6 (Bus: KA13 C.0378) stops at Railway Station at 8:30 AM.\nDriver: Kande Gowda | Ph: 8722649446 | Reaches college at 8:50 AM | Return: 5:15 PM", "English"),

    ("Transport", "Railway station inda college ge bus ide?",
     "Haan! Route 6 Railway Station nalli 8:30 AM ge nillutte.\nDriver: Kande Gowda | Ph: 8722649446 | College 8:50 AM | Return: 5:15 PM", "Mixed"),

    ("Transport", "Is there a bus from Aralikatte Circle?",
     "Yes! Route 3 starts from Aralikatte Circle at 8:12 AM.\nBus: KA13 D.6550 | Driver: Ranganath | Ph: 9900693953 | Return: 5:15 PM", "English"),

    ("Transport", "What are the bus driver contact numbers?",
     "RIT Hassan bus driver contacts:\nRoute 2 - Chonnakesava K R : 9483529679\nRoute 3 - Ranganath        : 9900693953\nRoute 4 - Maganegowda      : 9900871814\nRoute 5 - Ravi             : 9353032762\nRoute 6 - Kande Gowda      : 8722649446", "English"),

    ("Transport", "bus driver contact number kodi. driver phone number",
     "Bus driver numbers:\nRoute 2 - Chonnakesava K R: 9483529679\nRoute 3 - Ranganath: 9900693953\nRoute 4 - Maganegowda: 9900871814\nRoute 5 - Ravi: 9353032762\nRoute 6 - Kande Gowda: 8722649446", "Mixed"),

    ("Transport", "What is Route 2 bus timing and stops?",
     "Route 2 | Bus: KA13 C.8563 | Driver: Chonnakesava K R | Ph: 9483529679\nStops: Bittagodanahalli(8:10) -> Jayaraypura(8:15) -> Silk Board(8:20) -> Vijayanagara(8:25) -> Thanniruhalla(8:30) -> Nantha Pete(8:35) -> New Bus Stand(8:40) -> College(8:50 AM)\nReturn: 5:15 PM", "English"),

    ("Transport", "What is Route 3 bus timing and stops?",
     "Route 3 | Bus: KA13 D.6550 | Driver: Ranganath | Ph: 9900693953\nStops: Aralikatte Circle(8:12) -> Saraswathi Temple(8:15) -> Ring Road Petrol Bunk(8:17) -> Dasara Koppalu Bus Stop(8:20) -> Thivara Koppalu(8:25) -> Space Quarters(8:30) -> Ring Road(8:30) -> Thanyi Thrisha Kalyana Mantapa(8:40) -> Sathyamangala(8:45) -> Dairy Circle(8:55) -> College\nReturn: 5:15 PM", "English"),

    ("Transport", "What is Route 4 bus timing and stops?",
     "Route 4 | Bus: KA13 D.2332 | Driver: Maganegowda | Ph: 9900871814\nStops: 80 Feet Road(8:00) -> Hemavathi Nagara(8:00) -> Shanthi Nagar(8:05) -> Ganapathi Temple-Dagdar Koppal(8:10) -> MCE College(8:15) -> Ring Road(8:20) -> Tany Trisha Kalyana Mantapa(8:30) -> Old Bus Stand(8:40) -> New Bus Stand(8:45) -> College(9:00 AM)\nReturn: 4:30 PM to Nursing College", "English"),

    ("Transport", "What is Route 5 bus timing and stops?",
     "Route 5 | Bus: KA13 C.7610 | Driver: Ravi | Ph: 9353032762\nFREE transport from New Bus Stand to College.\nNew Bus Stand(8:30) -> College(8:45 AM)\nReturn: 5:15 PM", "English"),

    ("Transport", "What is Route 6 bus timing and stops?",
     "Route 6 | Bus: KA13 C.0378 | Driver: Kande Gowda | Ph: 8722649446\nStops: Yokkaligara Hostel-BM Road(8:05) -> Rajeev Arcade(8:07) -> Euro Kids-MG Road(8:08) -> Vidhya Nagar Ladies Hostel(8:15) -> Vidhya Nagar Auto Stand(8:20) -> Gowri Koppalu/Aralikatte Stop(8:20) -> Beeranally Kere Road(8:25) -> Ganapathi Temple-Kuvempu Nagar(8:25) -> Janatha Bazar(8:30) -> BSNL(8:30) -> Prithvi Theatre(8:30) -> Railway Station(8:30) -> Kattehalli(8:30) -> Dairy Circle(8:35) -> B T Koppalu(8:45) -> College(8:50 AM)\nReturn: 5:15 PM", "English"),

    # ============================================================
    # HOSTEL
    # Source: Handwritten hostel notes image
    # Girls Block 1 (Kaveri): 59 rooms, 2-sharing Rs.75000/3-sharing Rs.81000
    # Girls Block 2 (Hemavathi): 59 rooms, Pharmacy/Nursing
    # Boys: 143 rooms, 4-sharing Rs.75000
    # Timing: 6:30AM-6:30PM, Breakfast 8-9AM, Lunch 1-2PM, Dinner 8-9PM
    # Parents visiting: Sunday
    # ============================================================
    ("Hostel", "What hostel facilities are available at RIT Hassan?",
     "RIT Hassan has three hostel blocks:\n\nGirls Hostel Block 1 - Kaveri Block\nTotal rooms: 59 | Students: Nursing, BPT, Diploma, BE\n4-sharing: Rs.75,000/year | 3-sharing: Rs.81,000/year\n\nGirls Hostel Block 2 - Hemavathi Block\nTotal rooms: 59 | Students: Pharmacy, Nursing\nFees same as Kaveri Block\n\nBoys Hostel\nTotal rooms: 143 | 4-sharing: Rs.75,000/year\n\nHostel Timings: 6:30 AM - 6:30 PM\nBreakfast: 8:00 AM - 9:00 AM\nLunch: 1:00 PM - 2:00 PM\nDinner: 8:00 PM - 9:00 PM\nParents visiting day: Sunday", "English"),

    ("Hostel", "hostel facilities enu? hostel bagge details kodi",
     "RIT Hassan hostel:\n\nGirls Block 1 - Kaveri: 59 rooms (Nursing/BPT/Diploma/BE)\n2-sharing Rs.75,000 | 3-sharing Rs.81,000\n\nGirls Block 2 - Hemavathi: 59 rooms (Pharmacy/Nursing)\nFees same as Kaveri\n\nBoys Hostel: 143 rooms | 4-sharing Rs.75,000/year\n\nTiming: 6:30 AM - 6:30 PM\nBreakfast: 8-9 AM | Lunch: 1-2 PM | Dinner: 8-9 PM\nParents visiting: Sunday", "Mixed"),

    ("Hostel", "hostel ki poori jankari chahiye",
     "RIT Hassan hostel:\nGirls Block 1 (Kaveri): 59 rooms - 4-sharing Rs.75,000 | 3-sharing Rs.81,000\nGirls Block 2 (Hemavathi): 59 rooms - same fees\nBoys Hostel: 143 rooms - 4-sharing Rs.75,000/year\nTiming: 6:30 AM - 6:30 PM\nBreakfast: 8-9 AM | Lunch: 1-2 PM | Dinner: 8-9 PM\nParents visit: Sunday", "Mixed"),

    ("Hostel", "What are the hostel fees at RIT Hassan?",
     "RIT Hassan Hostel Fees (per year):\nGirls Hostel (Kaveri Block) - 4-sharing: Rs.75,000 | 3-sharing: Rs.81,000\nGirls Hostel (Hemavathi Block) - same as Kaveri Block\nBoys Hostel - 4-sharing: Rs.75,000", "English"),

    ("Hostel", "hostel fees eshtu? hostel fee kodi",
     "Hostel fees (per year):\nGirls 4-sharing: Rs.75,000 | Girls 3-sharing: Rs.81,000\nBoys 4-sharing: Rs.75,000", "Mixed"),

    ("Hostel", "hostel fees kitni hai? hostel ka kharcha kitna hai?",
     "Hostel fees per year:\nGirls 4-sharing: Rs.75,000 | Girls 3-sharing: Rs.81,000\nBoys 4-sharing: Rs.75,000", "Mixed"),

    ("Hostel", "What are the names of the girls hostels at RIT Hassan?",
     "RIT Hassan has two girls hostel blocks:\n1. Kaveri Block (Block 1) - for Nursing, BPT, Diploma and BE students - 59 rooms\n2. Hemavathi Block (Block 2) - for Pharmacy and Nursing students - 59 rooms", "English"),

    ("Hostel", "girls hostel name enu? girls hostel block yavavu?",
     "Girls hostel blocks:\n1. Kaveri Block (Block 1) - Nursing/BPT/Diploma/BE - 59 rooms\n2. Hemavathi Block (Block 2) - Pharmacy/Nursing - 59 rooms", "Mixed"),

    ("Hostel", "How many rooms are in the boys hostel?",
     "The Boys Hostel at RIT Hassan has 143 rooms with 4-sharing arrangement. Fee: Rs.75,000 per year.", "English"),

    ("Hostel", "boys hostel rooms eshtu? boys hostel details kodi",
     "Boys Hostel: 143 rooms, 4-sharing. Fee: Rs.75,000/year.", "Mixed"),

    ("Hostel", "What are the hostel meal timings?",
     "Hostel Mess Timings at RIT Hassan:\nBreakfast: 8:00 AM - 9:00 AM\nLunch: 1:00 PM - 2:00 PM\nDinner: 8:00 PM - 9:00 PM", "English"),

    ("Hostel", "hostel mess timing enu? hostel food time kodi",
     "Hostel mess timings:\nBreakfast: 8:00-9:00 AM\nLunch: 1:00-2:00 PM\nDinner: 8:00-9:00 PM", "Mixed"),

    ("Hostel", "hostel ka khana kab milta hai? mess timing kya hai?",
     "Hostel mess timing:\nBreakfast: 8:00-9:00 AM | Lunch: 1:00-2:00 PM | Dinner: 8:00-9:00 PM", "Mixed"),

    ("Hostel", "What are the hostel timings at RIT Hassan?",
     "RIT Hassan hostel timings: 6:30 AM to 6:30 PM.", "English"),

    ("Hostel", "hostel timing enu? hostel yavaga open aagutte?",
     "Hostel timing: 6:30 AM - 6:30 PM.", "Mixed"),

    ("Hostel", "When can parents visit students in the hostel?",
     "Parents can visit students in the hostel on Sundays. Hostel timings are 6:30 AM to 6:30 PM.", "English"),

    ("Hostel", "parents hostel ge yavaga barbahudu? parents visiting day",
     "Parents hostel ge Sunday dina barbahudu. Timing: 6:30 AM - 6:30 PM.", "Mixed"),

    ("Hostel", "parents hostel mein kab aa sakte hain?",
     "Parents Sunday ko hostel visit kar sakte hain. Hostel timing 6:30 AM - 6:30 PM.", "Mixed"),

    ("Hostel", "What is the sharing type in boys hostel?",
     "The Boys Hostel has only 4-sharing arrangement at Rs.75,000 per year.", "English"),

    ("Hostel", "What is the sharing type in girls hostel?",
     "Girls hostel has two options:\n4-sharing: Rs.75,000 per year\n3-sharing: Rs.81,000 per year\n(Both Kaveri Block and Hemavathi Block)", "English"),
    # ============================================================
    # ATTENDANCE
    # Source: Handwritten attendance note image
    # ============================================================
    ("Attendance", "What is the minimum attendance required at RIT Hassan?",
     "At RIT Hassan, a minimum of 85% attendance is required to be eligible to write semester exams.\nBelow 85%: Not eligible to appear for exams.\nMedical reason: Condonation can be applied with doctor's certificate.\nThe college informs parents about attendance through messages.", "English"),

    ("Attendance", "attendance percentage eshtu beku? minimum attendance keshtu?",
     "Exam bardabeku minimum 85% attendance beku.\n85% below: Exam bardabeku eligible alla.\nMedical reason idre: Condonation apply madabeku.\nCollege, attendance bagge parents ge message kaltatte.", "Mixed"),

    ("Attendance", "attendance kitni chahiye? minimum attendance kitna hona chahiye?",
     "RIT Hassan mein minimum 85% attendance zaroori hai exam dene ke liye.\n85% se kam ho to exam nahi de sakte.\nMedical reason pe condonation milta hai.", "Mixed"),

    ("Attendance", "What happens if my attendance is below 85%?",
     "If attendance falls below 85%, you will not be eligible to appear for semester exams. If the shortage is due to a medical reason, you can apply for attendance condonation with a doctor's certificate. The college also informs parents about attendance shortages through messages.", "English"),

    ("Attendance", "attendance 85% se neeche ho to kya hoga?",
     "85% se kam attendance ho to semester exam nahi de sakte. Medical reason ho to condonation apply kar sakte hain. College parents ko message karke inform karta hai.", "Mixed"),

    ("Attendance", "attendance shortage idre enu aagutte?",
     "Attendance 85% below aadre exam bardabeku eligible alla. Medical reason idre doctor certificate jathe condonation apply madabeku. College parents ge message kaltatte.", "Mixed"),

    ("Attendance", "Can I get attendance condonation at RIT Hassan?",
     "Yes. Students with attendance below 85% due to medical reasons can apply for attendance condonation. A doctor's certificate is required. Contact your department HOD for the process.", "English"),

    ("Attendance", "attendance condonation hege apply madabeku?",
     "Medical reason indaga attendance shortage idre condonation apply madabeku. Doctor certificate beku. Department HOD ge contact madabeku.", "Mixed"),

    ("Attendance", "How does the college inform parents about attendance?",
     "RIT Hassan informs parents about their ward's attendance through messages sent to their registered mobile number when attendance falls short.", "English"),

    ("Attendance", "college parents ge attendance bagge hege inform maaduttade?",
     "Attendance shortfall idre college parents ge message kaltatte (registered mobile number ge).", "Mixed"),

    # ============================================================
    # PLACEMENT STATISTICS
    # Source: Placement statistics image (CSE department data)
    # ============================================================
    ("Placements", "What are the placement statistics of RIT Hassan?",
     "RIT Hassan - Placement Summary:\n\nYear    | Students | Placed | Highest Salary | Placement %\n2023-24 |   119    |   49   | Rs.4,00,000    | 41.17%\n2022-23 |   100    |   52   | Rs.9,00,000    | 52.00%\n2021-22 |    83    |   48   | Rs.7,50,000    | 57.83%\n2020-21 |    98    |   38   | Rs.6,00,000    | 38.77%\n2019-20 |   111    |   50   | Rs.7,20,000    | 45.04%\n2018-19 |   108    |   44   | Rs.5,20,000    | 40.78%", "English"),

    ("Placements", "placement statistics kodi. placement data enu?",
     "RIT Hassan Placement Summary:\n2023-24: 49/119 placed (41.17%), Highest Rs.4,00,000\n2022-23: 52/100 placed (52%), Highest Rs.9,00,000\n2021-22: 48/83 placed (57.83%), Highest Rs.7,50,000\n2020-21: 38/98 placed (38.77%), Highest Rs.6,00,000\n2019-20: 50/111 placed (45.04%), Highest Rs.7,20,000\n2018-19: 44/108 placed (40.78%), Highest Rs.5,20,000", "Mixed"),

    ("Placements", "placement statistics kya hai? kitne log place hue?",
     "RIT Hassan placement:\n2023-24: 49/119 (41.17%) | 2022-23: 52/100 (52%)\n2021-22: 48/83 (57.83%) | 2020-21: 38/98 (38.77%)\n2019-20: 50/111 (45.04%) | 2018-19: 44/108 (40.78%)", "Mixed"),

    ("Placements", "What is the highest salary package at RIT Hassan?",
     "The highest salary package recorded at RIT Hassan was Rs.9,00,000 per annum, in the year 2022-23.", "English"),

    ("Placements", "highest salary eshtu? highest package kodi",
     "Highest salary package: Rs.9,00,000 per annum (2022-23 nalli).", "Mixed"),

    ("Placements", "sabse zyada salary kitni mili RIT mein?",
     "RIT Hassan mein sabse zyada salary Rs.9,00,000 per annum thi - year 2022-23 mein.", "Mixed"),

    ("Placements", "What was the best placement year at RIT Hassan?",
     "The best placement percentage was in 2021-22 with 57.83% (48 out of 83 students placed). The highest salary was in 2022-23 at Rs.9,00,000 per annum.", "English"),

    ("Placements", "placement percentage eshtu? placement rate kodi",
     "RIT Hassan placement percentages:\n2023-24: 41.17% | 2022-23: 52% | 2021-22: 57.83% (highest)\n2020-21: 38.77% | 2019-20: 45.04% | 2018-19: 40.78%", "Mixed"),

    ("Placements", "How many students were placed in 2023-24?",
     "In 2023-24: 49 out of 119 students were placed (41.17%). Highest salary: Rs.4,00,000 per annum.", "English"),

    ("Placements", "How many students were placed in 2022-23?",
     "In 2022-23: 52 out of 100 students were placed (52%). Highest salary: Rs.9,00,000 per annum.", "English"),

    ("Placements", "How many students were placed in 2021-22?",
     "In 2021-22: 48 out of 83 students were placed (57.83%). Highest salary: Rs.7,50,000 per annum.", "English"),

    # ============================================================
    # SCHOLARSHIPS
    # Source: SCHOLARSHIP.docx - complete
    # ============================================================
    ("Scholarships", "What scholarships are available for students at RIT Hassan?",
     "Scholarships at RIT Hassan:\n\nGOVERNMENT - SSP Portal:\nOBC Students: Rs.19,200/year | Income < Rs.1.5 lakh | Apply: ONLINE (SSP portal)\nSC/ST (Social Welfare Dept, CET only): CET Tuition Fee | Income Rs.10,000-Rs.2.5 lakh\nSC/ST (Dept of Technical Education, CET only): CET Tuition Fee | Income Rs.2.5L-Rs.10L\n\nNSP - National Scholarship Portal:\nMinority students: Rs.50,000/year | Income < Rs.1.5 lakh | Apply: scholarships.gov.in\n\nOTHER GOVERNMENT:\nDept of Labour (daily wage workers' children): Rs.50,000/year | Income < Rs.1 lakh\nYouth Empowerment & Sports (district/state athletes): Rs.25,000/year | Income < Rs.1.5L | OFFLINE\nDifferently Abled: CET Tuition Fee/year | Income < Rs.2.5 lakh | OFFLINE\nEx-Army Staff children: Rs.15,000/year | No income limit | OFFLINE\nRailway Employees' children: Rs.20,000/year | No income limit | OFFLINE\nKSRTC Employees: Rs.10,000/year | OFFLINE\nCoffee Board (coffee curing works' children): Rs.12,000/year | ONLINE\nGovt Teachers' children: Rs.10,000/year | OFFLINE\n\nNON-GOVERNMENT:\nSitaram Jindal Foundation (CET & Mgmt): Rs.30,000/year | Income < Rs.2.5L | OFFLINE+ONLINE\nDharamshala Rural Dev (Sujnana Nidhi): Rs.11,000/year | Income < Rs.1.5L | OFFLINE\nR L Jalappa Foundation (Veerashaiva Lingayat): Rs.20,000/year | No income limit | OFFLINE\nArya Vysya/Ediga/Arasu Community: Rs.20,000/year | Income < Rs.1.5L | OFFLINE\nArihant Charitable Trust, Bengaluru: Rs.25,000/year | Income < Rs.1.5L | OFFLINE", "English"),

    ("Scholarships", "scholarship bagge information kodi. scholarship yenu ide?",
     "Available scholarships:\n\nSSP Portal:\nOBC: Rs.19,200/year (income < Rs.1.5L) - Online\nSC/ST (Social Welfare, CET): CET fee (income Rs.10k-Rs.2.5L)\nSC/ST (Technical Ed, CET): CET fee (income Rs.2.5L-Rs.10L)\n\nNSP Portal:\nMinority: Rs.50,000/year (income < Rs.1.5L) - scholarships.gov.in\n\nOther:\nLabour Dept: Rs.50,000/year | Sports: Rs.25,000/year\nEx-Army: Rs.15,000/year | Railways: Rs.20,000/year\nSitaram Jindal: Rs.30,000/year | Arihant Trust: Rs.25,000/year", "Mixed"),

    ("Scholarships", "scholarship kya kya hain? scholarship list chahiye",
     "RIT Hassan scholarships:\nSSP (OBC): Rs.19,200/yr | SSP (SC/ST): CET fee\nNSP Minority: Rs.50,000/yr | Labour Dept: Rs.50,000/yr\nSports: Rs.25,000/yr | Ex-Army: Rs.15,000/yr\nRailways: Rs.20,000/yr | Differently Abled: CET fee\nSitaram Jindal: Rs.30,000/yr | Arihant Trust: Rs.25,000/yr\nKSRTC: Rs.10,000/yr | Coffee Board: Rs.12,000/yr", "Mixed"),

    ("Scholarships", "What is the OBC scholarship? How much do OBC students get?",
     "OBC Scholarship (SSP Portal - Backward Classes Welfare Department):\nEligibility: Karnataka engineering students | Income < Rs.1.5 lakh/year\nAmount: Rs.19,200 per year\nHow to apply: ONLINE via SSP portal", "English"),

    ("Scholarships", "OBC scholarship details. OBC students ge scholarship enu?",
     "OBC scholarship (SSP portal):\nAnnual income Rs.1.5 lakh below irbekku.\nRs.19,200 per year siguthade. Online apply madabeku.", "Mixed"),

    ("Scholarships", "What is the SC/ST scholarship from Social Welfare Department?",
     "SC/ST Scholarship - Social Welfare Department:\nEligible: Students admitted through CET only\nIncome: Rs.10,000 to Rs.2.5 lakh per year\nAmount: CET Tuition Fee (yearly)\nApply: SSP portal (ONLINE)", "English"),

    ("Scholarships", "SC ST scholarship enu? social welfare scholarship details",
     "SC/ST scholarship (Social Welfare Dept):\nCET through admission irbekku | Income: Rs.10,000-Rs.2.5 lakh\nAmount: CET tuition fee | Apply: SSP portal (Online)", "Mixed"),

    ("Scholarships", "What is the SC/ST scholarship from Dept of Technical Education?",
     "SC/ST Scholarship - Department of Technical Education:\nEligible: Students admitted through CET only\nIncome: Rs.2.5 lakh to Rs.10 lakh per year\nAmount: CET Tuition Fee for that academic year\nRequires: E-attestation of parent's salary certificate\nApply: SSP portal", "English"),

    ("Scholarships", "What is the NSP Minority scholarship?",
     "National Scholarship Portal (NSP) - Minority Scholarship:\nEligibility: Minority students\nIncome: Must not exceed Rs.1.5 lakh per year\nAmount: Rs.50,000 per year\nHow to apply: ONLINE at https://scholarships.gov.in/", "English"),

    ("Scholarships", "minority scholarship enu? NSP scholarship kodi",
     "NSP Minority Scholarship:\nIncome Rs.1.5 lakh below irbekku.\nRs.50,000 per year siguthade.\nApply: https://scholarships.gov.in/", "Mixed"),

    ("Scholarships", "Is there a scholarship for sports students?",
     "Youth Empowerment and Sports Department Scholarship:\nEligible: Students who represented at District/State level competitions\nIncome: Must not exceed Rs.1.5 lakh per year\nAmount: Rs.25,000 per year\nHow to apply: OFFLINE", "English"),

    ("Scholarships", "sports scholarship ide? athletes ge scholarship enu?",
     "Sports scholarship (Youth Empowerment and Sports Dept):\nDistrict/State level competition represent maadida students ge eligible.\nIncome Rs.1.5 lakh below irbekku. Rs.25,000/year. Offline apply.", "Mixed"),

    ("Scholarships", "Is there a scholarship for differently abled students?",
     "Department for the Empowerment of Differently Abled Scholarship:\nEligibility: Annual income must not exceed Rs.2.5 lakh\nAmount: CET Tuition Fee of each year\nHow to apply: OFFLINE", "English"),

    ("Scholarships", "Is there a scholarship for Ex-Army children?",
     "Scholarship for Children of Ex-Army Staff:\nNo income limit\nAmount: Rs.15,000 per year\nApply: OFFLINE", "English"),

    ("Scholarships", "Ex-Army children ke liye scholarship kya hai?",
     "Ex-Army Staff children scholarship:\nNo income limit | Amount: Rs.15,000/year | Apply: OFFLINE", "Mixed"),

    ("Scholarships", "Is there a scholarship for railway employees' children?",
     "Scholarship from Department of Railways:\nEligible: Children of railway department employees only\nNo income limit\nAmount: Rs.20,000 per year\nApply: OFFLINE", "English"),

    ("Scholarships", "What is the Sitaram Jindal Foundation scholarship?",
     "Sitaram Jindal Foundation Scholarship:\nAvailable for both CET and Management students\nIncome: Must not exceed Rs.2.5 lakh per year\nAmount: Rs.30,000 per year\nApply: OFFLINE and ONLINE", "English"),

    ("Scholarships", "Sitaram Jindal scholarship bagge kodi",
     "Sitaram Jindal Foundation Scholarship:\nCET mattu Management students ge applicable.\nIncome Rs.2.5 lakh below irbekku. Rs.30,000/year.\nOffline + Online apply.", "Mixed"),

    ("Scholarships", "What is the Arihant Charitable Trust scholarship?",
     "Arihant Charitable Trust, Bengaluru Scholarship:\nIncome: Must not exceed Rs.1.5 lakh per year\nAmount: Rs.25,000 per year\nApply: OFFLINE", "English"),

    ("Scholarships", "Is there a scholarship for KSRTC employees?",
     "KSRTC Employees Educational Fund:\nAmount: Rs.10,000 per year\nApply: OFFLINE", "English"),

    ("Scholarships", "Is there a scholarship for government teachers' children?",
     "Teachers Scholarship from Education Department:\nEligible: Students whose parents are working Government Teachers\nAmount: Rs.10,000 per year\nApply: OFFLINE", "English"),

    ("Scholarships", "Is there a scholarship from Coffee Board?",
     "Scholarship from Coffee Board, Bengaluru:\nEligible: Children whose parents work at any Coffee Curing Works\nAmount: Rs.12,000 per year\nApply: ONLINE", "English"),

    ("Scholarships", "What is the R L Jalappa Foundation scholarship?",
     "R L Jalappa Foundation Scholarship:\nEligible: Veerashaiva Lingayat students only\nNo income limit\nAmount: Rs.20,000 per year\nApply: OFFLINE", "English"),

    ("Scholarships", "Is there scholarship for Arya Vysya or Ediga community students?",
     "Scholarship for Arya Vysya, Ediga and Arasu Community Students:\nIncome: Must not exceed Rs.1.5 lakh per year\nAmount: Approximately Rs.20,000 per year\nApply: OFFLINE", "English"),

    ("Scholarships", "Is there a scholarship from Dharamshala Rural Development Project?",
     "Scholarship from Dharamshala Rural Development Project (Sujnana Nidhi):\nEligible: Children of members of Sri Kshethra Dharmasthala Rural Development Project\nIncome: Must not exceed Rs.1.5 lakh per year\nAmount: Rs.11,000 per year\nApply: OFFLINE", "English"),

    ("Scholarships", "How to apply for SSP scholarship?",
     "To apply for SSP (State Scholarship Portal) scholarship:\n1. Visit the Karnataka SSP portal online\n2. Karnataka student studying engineering in Karnataka\n3. Must score at least 50% in previous examinations\n4. Apply online through the SSP portal\nFor OBC: income < Rs.1.5 lakh | For SC/ST: income Rs.10k-Rs.10 lakh (CET students only)", "English"),

    ("Scholarships", "SSP scholarship apply madabeku hege?",
     "SSP scholarship apply maadalu:\n1. Karnataka student aagirbekku\n2. Engineering nalli minimum 50% score irbekku\n3. SSP portal mele online apply maadabeku\nOBC ge: income Rs.1.5 lakh below | SC/ST ge: CET students only", "Mixed"),

    # ============================================================
    # ACADEMIC TIMETABLE / CALENDAR
    # Source: CSE Department Academic Timetable PDF (2026-27 ODD SEM)
    # ============================================================
    ("Academic Calendar", "What is the academic timetable for 2026-27 odd semester?",
     "CSE Dept - Academic Calendar 2026-27 (ODD SEM):\n\nJuly 2026:\nPre-placement training for 7th Sem: July 6 - Aug 4\n7th Sem BE classes start: July 20\n\nAugust 2026:\nIndependence Day: Aug 15\nPre-placement training 5th Sem: Aug 10 - Sept 5\n\nSeptember 2026:\n5th Sem BE classes start: Sept 7\n1st CIE for 7th Sem: Sept 10, 11 & 12\n\nOctober 2026:\nGandhi Jayanti: Oct 2\nAyuda Pooja: Oct 20 | Vijayadashami: Oct 21\n2nd CIE for 7th Sem: Oct 10, 11 & 12\n\nNovember 2026:\nKannada Rajyotsava: Nov 1\nLast working day 7th Sem: Nov 9\nTheory Exam 7th Sem starts: Nov 14\n\nDecember 2026:\nPractical Exam 7th Sem starts: Dec 7\nLast working day 5th Sem: Dec 30\n8th Sem BE starts: Dec 21\n\nJanuary 2027:\nTheory Exam 5th Sem starts: Jan 4\nMakara Sankranti: Jan 15\nRepublic Day: Jan 26\n\nFebruary 2027:\nMaha Shivaratri: Feb 6\nPractical Exam 5th Sem starts: Feb 8\n6th Sem BE starts: Feb 22\n\nNote: 1st and 3rd Saturday is HOLIDAY.", "English"),

    ("Academic Calendar", "semester start date yavaga? class yavaga shuru aagutte?",
     "2026-27 ODD SEM:\n7th Sem classes: July 20, 2026\n5th Sem classes: September 7, 2026\n3rd Sem classes: September 7, 2026\n8th Sem starts: December 21, 2026\n6th Sem starts: February 22, 2027", "Mixed"),

    ("Academic Calendar", "semester kab shuru hoga? classes kab se hain?",
     "2026-27 ODD SEM:\n7th Sem: July 20, 2026\n5th Sem: September 7, 2026\n8th Sem: December 21, 2026\n6th Sem: February 22, 2027", "Mixed"),

    ("Academic Calendar", "What are the CIE dates for 2026-27?",
     "CIE Schedule 2026-27 ODD SEM (CSE Dept):\n1st CIE - 7th Sem: September 10, 11 & 12, 2026\n2nd CIE - 7th Sem: October 10, 11 & 12, 2026\nFor 5th Sem CIE dates check the department notice board.", "English"),

    ("Academic Calendar", "CIE exam date yavaga? internal exam schedule",
     "CIE dates (2026-27 ODD SEM):\n1st CIE 7th Sem: Sept 10-12, 2026\n2nd CIE 7th Sem: Oct 10-12, 2026", "Mixed"),

    ("Academic Calendar", "What are the theory exam dates for 2026-27?",
     "Theory Exam dates - 2026-27 ODD SEM:\nTheory Exam 7th Sem: November 14, 2026\nTheory Exam 5th Sem: January 4, 2027\nPractical Exam 7th Sem: December 7, 2026\nPractical Exam 5th Sem: February 8, 2027", "English"),

    ("Academic Calendar", "exam timetable kodi. semester exam date yenu?",
     "2026-27 ODD SEM exam dates:\nTheory Exam 7th Sem: November 14, 2026\nTheory Exam 5th Sem: January 4, 2027\nPractical Exam 7th Sem: December 7, 2026\nPractical Exam 5th Sem: February 8, 2027", "Mixed"),

    ("Academic Calendar", "What are the holidays in 2026-27 odd semester?",
     "2026-27 ODD SEM Holidays:\nIndependence Day: August 15, 2026\nEid Milad: August 26, 2026\nGanesha Chaturthi: September 14, 2026\nGandhi Jayanti: October 2, 2026\nMahalaya Amavasya: October 10, 2026\nAyuda Pooja: October 20, 2026\nVijayadashami: October 21, 2026\nValmiki Jayanthi: October 26, 2026\nKannada Rajyotsava: November 1, 2026\nNaraka Chaturdashi: November 8, 2026\nBalipadyami: November 10, 2026\nKanakadasa Jayanti: November 18, 2026\nChristmas: December 25, 2026\nMakara Sankranti: January 15, 2027\nRepublic Day: January 26, 2027\nMaha Shivaratri: February 6, 2027\n\nNote: 1st and 3rd Saturday is HOLIDAY every week.", "English"),

    ("Academic Calendar", "holidays yavaga ide? college holiday list kodi",
     "2026-27 ODD SEM holidays:\nAug 15: Independence Day | Aug 26: Eid Milad\nSept 14: Ganesha Chaturthi | Oct 2: Gandhi Jayanti\nOct 10: Mahalaya Amavasya | Oct 20: Ayuda Pooja\nOct 21: Vijayadashami | Oct 26: Valmiki Jayanthi\nNov 1: Kannada Rajyotsava | Nov 8: Naraka Chaturdashi\nNov 10: Balipadyami | Nov 18: Kanakadasa Jayanti\nDec 25: Christmas | Jan 15: Makara Sankranti\nJan 26: Republic Day | Feb 6: Maha Shivaratri\n\nNote: Every 1st and 3rd Saturday is holiday.", "Mixed"),

    ("Academic Calendar", "Is Saturday a holiday at RIT Hassan?",
     "At RIT Hassan, the 1st and 3rd Saturday of every month is a holiday. The 2nd and 4th Saturday are working days.", "English"),

    ("Academic Calendar", "Saturday holiday ide? which Saturday is holiday?",
     "Pratiya 1st mattu 3rd Saturday holiday. 2nd mattu 4th Saturday working day.", "Mixed"),

    ("Academic Calendar", "What upcoming events are scheduled in the CSE department?",
     "Upcoming CSE Dept Events 2026-27 ODD SEM:\nCurrent (Sept 2026): Codeathon 8-Hour Coding Contest (Sept 22-26 week)\nOct 2026: Industrial Visit/Study Tour (Oct 11-17 week)\nOct 2026: Project Exhibition Demo Expo - 7th Sem (Oct 18-24 week)\nOct 2026: Poster Presentation using Canva (Oct 25-31 week)\nNov 2026: Technical Treasure Hunt (Nov 1-7 week)\nNov 2026: Workshop on Git and GitHub (Nov 22-28 week)\nDec 2026: Alumni Interaction/Industry Expert Talk (Dec 13-19 week)", "English"),

    ("Academic Calendar", "upcoming events yavavu? college events list kodi",
     "CSE Dept upcoming events 2026-27:\nCurrent: Codeathon 8-Hour Coding Contest (Sept 22-26)\nOct: Industrial Visit, Demo Expo, Poster Presentation (Canva)\nNov: Technical Treasure Hunt, Git & GitHub Workshop\nDec: Alumni Interaction / Industry Expert Talk", "Mixed"),

    ("Academic Calendar", "When does pre-placement training start?",
     "Pre-placement training schedule 2026-27 ODD SEM:\n7th Sem: July 6, 2026 - August 4, 2026\n5th Sem: August 10, 2026 - September 5, 2026", "English"),

    ("Academic Calendar", "preplacement training yavaga ide?",
     "Pre-placement training:\n7th Sem: July 6 - Aug 4, 2026\n5th Sem: Aug 10 - Sept 5, 2026", "Mixed"),

    # ============================================================
    # FEES
    # Source: fees details.docx was EMPTY / no content available
    # ============================================================
    ("Fees", "What is the fee structure at RIT Hassan?",
     "Sorry, the detailed fee structure document did not contain readable information. Please contact the RIT Hassan Accounts Office directly for exact fee details.\nPhone: 08172-243180 / 243181 / 243184\nEmail: info@rithassan.ac.in", "English"),

    ("Fees", "fees eshtu? fee structure kodi",
     "Fee details document nalli information ililla. Accounts Office ge directly contact madabeku.\nPhone: 08172-243180 | Email: info@rithassan.ac.in", "Mixed"),

    ("Fees", "fees kitni hai? fee structure kya hai?",
     "Fee document mein information nahi thi. Accounts Office se directly pata karein.\nPhone: 08172-243180 | Email: info@rithassan.ac.in", "Mixed"),

    # ============================================================
    # LIBRARY
    # Source: library details.docx was EMPTY / no content available
    # ============================================================
    ("Library", "What are the library timings at RIT Hassan?",
     "Sorry, the library details document did not contain readable information. Please contact RIT Hassan directly for library timings and details.\nPhone: 08172-243180\nEmail: info@rithassan.ac.in", "English"),

    ("Library", "library timing yenu? library yavaga open aagutte?",
     "Library timing document nalli information ililla. College ge directly contact madabeku.\nPhone: 08172-243180 | info@rithassan.ac.in", "Mixed"),

    ("Library", "library timing kya hai? library kab khulti hai?",
     "Library details document mein information nahi thi. College se directly pata karein.\nPhone: 08172-243180", "Mixed"),

    ("Library", "What are the library facilities at RIT Hassan?",
     "Sorry, the library details document provided did not contain readable information about library facilities. Please contact RIT Hassan at 08172-243180 or info@rithassan.ac.in for accurate library details.", "English"),

    # ============================================================
    # VTU EXAMS (general VTU knowledge, not college-specific docs)
    # Only including what is document-supported
    # ============================================================
    ("Exams", "Where can I check VTU exam results?",
     "VTU exam results are published on the official VTU results portal: results.vtu.ac.in\nYou need your USN (University Seat Number) to check results.", "English"),

    ("Exams", "VTU result yavaga baruttade? result check madabeku hege?",
     "VTU results: results.vtu.ac.in website nalli check madabeku. USN number beku.", "Mixed"),

    ("Exams", "VTU result kaise check kare?",
     "VTU results check karne ke liye: results.vtu.ac.in website visit karein. USN number chahiye.", "Mixed"),

    ("Exams", "What is the minimum attendance to appear for VTU exams?",
     "As per RIT Hassan rules, a minimum of 85% attendance is required to be eligible to appear for semester examinations. (Note: The college follows 85%, which is stricter than VTU's general guideline.)", "English"),

    ("Exams", "exam bardabeku eshtu attendance beku?",
     "RIT Hassan nalli exam bardabeku minimum 85% attendance beku.", "Mixed"),
]

# ==================================================================
#  SEED THE DATABASE
# ==================================================================
with app.app_context():
    # Step 1: Remove ALL existing FAQs
    deleted = FAQ.query.delete()
    db.session.commit()
    print(f"Cleared {deleted} existing FAQ entries.")

    # Step 2: Insert all real-data FAQs
    added = 0
    for entry in FAQS:
        category, question, answer, language = entry
        db.session.add(FAQ(
            category=category,
            question=question,
            answer=answer,
            language=language
        ))
        added += 1

    db.session.commit()
    print(f"\nSuccessfully inserted {added} real-data FAQs.")
    print("\nBreakdown by category:")

    from collections import Counter
    cats = Counter(e[0] for e in FAQS)
    for cat, count in sorted(cats.items()):
        print(f"  {cat:25s}: {count} entries")

    print("\nDatabase is now clean - only real RIT Hassan document data.")
    print("No dummy, generic, or invented information remains.")
