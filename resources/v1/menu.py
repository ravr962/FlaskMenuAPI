from flask import Blueprint, request
from flask_restful import Api, Resource
from models.menu import MenuItem
from models import db
from schemas.menu import MenuItemSchema
from math import ceil
from auth_helpers import admin_required, role_required
from flasgger import swag_from

# menu_bp = Blueprint('menu', __name__)   # create blueprint
# menu_api = Api(menu_bp)                 # bind Flask-RESTful API to it

menu_bp_v1 = Blueprint('menu_v1', __name__)
menu_api_v1 = Api(menu_bp_v1)

menu_item_schema = MenuItemSchema()
menu_items_schema = MenuItemSchema(many=True)

class MenuItemListResource(Resource):
    @swag_from({
    'parameters': [
        {
            'name': 'title',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by title',
        },
        {
            'name': 'min_price',
            'in': 'query',
            'type': 'number',
            'description': 'Minimum price filter',
        },
        {
            'name': 'max_price',
            'in': 'query',
            'type': 'number',
            'description': 'Maximum price filter',
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'description': 'Page number',
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'description': 'Number of items per page',
        }
    ],
    'responses': {
        200: {
            'description': 'List of menu items',
            'examples': {
                'application/json': {
                    'items': [
                        {
                            'id': 1,
                            'title': 'Burger',
                            'price': 8.5,
                            'inventory': 20
                        }
                    ],
                    'page': 1,
                    'per_page': 10,
                    'total': 1,
                    'pages': 1
                }
            }
        }
    }
    })
    def get(self):
        # items = MenuItem.query.all()
        # return menu_items_schema.dump(items)
        
        # Query params
        title = request.args.get('title')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # Base query
        query = MenuItem.query

        # Filtering
        if title:
            query = query.filter(MenuItem.title.ilike(f"%{title}%"))
        if min_price is not None:
            query = query.filter(MenuItem.price >= min_price)
        if max_price is not None:
            query = query.filter(MenuItem.price <= max_price)

        # Ordering
        sort_by = request.args.get('sort_by', 'id')  # default to 'id'
        order = request.args.get('order', 'asc')

        if hasattr(MenuItem, sort_by):
            column = getattr(MenuItem, sort_by)
            if order == 'desc':
                column = column.desc()
            query = query.order_by(column)

        # Search by title
        search = request.args.get('search')
        if search:
            query = query.filter(MenuItem.title.ilike(f'%{search}%'))


        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = menu_items_schema.dump(pagination.items)

        return {
            "items": items,
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }

    @swag_from({
    'security': [{'Bearer': []}],
    'parameters': [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "example": "Falafel"
                    },
                    "price": {
                        "type": "number",
                        "example": 7.99
                    }
                },
                "required": ["title", "price"]
            }
        }
    ],
    'responses': {
        201: {'description': 'Menu item created'},
        401: {'description': 'Unauthorized'}
    }
    })
    @admin_required
    @role_required('admin', 'manager')
    def post(self):
        data = request.get_json()
        print("Received data:", data)
        if not data:
            return {"error": "No input data provided"}, 400

        errors = menu_item_schema.validate(data)
        print("Validation errors:", errors)
        if errors:
            return {"errors": errors}, 422

        title = data['title']
        if MenuItem.query.filter_by(title=title).first():
            return {"error": f"Menu item '{title}' already exists."}, 400

        item = MenuItem(**data)
        db.session.add(item)
        db.session.commit()
        #return menu_item_schema.dump(item), 201
        #return {"item": menu_item_schema.dump(item)}, 201
        try:
            result = menu_item_schema.dump(item)
            return {"item": result}, 201
        except Exception as e:
            print("Serialization error:", str(e))
            return {"error": "Serialization failed"}, 500
    
# # Request validation
# parser = reqparse.RequestParser()
# parser.add_argument('title', required=True)
# parser.add_argument('price', type=float, required=True)
# parser.add_argument('inventory', type=int, required=True)

# class MenuItemListResource(Resource):
#     def get(self):
#         items = MenuItem.query.all()
#         return [{'id': item.id, 'title': item.title, 'price': item.price, 'inventory': item.inventory} for item in items]

#     def post(self):
#         args = parser.parse_args()
#         item = MenuItem(title=args['title'], price=args['price'], inventory=args['inventory'])
#         db.session.add(item)
#         db.session.commit()
#         return {'id': item.id, 'title': item.title, 'price': item.price, 'inventory': item.inventory}, 201


class MenuItemResource(Resource):
    def get(self, item_id):
        item = MenuItem.query.get_or_404(item_id)
        return menu_item_schema.dump(item)

    def delete(self, item_id):
        item = MenuItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return '', 204
    
# class MenuItemResource(Resource):
#     def get(self, item_id):
#         item = MenuItem.query.get_or_404(item_id)
#         return {'id': item.id, 'title': item.title, 'price': item.price, 'inventory': item.inventory}

#     def delete(self, item_id):
#         item = MenuItem.query.get_or_404(item_id)
#         db.session.delete(item)
#         db.session.commit()
#         return '', 204

# Register endpoints
# menu_api.add_resource(MenuItemListResource, '/menu/')
# menu_api.add_resource(MenuItemResource, '/menu/<int:item_id>')

# Register your resource here
menu_api_v1.add_resource(MenuItemListResource, '/menu/')
menu_api_v1.add_resource(MenuItemResource, '/menu/<int:item_id>')