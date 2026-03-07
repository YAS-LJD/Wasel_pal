from sqlalchemy.orm import Session


def get_user_by_email(db: Session, email: str):
    return None


def create_user(db: Session, data: dict):
    return data
