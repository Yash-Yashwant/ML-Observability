from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy.orm import declarative_base, sessionmaker
import os

load_dotenv()

user = os.getenv("DB_USER")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")
password = os.getenv("DB_PASSWORD")

# Debug print to verify env variables are loaded
print(f"DEBUG - User: {user}")
print(f"DEBUG - Host: {host}")
print(f"DEBUG - Port: {port}")
print(f"DEBUG - DB: {dbname}")

DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"

# creating a SQL-Alchemy engine

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(engine) #session make var, this will be used to make the actual session

#main class

Base=declarative_base()
