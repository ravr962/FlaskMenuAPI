from flask import Blueprint, request
from flask_restful import Api, Resource
from models.menu import MenuItem
from models.order import Order, OrderItem
from models import db
from schemas.order import OrderSchema, OrderUpdateSchema
from auth_helpers import token_required

order_bp = Blueprint('order', __name__)
order_api = Api(order_bp)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_update_schema = OrderUpdateSchema()

class OrderListResource(Resource):
    @token_required
    def get(current_user, self):
        # orders = Order.query.all()
        orders = Order.query.filter_by(user_id=current_user.id).all()
        return orders_schema.dump(orders)

    @token_required
    def post(current_user, self):
        data = request.get_json()
        errors = order_schema.validate(data)
        if errors:
            return {"errors": errors}, 422

        customer_name = data['customer_name']
        items_data = data['items']

        total = 0
        order_items = []

        for item in items_data:
            menu_item = MenuItem.query.get(item['menu_item_id'])
            if not menu_item:
                return {"error": f"Menu item ID {item['menu_item_id']} does not exist"}, 400

            line_total = menu_item.price * item['quantity']
            total += line_total

            order_item = OrderItem(
                menu_item_id=menu_item.id,
                quantity=item['quantity']
            )
            order_items.append(order_item)

        order = Order(customer_name=customer_name, total=total, items=order_items, user=current_user)
        db.session.add(order)
        db.session.commit()

        return order_schema.dump(order), 201

class OrderResource(Resource):
    @token_required
    def get(current_user, self, order_id):
        order = Order.query.get_or_404(order_id)
        if order.user_id != current_user.id:
            return {"error": "Not authorized"}, 403
        return order_schema.dump(order)

    @token_required
    def delete(current_user, self, order_id):
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
        if not order:
            return {"error": "Order not found or unauthorized"}, 404

        db.session.delete(order)
        db.session.commit()
        return '', 204

    @token_required
    def put(current_user, self, order_id):
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
        if not order:
            return {"error": "Order not found or unauthorized"}, 404

        data = request.get_json()
        errors = order_update_schema.validate(data)
        if errors:
            return {"errors": errors}, 422

        # Clear existing order items and update them
        order.items.clear()
        total = 0

        for item in data["items"]:
            menu_item = MenuItem.query.get(item["menu_item_id"])
            if not menu_item:
                return {"error": f"Menu item ID {item['menu_item_id']} does not exist"}, 400
            order_item = OrderItem(menu_item_id=menu_item.id, quantity=item["quantity"])
            order.items.append(order_item)
            total += menu_item.price * item["quantity"]

        order.total = total
        db.session.commit()
        return order_schema.dump(order)

# Register endpoints
order_api.add_resource(OrderListResource, '/orders/')
order_api.add_resource(OrderResource, '/orders/<int:order_id>')