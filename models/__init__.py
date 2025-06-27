from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # ✅ define the db first

# ⏬ import model files only after db is defined
from .menu import MenuItem
from .order import Order