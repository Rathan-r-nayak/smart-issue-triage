# src/main.py
from fastapi import FastAPI
from src.modules.core.database import engine
from src.modules import Base  # 🚨 Imports our gathered models to build them safely
from src.modules.employees.router import router as employee_router
from src.modules.tickets.router import router as ticket_router
from src.modules.core.logger import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Creates all physical tables inside Postgres automatically on boot
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Issue Triage API Engine",
    description="Domain-Driven Architecture utilizing FastAPI, SQLAlchemy, and Pydantic.",
    version="1.0.0"
)

# Mount Routers
app.include_router(employee_router, prefix="/api")
app.include_router(ticket_router, prefix="/api")

@app.get("/")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "online", "project": "smart-issue-triage"}