from domains.core.dependencies import Base, engine
from fastapi import FastAPI

from domains.user.router import router as user_router
from domains.issue.router import router as issue_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Smart Issue Triage API",
    description="Omnichannel API for Jira-like issue tracking.",
    version="1.0.0"
)

app.include_router(user_router)
app.include_router(issue_router)


@app.get("/", tags=["System"])
def health_check():
    """A simple ping to verify the server is alive."""
    return {"status": "Engine is running! PostgreSQL is connected and Domains are registered."}