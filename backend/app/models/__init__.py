"""ORM models. Import all here so Alembic autogenerate sees them."""
from app.models.collection import Collection
from app.models.houses import House
from app.models.users import User

__all__ = ["User", "House", "Collection"]
