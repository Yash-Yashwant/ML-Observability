from sqlite3.dbapi2 import Timestamp
import time
import pytz
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, JSON, false, null
from datetime import datetime
from connection import Base, SessionLocal, engine

# this wont work because its going to be static time, the time of creation and instead it needs to be created when called
# utc_timestamp = datetime.utcnow
mountain = pytz.timezone("America/Denver")
# local_time = utc_timestamp.astimezone(mountain)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, autoincrement=True, primary_key=True)
    model_id = Column(String, nullable=False)
    prediction = Column(Integer, nullable=False)
    input_feature = Column(JSON)
    time_stamp = Column(DateTime(timezone=True), default=lambda: datetime.now(mountain))


class GroundTruth(Base):
    __tablename__ = "groundtruth"


    id = Column(Integer,primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, unique=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(mountain))
    actual_value=Column(Integer, nullable=False) # 0 or

    



# create table and test it

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Table Created")

    # demo insertion

    session = SessionLocal()

    # test = Prediction(
    #     model_id = "test_v1",
    #     prediction = 1,
    #     input_feature={
    #         "transaction_amount":127,
    #         "name":"nemo",
    #         "days":45
    #     }
    # )

    test_gt = GroundTruth(
        prediction_id = 1,
        actual_value = 1
    )

    session.add(test_gt)
    session.commit()
    print("row ingested")
    session.close()



