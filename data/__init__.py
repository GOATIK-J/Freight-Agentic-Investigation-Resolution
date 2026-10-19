"""F.A.I.R. synthetic data layer."""
from .database import init_db, get_db_path, get_connection

__all__ = ["init_db", "get_db_path", "get_connection"]