from datetime import datetime
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Ticket


def create_ticket(title: str, description: str = ""):
    db = SessionLocal()
    try:
        ticket = Ticket(
            ticket_id="T" + datetime.now().strftime("%Y%m%d%H%M%S%f"),
            title=title,
            description=description,
            status="OPEN",
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    finally:
        db.close()


def get_ticket(ticket_id: str):
    db = SessionLocal()
    try:
        stmt = select(Ticket).where(Ticket.ticket_id == ticket_id)
        return db.scalar(stmt)
    finally:
        db.close()
