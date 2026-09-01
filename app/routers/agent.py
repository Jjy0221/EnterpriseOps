from fastapi import APIRouter
from app.schemas import AgentRequest
from app.services.agent_service import run_agent


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("")
def agent(req: AgentRequest) -> dict:
    return {"answer": run_agent(req.message)}

