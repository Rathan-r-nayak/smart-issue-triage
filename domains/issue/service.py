from sqlalchemy.orm import Session
from .schema import IssueCreate
from .model import IssueDBModel
from sqlalchemy.exc import SQLAlchemyError


def create_issue(db: Session, issue_data: IssueCreate, reporter_id: str) -> IssueDBModel:
    """
    Core business logic for creating a ticket. 
    Accepts the validated payload and the strictly verified reporter_id.
    """
    try:
        new_issue = IssueDBModel(
            title = issue_data.title,
            description = issue_data.description,
            issue_type = issue_data.issue_type.value,
            custom_metadata = issue_data.custom_metadata,
            reporter_id = reporter_id,
            assignee_id = issue_data.assignee_id
        )

        db.add(new_issue)
        db.commit()
        db.refresh(new_issue)

        new_issue.ticket_key = f"SIT-{new_issue.id}"

        db.commit()
        db.refresh(new_issue)
        
        return new_issue

    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Failed to create issue in database: {str(e)}")