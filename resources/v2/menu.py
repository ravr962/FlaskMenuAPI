# resources/v2/menu.py
from flask import Blueprint, request
from flask_restful import Api, Resource
from models.menu import MenuItem
from schemas.menu_v2 import MenuItemSchemaV2
from math import ceil

menu_bp_v2 = Blueprint('menu_v2', __name__)
menu_api_v2 = Api(menu_bp_v2)

menu_item_schema = MenuItemSchemaV2()
menu_items_schema = MenuItemSchemaV2(many=True)

class MenuItemListResourceV2(Resource):
    def get(self):
        # Filtering and pagination logic like v1
        title = request.args.get('title')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = MenuItem.query

        if title:
            query = query.filter(MenuItem.title.ilike(f"%{title}%"))
        if min_price is not None:
            query = query.filter(MenuItem.price >= min_price)
        if max_price is not None:
            query = query.filter(MenuItem.price <= max_price)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = pagination.items

        result = menu_items_schema.dump(items)

        # add description to each item in result (mocked)
        for item in result:
            item["description"] = f"{item['title']} is a great choice!"

        return {
            "items": result,
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": ceil(pagination.total / per_page)
        }

menu_api_v2.add_resource(MenuItemListResourceV2, '/menu/')