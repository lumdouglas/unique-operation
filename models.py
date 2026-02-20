"""SQLAlchemy ORM models for the Sushi Catering Management System."""
from sqlalchemy import Column, Integer, String, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DATABASE_URL

Base = declarative_base()


class Recipe(Base):
    """Recipe model: name, ingredients, procedures, supplies, base_servings."""

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    # e.g. [{"item": "fish", "quantity": 200, "unit": "g", "cost_per_unit": 15}]
    ingredients = Column(JSON, default=list)
    # e.g. ["Step 1: Rinse rice", "Step 2: Cook for 20min"]
    procedures = Column(JSON, default=list)
    # e.g. [{"item": "tray", "quantity": 10}]
    supplies = Column(JSON, default=list)
    base_servings = Column(Integer, default=50)

    def to_dict(self):
        """Serialize recipe for JSON/AI consumption."""
        return {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients or [],
            "procedures": self.procedures or [],
            "supplies": self.supplies or [],
            "base_servings": self.base_servings,
        }


class User(Base):
    """Staff user linked to Discord; role controls permissions."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    discord_id = Column(String, unique=True, nullable=False)
    role = Column(String, default="general")  # sushi_chef, prep_cook, general, admin


# Engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Return a new database session (caller should close or use as context)."""
    return SessionLocal()
