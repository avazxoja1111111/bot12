"""
Database models and management for Kitobxon Kids Telegram Bot
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """User model for storing user registration and profile data"""
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, index=True)  # Telegram user ID
    child_name = Column(String, nullable=False)
    parent_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    age_group = Column(String, nullable=False)  # "7-10" or "11-14"
    region = Column(String, nullable=False)
    district = Column(String, nullable=False)
    mahalla = Column(String, nullable=True)
    telegram_username = Column(String, nullable=True)
    telegram_name = Column(String, nullable=True)
    registered = Column(Boolean, default=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_results = relationship("TestResult", back_populates="user", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

class Question(Base):
    """Question model for storing test questions"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    age_group = Column(String, nullable=False)  # "7-10" or "11-14"
    options = Column(JSON, nullable=False)  # List of 4 options
    correct_answer = Column(Integer, nullable=False)  # Index of correct answer (0-3)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)  # Admin user ID who created
    
    # Relationships
    test_answers = relationship("TestAnswer", back_populates="question")

class TestResult(Base):
    """Test result model for storing completed test data"""
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    age_group = Column(String, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="test_results")
    answers = relationship("TestAnswer", back_populates="test_result", cascade="all, delete-orphan")

class TestAnswer(Base):
    """Individual question answers within a test"""
    __tablename__ = "test_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    test_result_id = Column(Integer, ForeignKey("test_results.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_answer = Column(Integer, nullable=False)  # Index selected by user
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_result = relationship("TestResult", back_populates="answers")
    question = relationship("Question", back_populates="test_answers")

class Feedback(Base):
    """Feedback model for storing user feedback"""
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    feedback_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")

class RegionData(Base):
    """Static region/district/mahalla data"""
    __tablename__ = "region_data"
    
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, nullable=False)
    districts = Column(JSON, nullable=False)  # List of districts with mahallas
    created_at = Column(DateTime, default=datetime.utcnow)

# Database management functions
def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def close_db(db: Session):
    """Close database session"""
    db.close()

