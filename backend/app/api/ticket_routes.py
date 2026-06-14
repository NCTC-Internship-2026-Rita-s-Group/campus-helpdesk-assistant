from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import APIResponse, TicketCreate, TicketResponse
from app.services.database_services import DBService
from typing import List

router = APIRouter()

@router.post("/", response_model=APIResponse[TicketResponse], status_code=status.HTTP_201_CREATED)
def lodge_student_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    """
    Lodge a formal grievance/helpdesk support ticket.
    """
    try:
        new_ticket = DBService.create_ticket(db, ticket_data=ticket_in)
        return APIResponse(
            success=True,
            message="Your grievance ticket has been registered successfully.",
            data=new_ticket
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register ticket due to system error: {str(e)}"
        )

@router.get("/", response_model=APIResponse[List[TicketResponse]])
def view_all_tickets(db: Session = Depends(get_db)):
    """
    Retrieve all registered tickets (Admin/Helpdesk staff capability).
    """
    tickets = DBService.get_all_tickets(db)
    return APIResponse(
        success=True,
        message="All grievance tickets retrieved successfully.",
        data=tickets
    )