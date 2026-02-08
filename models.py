from sqlalchemy import Column, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Code(Base):
    __tablename__ = "codes"
    code = Column(String, primary_key=True)
    file_path = Column(String)
    qr_path = Column(String)
    original_name = Column(String)
    created_at = Column(Float)
    expires_at = Column(Float)
    status = Column(String)
