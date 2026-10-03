import pytest
from app.database.connection import SessionLocal
from app.models.user import User


@pytest.fixture(autouse=True)
def cleanup_test_users():
    yield
    db = SessionLocal()
    db.query(User).filter(User.email.like("%@test.com")).delete(synchronize_session=False)
    db.commit()
    db.close()

