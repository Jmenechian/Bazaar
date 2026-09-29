import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
# Import all models so that Base.metadata knows about them
from models.user import User

# Read database credentials from environment or use local defaults
DB_USER = os.getenv("DB_USER", "bazaar")
DB_PASSWORD = os.getenv("DB_PASSWORD", "bazaar")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bazaar_users")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Fix Heroku/Cloud postgres:// prefix to postgresql:// if present
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables defined in models if they don't already exist."""
    Base.metadata.create_all(bind=engine)

# Automatically create tables on module load
try:
    init_db()
except Exception as e:
    # If DB is not reachable during build/import, print warning
    print(f"Warning: Could not connect to database on startup: {e}")
