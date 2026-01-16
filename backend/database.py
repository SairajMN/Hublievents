"""
Database configuration and session management for Hublievents Backend API.
Supports both SQLite (development) and PostgreSQL (production).
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from typing import Generator

from config import settings

logger = logging.getLogger(__name__)

# Database URL configuration
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Engine configuration based on database type
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration for development
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG,
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=settings.DEBUG,
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base(metadata=MetaData())

# Naming convention for constraints and indexes
Base.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Provides a database session that automatically closes when done.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database operations.
    Useful for operations outside of FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database context error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """
    Create all database tables.
    Should be called on application startup.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise


def drop_tables():
    """
    Drop all database tables.
    USE WITH CAUTION - This will delete all data!
    """
    try:
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("Database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {str(e)}")
        raise


def reset_database():
    """
    Reset database by dropping and recreating all tables.
    USE WITH CAUTION - This will delete all data!
    """
    logger.warning("Resetting database - all data will be lost!")
    drop_tables()
    create_tables()
    logger.info("Database reset complete")


# Health check function
def check_database_connection() -> bool:
    """
    Check if database connection is working.
    Returns True if connection is successful, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False