# Data migration functions
def migrate_json_to_db():
    """Migrate existing JSON data to database"""
    logger.info("Starting migration from JSON files to database...")
    
    db = get_db()
    try:
        # Migrate users
        migrate_users(db)
        
        # Migrate questions
        migrate_questions(db)
        
        # Migrate regions
        migrate_regions(db)
        
        db.commit()
        logger.info("Migration completed successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        close_db(db)

def migrate_users(db: Session):
    """Migrate users from JSON to database"""
    try:
        if os.path.exists("data/users.json"):
            with open("data/users.json", "r", encoding="utf-8") as f:
                users_data = json.load(f)
            
            for user_id, user_info in users_data.items():
                # Check if user already exists
                existing_user = db.query(User).filter(User.user_id == user_id).first()
                if existing_user:
                    continue
                
                # Create new user
                user = User(
                    user_id=user_id,
                    child_name=user_info.get("child_name", ""),
                    parent_name=user_info.get("parent_name", ""),
                    phone=user_info.get("phone", ""),
                    age_group=user_info.get("age_group", ""),
                    region=user_info.get("region", ""),
                    district=user_info.get("district", ""),
                    mahalla=user_info.get("mahalla", ""),
                    telegram_username=user_info.get("telegram_username", ""),
                    telegram_name=user_info.get("telegram_name", ""),
                    registered=user_info.get("registered", True),
                    registration_date=datetime.fromisoformat(user_info.get("registration_date", datetime.now().isoformat()))
                )
                db.add(user)
                
                # Migrate test results
                for result_data in user_info.get("test_results", []):
                    test_result = TestResult(
                        user_id=user_id,
                        age_group=result_data.get("age_group", user.age_group),
                        total_questions=result_data.get("total_questions", 0),
                        correct_answers=result_data.get("correct_answers", 0),
                        percentage=result_data.get("percentage", 0),
                        duration_seconds=result_data.get("duration", 0),
                        started_at=datetime.fromisoformat(result_data.get("date", datetime.now().isoformat())),
                        completed_at=datetime.fromisoformat(result_data.get("date", datetime.now().isoformat()))
                    )
                    db.add(test_result)
            
            logger.info(f"Migrated {len(users_data)} users")
            
    except Exception as e:
        logger.error(f"Error migrating users: {e}")

def migrate_questions(db: Session):
    """Migrate questions from JSON to database"""
    try:
        if os.path.exists("data/test_questions.json"):
            with open("data/test_questions.json", "r", encoding="utf-8") as f:
                questions_data = json.load(f)
            
            for age_group, questions_list in questions_data.items():
                for q_data in questions_list:
                    # Check if question already exists
                    existing_question = db.query(Question).filter(
                        Question.question_text == q_data["question"],
                        Question.age_group == age_group
                    ).first()
                    if existing_question:
                        continue
                    
                    question = Question(
                        question_text=q_data["question"],
                        age_group=age_group,
                        options=q_data["options"],
                        correct_answer=q_data["correct"]
                    )
                    db.add(question)
            
            logger.info(f"Migrated questions for age groups: {list(questions_data.keys())}")
            
    except Exception as e:
        logger.error(f"Error migrating questions: {e}")

def migrate_regions(db: Session):
    """Migrate regions from JSON to database"""
    try:
        if os.path.exists("data/regions.json"):
            with open("data/regions.json", "r", encoding="utf-8") as f:
                regions_data = json.load(f)
            
            for region, districts in regions_data.items():
                # Check if region already exists
                existing_region = db.query(RegionData).filter(RegionData.region == region).first()
                if existing_region:
                    continue
                
                region_data = RegionData(
                    region=region,
                    districts=districts
                )
                db.add(region_data)
            
            logger.info(f"Migrated {len(regions_data)} regions")
            
    except Exception as e:
        logger.error(f"Error migrating regions: {e}")

# Database service functions
class DatabaseService:
    """Service class for database operations"""
    
    @staticmethod
    def get_user(user_id: str) -> Optional[User]:
        """Get user by ID"""
        db = get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                # Load related data to avoid lazy loading issues
                _ = user.test_results
                _ = user.feedbacks
            return user
        finally:
            close_db(db)
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> User:
        """Create new user"""
        db = get_db()
        try:
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise e
        finally:
            close_db(db)
    
    @staticmethod
    def update_user(user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        """Update user data"""
        db = get_db()
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                for key, value in user_data.items():
                    setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise e
        finally:
            close_db(db)
    
    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users"""
        db = get_db()
        try:
            users = db.query(User).all()
            # Load related data to avoid lazy loading issues
            for user in users:
                _ = user.test_results
                _ = user.feedbacks
            return users
        finally:
            close_db(db)
    
    @staticmethod
    def get_questions_by_age_group(age_group: str) -> List[Question]:
        """Get questions for specific age group"""
        db = get_db()
        try:
            return db.query(Question).filter(Question.age_group == age_group).all()
        finally:
            close_db(db)
    
    @staticmethod
    def add_question(question_data: Dict[str, Any]) -> Question:
        """Add new question"""
        db = get_db()
        try:
            question = Question(**question_data)
            db.add(question)
            db.commit()
            db.refresh(question)
            return question
        except Exception as e:
            db.rollback()
            raise e
        finally:
            close_db(db)
    
    @staticmethod
    def delete_question(question_id: int) -> bool:
        """Delete question by ID"""
        db = get_db()
        try:
            question = db.query(Question).filter(Question.id == question_id).first()
            if question:
                db.delete(question)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise e
        finally:
            close_db(db)
    
    @staticmethod
    def save_test_result(result_data: Dict[str, Any]) -> TestResult:
        """Save test result"""
        db = get_db()
        try:
            test_result = TestResult(**result_data)
            db.add(test_result)
            db.commit()
            db.refresh(test_result)
            return test_result
        except Exception as e:
            db.rollback()
            raise e
        finally:
            close_db(db)
    
    @staticmethod
    def save_feedback(feedback_data: Dict[str, Any]) -> Feedback:
        """Save user feedback"""
        db = get_db()
        try:
            feedback = Feedback(**feedback_data)
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            return feedback
        except Exception as e:
            db.rollback()
            raise e
        finally:
            close_db(db)
    
    @staticmethod
    def get_regions() -> Dict[str, Any]:
        """Get all regions data"""
        db = get_db()
        try:
            regions = db.query(RegionData).all()
            result = {}
            for region in regions:
                result[region.region] = region.districts
            return result
        finally:
            close_db(db)

# Initialize database
def init_database():
    """Initialize database with tables and basic data"""
    try:
        create_tables()
        
        # Check if we need to migrate from JSON
        db = get_db()
        user_count = db.query(User).count()
        close_db(db)
        
        if user_count == 0:
            # No users exist, try migration
            if any(os.path.exists(f"data/{file}") for file in ["users.json", "test_questions.json", "regions.json"]):
                logger.info("Found existing JSON files, starting migration...")
                migrate_json_to_db()
            else:
                logger.info("No existing data found, starting fresh")
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_database()