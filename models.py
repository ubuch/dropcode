from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Code(Base):
    __tablename__ = "codes"

    code = Column(String, primary_key=True)
    qr_path = Column(String)
    created_at = Column(Float)
    expires_at = Column(Float)
    status = Column(String)

    files = relationship(
        "File",
        back_populates="code_rel",
        cascade="all, delete-orphan",
    )


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("codes.code"))
    file_path = Column(String)
    original_name = Column(String)

    code_rel = relationship("Code", back_populates="files")
