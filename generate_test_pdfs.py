import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

# Definition arrays for document data logs
documents_payload = {
    "academic_prospectus_2026.pdf": [
        "AMITY UNIVERSITY JHARKHAND — OFFICIAL ACADEMIC PROSPECTUS 2026",
        "1. REGULATORY ATTENDANCE MATRIX",
        "All enrolled students across undergraduate and postgraduate divisions must maintain a strict minimum attendance threshold of 75% per individual course block. If a student's attendance drops between 60% and 74%, they are barred from standard examination routing unless an official Medical Waiver Request Form (Form AM-MED-01) is filed with the Academic Registrar within 48 hours of recovery. Any attendance recording below 60% results in an automated systemic course block, requiring a complete course repetition in the subsequent semester cycle.",
        "2. ADVANCED DEGREE SPECIALIZATIONS",
        "The School of Engineering and Technology offers the premium B.Tech in Artificial Intelligence & Security Core degree path. This program requires a total completion ledger of 160 credits across 8 semesters. Key specialized modules include Course Code AI-401: Vector Retrieval Architectures & Neural Embeddings (4 Credits), Course Code SEC-402: Asynchronous Multi-Agent Safety Frameworks (3 Credits), and Course Code RAG-403: Retrieval-Augmented Generation Scaling & Context Ingestion (4 Credits).",
        "3. GRADING & ACCREDITATION STANDARDS",
        "Evaluations are compiled using a 10-point Relative Cumulative Grade Point Average (CGPA) system. A student must achieve an absolute minimum CGPA of 4.5 to clear graduation allocation scripts. Distinction honors are programmatically locked behind a strict 8.5 CGPA gate condition with zero active backlogs or disciplinary compliance marks on record."
    ],
    "hostel_resident_policy_2026.pdf": [
        "AMITY UNIVERSITY JHARKHAND — HOSTEL HOUSING POLICY COVENANT 2026",
        "1. SECURITY CURFEW PROTOCOLS",
        "The external perimeter gates of the hostel blocks lock programmatically at exactly 20:30 hours (8:30 PM) every evening. Late entry requests require an explicit digital pass authorized by the Chief Warden via the Student Smart Portal before 17:00 hours on the date of travel. Unsanctioned breach of curfew triggers a Level 1 systemic violation notice, applying an automated fine of INR 1,500 directly to the student's fee account balance.",
        "2. COMPLIANCE & PROHIBITED INFRASTRUCTURE",
        "To prevent fire hazards and grid load drops, residents are strictly prohibited from installing private appliance infrastructure within dorm rooms. Prohibited items include high-voltage electric kettles (exceeding 800W), portable coil heaters and immersion rods, and individual induction cooktops. Discovery of these utility components during spot checks results in immediate asset seizure and an INR 3,000 environmental health penalty charge.",
        "3. ROOM ALLOCATION & ROOM TRANSFERS",
        "Room assignments are locked for the complete duration of the academic year. Inter-room change requests are only evaluated during the mid-semester window (October 1 to October 15) and require the submission of an Inter-Hostel Transfer Petition (Form HT-ROOM-X), accompanied by a signed mutual clearance agreement from both room occupants and a transaction handling processing fee of INR 500."
    ],
    "mess_nutrition_operations.pdf": [
        "AMITY UNIVERSITY JHARKHAND — CAMPUS DINING REFECTORY OPERATIONS GUIDE",
        "1. SERVICE TIMING LIFECYCLE",
        "The central campus mess hall executes dining operations across four precise daily time window arrays: Breakfast Protocol (07:30 AM to 09:00 AM), Lunch Protocol (12:15 PM to 02:00 PM), High Tea Protocol (05:00 PM to 06:15 PM), and Dinner Protocol (07:45 PM to 09:15 PM). Refectory entry channels lock dynamically 5 minutes before the conclusion of each protocol window to clean and drain food line vectors completely.",
        "2. WEEKLY DIETARY MENU REVOLUTION CYCLE",
        "The catering board maintains a fixed dietary menu cycle. Notable premium rotation parameters include every Wednesday evening: Special Paneer Butter Masala served with baseline Jeera Rice; every Friday afternoon: Traditional South Indian Masala Dosa accompanied by Sambhar; every Sunday evening: Premium Multi-Course Feast incorporating Special Chicken Biryani or Kadhai Mushroom for vegetarian preferences.",
        "3. HYGIENE AUDITS & COMPLIANCE ESCALATIONS",
        "The Mess Quality Committee reviews food line hygiene matrices weekly. Students can report catering issues or foreign body contaminants directly to the Food Safety Inspector by scanning the QR codes located on the dining tables or calling the helpline at extension line +91-651-2244. Official support tickets are raiseable on the Student Hub dashboard under the category 'Catering Quality Escalation'."
    ]
}

def build_pdf_document(filename, text_lines):
    # Setup clean margins and canvas template boundaries
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    # Premium Typography Styles
    title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=HexColor('#0f172a'), spaceAfter=20)
    heading_style = ParagraphStyle('SectionHeading', fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=HexColor('#b45309'), spaceBefore=14, spaceAfter=8)
    body_style = ParagraphStyle('BodyTextCustom', fontName='Helvetica', fontSize=10.5, leading=16, textColor=HexColor('#334155'), spaceAfter=12)
    
    story = []
    
    # Title Element append
    story.append(Paragraph(text_lines[0], title_style))
    story.append(Spacer(1, 10))
    
    # Construct paragraph tree elements iteratively
    for line in text_lines[1:]:
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            story.append(Paragraph(line, heading_style))
        else:
            story.append(Paragraph(line, body_style))
            
    doc.build(story)
    print(f"🚀 [SUCCESS] Generated high-density PDF artifact: '{filename}'")

if __name__ == "__main__":
    print("🏗️ Initializing production-grade PDF synthesis process...")
    for filename, lines in documents_payload.items():
        build_pdf_document(filename, lines)
    print("🌟 All test document artifacts generated. Ready for RAG pipeline ingestion!")