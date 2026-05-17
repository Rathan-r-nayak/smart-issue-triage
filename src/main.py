# main.py
from fastapi import FastAPI
from src.modules.core.database import engine
from Models import Base  # Collects all schema creations metadata definitions
from Routers.employee_router import employee_router
from Routers.ticket_router import ticket_router

# Generate the physical tables inside Postgres on server initialization
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Issue Triage Backend Engine",
    description="Decoupled enterprise service desk API for managing manual and automated workflows.",
    version="1.0.0"
)

# Mount the explicitly named router modules
app.include_router(employee_router, prefix="/api")
app.include_router(ticket_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "online", "project": "smart-issue-triage"}