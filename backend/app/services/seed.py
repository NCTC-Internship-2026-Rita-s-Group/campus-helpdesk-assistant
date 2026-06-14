from sqlalchemy.orm import Session
from app.models.db_models import NoticeModel
from datetime import datetime

def seed_initial_notices(db: Session):
    # Check if the database already has notices to avoid duplication
    if db.query(NoticeModel).first() is not None:
        return

    sample_notices = [
        {
            "title": "MCA Semester Odd Examinations Fee Extension",
            "description": "The last date to clear all outstanding dues and submit the examination form for the upcoming MCA Semester III examinations has been extended to June 25, 2026, without any late fines.",
            "category": "fee_structure",
            "notice_date": "2026-06-12"
        },
        {
            "title": "Amity Campus Placement Drive 2026 - Wipro Tech",
            "description": "Wipro Technologies will be hosting an on-campus placement drive for final year B.Tech (CSE/ECE) and MCA students on July 05, 2026. Pre-placement talks start at 09:30 AM in the main auditorium. Resumes must be updated on the ERP portal.",
            "category": "placement",
            "notice_date": "2026-06-14"
        },
        {
            "title": "Hostel In-Out Timings Modification Notice",
            "description": "To ensure maximum safety on campus, the strict curfew time for all institutional hostel blocks has been revised to 08:30 PM starting this Monday. Biometric logging is mandatory for entries post-curfew.",
            "category": "hostel_rules",
            "notice_date": "2026-06-10"
        }
    ]

    for notice in sample_notices:
        db_notice = NoticeModel(
            title=notice["title"],
            description=notice["description"],
            category=notice["category"],
            notice_date=notice["notice_date"]
        )
        db.add(db_notice)
    
    db.commit()
    print("----- DATABASE SEEDED SUCCESSFULLY WITH AMITY UNIVERSITY RANCHI DATA -----")