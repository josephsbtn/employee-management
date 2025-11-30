import os

class Config:
    MONGO_URI = os.environ.get("MONGO_URI")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    DATABASE = os.environ.get("DATABASE")
    