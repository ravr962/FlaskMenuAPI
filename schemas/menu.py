from schemas import ma
from models.menu import MenuItem

class MenuItemSchema(ma.SQLAlchemySchema):
    class Meta:
        model = MenuItem

    id = ma.auto_field()
    title = ma.Str(required=True)
    price = ma.Float(required=True)
    inventory = ma.Int(required=True)