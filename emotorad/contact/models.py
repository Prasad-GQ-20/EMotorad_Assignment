from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    phoneNumber = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    linkedId = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    linkPrecedence = Column(Enum('primary', 'secondary', name='link_precedence'), default='primary')
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletedAt = Column(DateTime, nullable=True)

engine = create_engine('mysql://EMotorad_v1:EMotorad_v1@localhost/EMotorad_v1')
Session = scoped_session(sessionmaker(bind=engine))
Base.metadata.create_all(engine)