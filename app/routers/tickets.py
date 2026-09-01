from fastapi import APIRouter, HTTPException
from app.schemas import TicketCreate
from app.services.ticket_service import create_ticket, get_ticket


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("")
def create(req: TicketCreate):
    ticket = create_ticket(req.title, req.description)
    return {
        "ticket_id": ticket.ticket_id,
        "title": ticket.title,
        "status": ticket.status,
    }


@router.get("/{ticket_id}")
def get(ticket_id: str):
    ticket = get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="工单不存在")
    return {
        "ticket_id": ticket.ticket_id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
    }
