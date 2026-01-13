from contextlib import contextmanager
from sqlalchemy.orm import Session
from typing import Generator
import logging

logger = logging.getLogger(__name__)

@contextmanager
def atomic_transaction(db: Session) -> Generator[Session, None, None]:
    """
    Context manager for atomic transactions

    Automatically commits on success and rolls back on error

    Usage:
    with atomic_transaction(db) as session:
    # Your database operations
    session.add(object)

    Args:
    db: Database session

    Yields:
    db: Database session
    """
    try:
        yield db
        db.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise

@contextmanager
def pessimistic_lock(db: Session, model, filter_condition) -> Generator:
    """
    Context manager for pessimistic locking (row-level lock)

    Usage:
    with pessimistic_lock(db, CreditBalance, CreditBalance.user_id == user_id) as balance:
    balance.balance -= 100

    Args:
    db: Database session
    model: SQLAlchemy model
    filter_condition: Filter condition

    Yields:
    Locked object
    """
    try:
        obj = db.query(model).filter(filter_condition).with_for_update().first()

        if not obj:
            raise ValueError(f"Object not found for locking")
        
        yield obj
    
    except Exception as e:
        logger.error(f"Error during pessimistic lock: {e}")
        raise
    

