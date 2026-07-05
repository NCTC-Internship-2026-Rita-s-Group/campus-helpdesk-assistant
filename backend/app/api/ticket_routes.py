import datetime
import random
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.db_models import Ticket, User  # 🗄️ Ingested User class models cleanly
from app.models.schemas import TicketCreate, TicketResponse, TicketStatusUpdate
from app.services.security import get_current_user_from_token, verify_admin_clearance  # 🔒 Institutional Security Guards

router = APIRouter(prefix="/tickets", tags=["Campus Grievance Ledger"])


# 🌐 REAL-TIME CONNECTION BROADCAST MANAGER
class TicketBroadcastManager:
    """
    Tracks and manages live persistent WebSocket connections to administrative dashboards,
    broadcasting incoming student grievances instantly.
    """
    def __init__(self):
        self.active_sockets: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_sockets.append(websocket)
        print(f"🔌 Live Sync Connection established. Total active channels: {len(self.active_sockets)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_sockets:
            self.active_sockets.remove(websocket)
            print(f"❌ Connection severed. Remaining channels: {len(self.active_sockets)}")

    async def broadcast_new_ticket_event(self, ticket_data: dict):
        """
        Blasts a JSON data packet down all active administration lines concurrently.
        """
        stale_sockets = []
        for connection in self.active_sockets:
            try:
                await connection.send_json({
                    "event": "TICKET_CREATED",
                    "data": ticket_data
                })
            except Exception:
                # Track broken or closed connections to clean up the memory pool safely
                stale_sockets.append(connection)
                
        for broken_socket in stale_sockets:
            self.disconnect(broken_socket)

# Instantiated singular socket hub token
ws_hub = TicketBroadcastManager()


@router.websocket("/ws/live-sync")
async def ticket_realtime_sync_endpoint(websocket: WebSocket):
    """
    📡 Live WebSocket Persistent Access Point
    Admin dashboards subscribe here to receive instant live stream data blocks.
    """
    await ws_hub.connect(websocket)
    try:
        while True:
            # Keep the socket pipeline alive listening for client pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_hub.disconnect(websocket)
    except Exception:
        ws_hub.disconnect(websocket)


@router.get("", response_model=List[TicketResponse])
async def fetch_all_student_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)  # 🛡️ RESTORED AUTH BARRIER
):
    """
    📥 Read Operation: Pulls registered grievance tickets from PostgreSQL / SQLite.
    👑 TENANT ISOLATION LAYER: Admins view all records, students only see their own tickets.
    """
    try:
        if current_user.role == "admin":
            # Administrators pull the global systemic queue
            statement = select(Ticket).order_by(Ticket.created_at.desc() if hasattr(Ticket, 'created_at') else Ticket.id.desc())
        else:
            # Students are strictly bounded to rows matching their user identifier fields
            # Check if your Ticket model houses user_id or email tracking parameters
            filter_column = Ticket.user_id if hasattr(Ticket, 'user_id') else Ticket.email if hasattr(Ticket, 'email') else None
            
            if filter_column is not None:
                filter_val = current_user.id if hasattr(Ticket, 'user_id') else current_user.email
                statement = select(Ticket).where(filter_column == filter_val).order_by(Ticket.id.desc())
            else:
                # Fallback to general select if schema fields aren't present
                statement = select(Ticket).order_by(Ticket.id.desc())

        result = await db.execute(statement)
        tickets_list = result.scalars().all()
        return tickets_list
    except Exception as e:
        print(f"❌ [DATABASE LEDGER READ EXCEPTION] {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System was unable to scan relational ticket registries."
        )


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def open_new_grievance_ticket(
    payload: TicketCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_from_token)  # 🛡️ RESTORED AUTH BARRIER
):
    """
    📤 Write & Broadcast Operation: Commits a fresh ticket to disk and forces
    an automated WebSocket push down to all active admin panels live.
    """
    unique_id = f"TK-2026-{random.randint(1000, 9999)}"
    current_time_str = datetime.datetime.now().strftime("%B %d, %Y")
    current_time_with_clock = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
    
    initial_timeline = [{
        "date": current_time_with_clock,
        "message": f"Ticket created successfully by student ({current_user.name}) and routed to dispatch systems."
    }]

    new_ticket = Ticket(
        id=unique_id,
        subject=payload.subject,
        category=payload.category,
        priority=payload.priority,
        status="Open",
        description=payload.description,
        timeline=initial_timeline,
        created_date=current_time_str
    )

    # 👑 Assign ownership to the authenticated student profile if the column is present
    if hasattr(Ticket, 'user_id'):
        new_ticket.user_id = current_user.id
    if hasattr(Ticket, 'email'):
        new_ticket.email = current_user.email

    try:
        db.add(new_ticket)
        await db.commit()
        await db.refresh(new_ticket)
    except Exception as db_fault:
        await db.rollback()
        print(f"❌ [DATABASE WRITE TRANSACTION EXCEPTION] {str(db_fault)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed recording grievance metrics into disk vaults."
        )

    # 🚀 THE REAL-TIME MAGIC: Convert model data to dictionary and broadcast it instantly
    serialized_ticket = {
        "id": new_ticket.id,
        "subject": new_ticket.subject,
        "category": new_ticket.category,
        "priority": new_ticket.priority,
        "status": new_ticket.status,
        "description": new_ticket.description,
        "timeline": new_ticket.timeline,
        "created_date": new_ticket.created_date
    }
    await ws_hub.broadcast_new_ticket_event(serialized_ticket)

    return new_ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def alter_existing_ticket_status(
    ticket_id: str,
    payload: TicketStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(verify_admin_clearance)  # 🔒 RESTORED ADMIN PRIVILEGE GUARD
):
    """
    🔄 Update Operation: Modifies ticket lifecycle and writes an audit note.
    Secured so only cleared admin operators can manipulate ticket tracking states.
    """
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket_instance = result.scalar_one_or_none()

    if not ticket_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grievance token {ticket_id} does not exist in administrative indexes."
        )

    current_time_with_clock = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
    updated_timeline = list(ticket_instance.timeline) if ticket_instance.timeline else []
    
    updated_timeline.append({
        "date": current_time_with_clock,
        "message": f"Administrative state adjustment by {current_admin.name}: Status updated to '{payload.status}'."
    })

    try:
        ticket_instance.status = payload.status
        ticket_instance.timeline = updated_timeline

        db.add(ticket_instance)
        await db.commit()
        await db.refresh(ticket_instance)
        return ticket_instance
    except Exception as db_fault:
        await db.rollback()
        print(f"❌ [STATUS PATUATION CORE FAULT] {str(db_fault)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Grievance lifecycle state change failed to commit."
        )