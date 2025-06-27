from . import db
from sqlalchemy.schema import UniqueConstraint

class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    __table_args__ = (
        UniqueConstraint('title', name='uq_menu_item_title'),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    inventory = db.Column(db.Integer, nullable=False)