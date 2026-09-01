from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.db import Base, engine
from app.routers import agent, chat, documents, tickets


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(tickets.router)
app.include_router(agent.router)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
