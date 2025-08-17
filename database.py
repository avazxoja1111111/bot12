import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import JSON

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/kitobxon_kids")

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    child_name = Column(String, nullable=False)
    parent_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    age_group = Column(String, nullable=False)
    region = Column(String, nullable=False)
    district = Column(String, nullable=False)
    mahalla = Column(String, nullable=False)
    telegram_username = Column(String, nullable=True)
    telegram_name = Column(String, nullable=True)
    registered = Column(Boolean, default=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_results = relationship("TestResult", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of options
    correct_answer = Column(Integer, nullable=False)  # Index of correct option
    age_group = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    age_group = Column(String, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="test_results")
    test_answers = relationship("TestAnswer", back_populates="test_result")

class TestAnswer(Base):
    __tablename__ = "test_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    test_result_id = Column(Integer, ForeignKey("test_results.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(Integer, nullable=True)  # User's answer index
    is_correct = Column(Boolean, nullable=False)
    time_taken = Column(Integer, nullable=False)  # Seconds
    
    # Relationships
    test_result = relationship("TestResult", back_populates="test_answers")
    question = relationship("Question")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    feedback_text = Column(Text, nullable=False)
    phone = Column(String, nullable=True)
    telegram_username = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")

class RegionData(Base):
    __tablename__ = "region_data"
    
    id = Column(Integer, primary_key=True, index=True)
    region_name = Column(String, nullable=False)
    district_name = Column(String, nullable=False)
    mahalla_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseService:
    @staticmethod
    def get_session() -> Session:
        return SessionLocal()
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> User:
        session = DatabaseService.get_session()
        try:
            user = User(
                user_id=str(user_data["user_id"]),
                child_name=user_data["child_name"],
                parent_name=user_data["parent_name"],
                phone=user_data.get("phone", ""),
                age_group=user_data["age_group"],
                region=user_data["region"],
                district=user_data["district"],
                mahalla=user_data["mahalla"],
                telegram_username=user_data.get("telegram_username", ""),
                telegram_name=user_data.get("telegram_name", "")
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_user(user_id: str) -> Optional[User]:
        session = DatabaseService.get_session()
        try:
            return session.query(User).filter(User.user_id == user_id).first()
        finally:
            session.close()
    
    @staticmethod
    def update_user(user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        session = DatabaseService.get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            if user:
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                session.commit()
                session.refresh(user)
            return user
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_all_users() -> List[User]:
        session = DatabaseService.get_session()
        try:
            return session.query(User).all()
        finally:
            session.close()
    
    @staticmethod
    def add_question(question_data: Dict[str, Any]) -> Question:
        session = DatabaseService.get_session()
        try:
            question = Question(
                question_text=question_data["question_text"],
                options=question_data["options"],
                correct_answer=question_data["correct_answer"],
                age_group=question_data["age_group"]
            )
            session.add(question)
            session.commit()
            session.refresh(question)
            return question
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_questions_by_age_group(age_group: str) -> List[Question]:
        session = DatabaseService.get_session()
        try:
            return session.query(Question).filter(Question.age_group == age_group).all()
        finally:
            session.close()
    
    @staticmethod
    def delete_question(question_id: int) -> bool:
        session = DatabaseService.get_session()
        try:
            question = session.query(Question).filter(Question.id == question_id).first()
            if question:
                session.delete(question)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def clear_questions_by_age_group(age_group: str) -> int:
        """Clear all questions for a specific age group and return count of deleted questions"""
        session = DatabaseService.get_session()
        try:
            questions = session.query(Question).filter(Question.age_group == age_group).all()
            count = len(questions)
            for question in questions:
                session.delete(question)
            session.commit()
            return count
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def save_test_result(test_data: Dict[str, Any]) -> TestResult:
        session = DatabaseService.get_session()
        try:
            test_result = TestResult(
                user_id=str(test_data["user_id"]),
                age_group=test_data["age_group"],
                total_questions=test_data["total_questions"],
                correct_answers=test_data["correct_answers"],
                percentage=test_data["percentage"],
                duration_seconds=test_data["duration_seconds"]
            )
            session.add(test_result)
            session.commit()
            session.refresh(test_result)
            return test_result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def save_feedback(feedback_data: Dict[str, Any]) -> Feedback:
        session = DatabaseService.get_session()
        try:
            feedback = Feedback(
                user_id=str(feedback_data["user_id"]),
                feedback_text=feedback_data["feedback_text"],
                phone=feedback_data.get("phone", ""),
                telegram_username=feedback_data.get("telegram_username", "")
            )
            session.add(feedback)
            session.commit()
            session.refresh(feedback)
            return feedback
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_user_test_count(user_id: str) -> int:
        """Get count of tests taken by user"""
        session = DatabaseService.get_session()
        try:
            count = session.query(TestResult).filter(TestResult.user_id == user_id).count()
            return count
        finally:
            session.close()
    
    @staticmethod
    def get_regions() -> Dict[str, Any]:
        """Get regions data from database or return default structure"""
        session = DatabaseService.get_session()
        try:
            regions = session.query(RegionData).all()
            if not regions:
                return {}
            
            result = {}
            for region_data in regions:
                if region_data.region_name not in result:
                    result[region_data.region_name] = {
                        "districts": [],
                        "mahallas": {}
                    }
                
                if region_data.district_name not in result[region_data.region_name]["districts"]:
                    result[region_data.region_name]["districts"].append(region_data.district_name)
                
                if region_data.mahalla_name:
                    if region_data.district_name not in result[region_data.region_name]["mahallas"]:
                        result[region_data.region_name]["mahallas"][region_data.district_name] = []
                    if region_data.mahalla_name not in result[region_data.region_name]["mahallas"][region_data.district_name]:
                        result[region_data.region_name]["mahallas"][region_data.district_name].append(region_data.mahalla_name)
            
            return result
        finally:
            session.close()

def init_database():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise e
