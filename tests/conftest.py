import pytest
from app import create_app
from app.models import db, Usuario

@pytest.fixture
def app():
    # Set up config for an in-memory SQLite DB
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def new_user(app):
    with app.app_context():
        user = Usuario(
            username='testuser', 
            email='test@example.com', 
            nombre_completo='Test User',
            suscripcion_activa=False
        )
        user.set_password('TestPass123!')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user
