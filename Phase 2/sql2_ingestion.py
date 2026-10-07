from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Database connection
engine = create_engine(
    "mysql+pymysql://root:root@localhost/friday"
)

Base = declarative_base()


# Ingestion Log Table
class IngestionLog(Base):
    __tablename__ = "ingestion_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(255), nullable=False)
    row_count = Column(Integer, nullable=False)
    load_time = Column(DateTime, nullable=False)


# Create table
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

# Insert a log record
log = IngestionLog(
    file_name="telcom_churn.csv",
    row_count=7043,
    load_time=datetime.now()
)

session.add(log)
session.commit()

print("Log record inserted successfully.")

# Display all log records
logs = session.query(IngestionLog).all()

print("\nIngestion Log Records:")
for row in logs:
    print(
        f"Log ID: {row.log_id}, "
        f"File: {row.file_name}, "
        f"Rows: {row.row_count}, "
        f"Load Time: {row.load_time}"
    )

session.close()