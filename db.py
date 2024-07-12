from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./objectifs.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Objectif(Base):
    __tablename__ = "objectifs"

    id = Column(Integer, primary_key=True, index=True)
    pays = Column(String, index=True)
    segment = Column(String, index=True)
    possible = Column(Integer)
    mois_dernier = Column(Integer)
    juillet_now = Column(Integer)
    taux_2023 = Column(Float)
    taux_2024 = Column(Float)
    obj_juillet = Column(Integer)
    reste_a_faire = Column(Integer)

Base.metadata.create_all(bind=engine)
