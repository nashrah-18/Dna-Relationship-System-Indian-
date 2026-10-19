from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./data/dna_intelligence.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

class DNAProfile(Base):
    __tablename__ = "dna_profiles"
    sample_id = Column(String, primary_key=True, index=True)
    sex = Column(String)
    amel = Column(Integer, default=0)
    d3s1358 = Column(Integer, default=0)
    vwa = Column(Integer, default=0)
    d16s539 = Column(Integer, default=0)
    csf1po = Column(Integer, default=0)
    tpox = Column(Integer, default=0)
    d8s1179 = Column(Integer, default=0)
    d21s11 = Column(Integer, default=0)
    d18s51 = Column(Integer, default=0)
    dys391 = Column(Integer, default=0)
    d2s441 = Column(Integer, default=0)
    d19s433 = Column(Integer, default=0)
    tho1 = Column(Integer, default=0)
    fga = Column(Integer, default=0)
    d22s1045 = Column(Integer, default=0)
    d5s818 = Column(Integer, default=0)
    d13s317 = Column(Integer, default=0)
    d7s820 = Column(Integer, default=0)
    se33 = Column(Integer, default=0)
    d10s1248 = Column(Integer, default=0)
    d1s1656 = Column(Integer, default=0)
    d12s391 = Column(Float, default=0.0)
    d2s1338 = Column(Integer, default=0)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    sector = Column(String)
    password_hash = Column(String, nullable=False)

class HospitalLog(Base):
    __tablename__ = "hospital_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    action = Column(String)
    sample_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class PoliceCase(Base):
    __tablename__ = "police_cases"
    case_id = Column(String, primary_key=True)
    description = Column(Text)
    status = Column(String)
    updated_by = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class PoliceLog(Base):
    __tablename__ = "police_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    action = Column(String)
    case_id = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)