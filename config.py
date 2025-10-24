# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Ожидается, что вы установите DATABASE_URL в .env или в окружении:
# пример: postgresql://user:password@localhost:5432/mydb
#DATABASE_URI = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:Post/.77SD_/@localhost:5432/course_records_db")
DATABASE_URI = os.getenv("DATABASE_URL", "postgresql+psycopg://user_04:password4@10.115.0.67:5432/edu_practice01_04")

# Flask settings
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
