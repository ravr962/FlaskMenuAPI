# schemas/menu_v2.py
from marshmallow import Schema, fields

class MenuItemSchemaV2(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    price = fields.Float(required=True)
    inventory = fields.Int(required=True)
    description = fields.Str(dump_only=True)  # new field for v2