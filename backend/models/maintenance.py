import enum
from sqlalchemy import Column, String, Enum, Integer, Date
from database import Base

class MaintenanceStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    denied = "denied"
    completed = "completed"

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    teacher_name = Column(String, nullable=False)
    room = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.pending)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)