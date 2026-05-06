from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Numeric(10, 2), default=0)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("User", backref="account")