import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.db_models import User, Ticket, Notice

async def seed_system_data(db: AsyncSession) -> bool:
    """
    🌱 Database Seeding Service Core
    Injects foundational records into PostgreSQL to ensure the frontend displays
    rich, populated data states right out of the box.
    """
    try:
        # 1. Check if users are already seeded to prevent duplicate record conflicts
        user_check = await db.execute(select(User).limit(1))
        if user_check.scalar_one_or_none():
            print("ℹ️ Database already contains records. Skipping seed sequence.")
            return False

        print("🚀 Executing enterprise database seed matrix injection...")

        # 2. Seed System Profiles (Hashed Password Placeholders for Local Proto)
        mock_users = [
            User(
                email="student.portal@amity.edu",
                hashed_password="pbkdf2:sha256:600000$mock_student_hash_value",
                name="Prakash Kumar Prajapati",
                role="student",
                is_active=True
            ),
            User(
                email="admin.helpdesk@amity.edu",
                hashed_password="pbkdf2:sha256:600000$mock_admin_hash_value",
                name="Prof. Sharma (Admin)",
                role="admin",
                is_active=True
            )
        ]
        db.add_all(mock_users)

        # 3. Seed Campus Notices (Aligning seamlessly with 2026 timestamps)
        mock_notices = [
            Notice(
                title="End Semester Examination Schedule - Autumn 2026",
                category="Examinations",
                date="June 15, 2026",
                excerpt="The final theory and practical examination timetables for all technical streams have been officially released by the controller of examinations...",
                content="The final theory and practical examination timetables for all B.Tech streams have been officially released by the controller of examinations. Theory exams will commence on July 05, 2026. Students must ensure that all outstanding academic semester fees and library dues are fully cleared to download their digital admit cards from the student portal interface before June 30."
            ),
            Notice(
                title="Mega Campus Placement Drive: Tech Mahindra & Capgemini",
                category="Placements",
                date="June 12, 2026",
                excerpt="All eligible profiles from CSE/IT graduating cohorts are requested to register on the training and placement module before the upcoming deadline...",
                content="The Training & Placement Office (TPO) is hosting a joint mega placement drive for Tech Mahindra and Capgemini starting June 22, 2026. Pre-placement talks will begin at 09:30 AM in the main campus auditorium. Crisp business formal attire, updated digital resumes on a secure drive, and an active GitHub link profile documentation package are strictly mandatory for all candidates."
            ),
            Notice(
                title="Hostel Wi-Fi Network Upgrade & Temporary Downtime",
                category="Facilities",
                date="June 10, 2026",
                excerpt="The campus IT network operations team will be performing a high-speed fiber backbone routing upgrade across Hostel Blocks A, B, and C...",
                content="Please note that the campus IT network operations division will be installing high-speed Wi-Fi 6 access routing nodes across all hostel corridors. Temporary internet disruptions are anticipated between 11:00 PM and 04:00 AM on June 24. For urgent MAC address device bindings, please drop a structural support query directly down to our Helpdesk Chat Assistant."
            )
        ]
        db.add_all(mock_notices)

        # 4. Seed Initial Grievance Incident Matrix Tickets
        mock_tickets = [
            Ticket(
                id="TK-2026-8841",
                subject="Semester Fee Payment Reflection Discrepancy",
                category="Finance & Accounts",
                priority="High",
                status="In Review",
                description="Paid the 6th-semester academic tuition fee via UPI gateway interface. My bank debited the amount successfully and the transaction receipt reports a successful transfer, but the student portal invoice token still reflects an 'Outstanding Balance' warning block.",
                timeline=[
                    {"date": "June 14, 2026 - 10:15 AM", "message": "Ticket filed automatically via Chat Escalation Core."},
                    {"date": "June 15, 2026 - 02:30 PM", "message": "Assigned to Finance Dept Analyst (Accounts Section) for active verification."}
                ],
                created_date="June 14, 2026"
            ),
            Ticket(
                id="TK-2026-7712",
                subject="Backlog Examination Form Registration Error",
                category="Academic Operations",
                priority="Critical",
                status="Open",
                description="Attempting to register for the upcoming supplementary exam for Computer Networks, but the system keeps throwing a structural dependency validation error stating pre-requisite courses are unfulfilled.",
                timeline=[
                    {"date": "June 11, 2026 - 04:45 PM", "message": "Grievance ticket created successfully by student. Awaiting dispatch manager review."}
                ],
                created_date="June 11, 2026"
            )
        ]
        db.add_all(mock_tickets)

        # 5. Flush and Commit all transactions safely to PostgreSQL
        await db.commit()
        print("📥 Database seed tracking arrays committed successfully!")
        return True

    except Exception as e:
        await db.rollback()
        print(f"❌ Critical Error during database seeding sequence: {str(e)}")
        return False