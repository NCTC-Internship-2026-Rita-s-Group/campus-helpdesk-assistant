import datetime
import random
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models.db_models import Ticket
from app.models.schemas import TicketCreate, TicketResponse, TicketStatusUpdate

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
        self.active_sockets.remove(websocket)
        print(f"❌ Connection severed. Remaining channels: {len(self.active_sockets)}")

    async def broadcast_new_ticket_event(self, ticket_data: dict):
        """
        Blasts a JSON data packet down all active administration lines concurrently.
        """
        for connection in self.active_sockets:
            try:
                await connection.send_json({
                    "event": "TICKET_CREATED",
                    "data": ticket_data
                })
            except Exception:
                # Safely pass over broken or stale socket references
                pass

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


@router.get("", response_model=List[TicketResponse])
async def fetch_all_student_tickets(db: AsyncSession = Depends(get_db)):
    """
    📥 Read Operation: Pulls all registered grievance tickets from PostgreSQL.
    """
    result = await db.execute(select(Ticket).order_by(Ticket.created_at.desc()))
    tickets_list = result.scalars().all()
    return tickets_list


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def open_new_grievance_ticket(
    payload: TicketCreate, 
    db: AsyncSession = Depends(get_db)
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
        "message": "Ticket created successfully by student and routed to dispatch systems."
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

    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)

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
    db: AsyncSession = Depends(get_db)
):
    """
    🔄 Update Operation: Modifies ticket lifecycle and writes an audit note.
    """
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket_instance = result.scalar_one_or_none()

    if not ticket_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grievance token {ticket_id} does not exist in administrative indexes."
        )

    current_time_with_clock = datetime.datetime.now().strftime("%B %d, %Y - %I:%M %p")
    updated_timeline = list(ticket_instance.timeline)
    updated_timeline.append({
        "date": current_time_with_clock,
        "message": f"Administrative state adjustment: Status updated to '{payload.status}'."
    })

    ticket_instance.status = payload.status
    ticket_instance.timeline = updated_timeline

    db.add(ticket_instance)
    await db.commit()
    await db.refresh(ticket_instance)
    return ticket_instance