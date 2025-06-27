from schemas import ma
from models.order import Order, OrderItem
from models.menu import MenuItem
from marshmallow import Schema, fields, validate

class OrderItemSchema(ma.SQLAlchemySchema):
    class Meta:
        model = OrderItem

    id = ma.auto_field()
    menu_item_id = ma.Int(required=True)
    quantity = ma.Int(required=True)

    # Add nested MenuItem fields for context
    title = ma.Function(lambda obj: obj.menu_item.title)
    price = ma.Function(lambda obj: obj.menu_item.price)

class OrderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Order

    id = ma.auto_field()
    customer_name = ma.Str(required=True)
    created_at = ma.auto_field()
    total = ma.Float()
    items = ma.Nested(OrderItemSchema, many=True)

class OrderItemUpdateSchema(Schema):
    menu_item_id = fields.Int(required=True)
    quantity = fields.Int(required=True)

class OrderUpdateSchema(Schema):
    items = fields.List(fields.Nested(OrderItemUpdateSchema), required=True)