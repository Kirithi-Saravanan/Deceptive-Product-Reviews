import pytest
from pathlib import Path
import sys

# Ensure backend and ml/src are in sys.path
backend_dir = Path(__file__).resolve().parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'ml' / 'src'))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.models.user import User
from app.core.security import get_password_hash, create_access_token

# Use in-memory SQLite with StaticPool for fast, isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Creates a fresh database schema for every test function."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Provides a TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Creates and returns a test user."""
    user = User(
        email="testuser@example.com",
        name="Test User",
        hashed_password=get_password_hash("testpassword123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user):
    """Returns a valid JWT access token for test_user."""
    return create_access_token(test_user.id)


@pytest.fixture
def auth_headers(test_user_token):
    """Returns headers with Bearer token for test_user."""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest.fixture
def second_user(db_session):
    """Creates and returns a second distinct user for isolation testing."""
    user = User(
        email="seconduser@example.com",
        name="Second User",
        hashed_password=get_password_hash("password456"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def second_user_token(second_user):
    """Returns a valid JWT access token for second_user."""
    return create_access_token(second_user.id)


@pytest.fixture
def second_auth_headers(second_user_token):
    """Returns headers with Bearer token for second_user."""
    return {"Authorization": f"Bearer {second_user_token}"}
