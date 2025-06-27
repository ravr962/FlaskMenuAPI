import os
from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate 
from models import db
from schemas import ma
# from resources.menu import menu_bp
from resources.order import order_bp
from resources.auth import auth_bp

from dotenv import load_dotenv
import os
from flasgger import Swagger
from flasgger.utils import swag_from
from flask_cors import CORS

from resources.v1.menu import menu_bp_v1
from resources.v2.menu import menu_bp_v2

# Load default .env
load_dotenv()

# Load .env.render if in production
if os.environ.get("FLASK_ENV") == "production":
    load_dotenv(".env.render")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "swagger_ui": True,
    "specs_route": "/docs/",
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
        }
    },
    "security": [{"Bearer": []}]
}

Swagger(app, config=swagger_config)

api = Api(app)

# Build the full path to db.sqlite3 inside instance/
# basedir = os.path.abspath(os.path.dirname(__file__))
# db_path = os.path.join(basedir, 'instance', 'db.sqlite3')
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set DB URI depending on environment
if os.environ.get("FLASK_ENV") == "production":
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'instance', 'db.sqlite3')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

# app.register_blueprint(menu_bp)
app.register_blueprint(order_bp)
app.register_blueprint(auth_bp)

app.register_blueprint(menu_bp_v1, url_prefix="/api/v1")
app.register_blueprint(menu_bp_v2, url_prefix="/api/v2")

# Routes
# api.add_resource(MenuItemListResource, '/menu/')
# api.add_resource(MenuItemResource, '/menu/<int:item_id>')

@app.route("/")
def index():
    return {"message": "FlaskMenuAPI is live!"}

# from flask_migrate import upgrade

# # apply migrations when app starts up
# with app.app_context():
#     upgrade()

# from models.user import User


# with app.app_context():
#     admin_user = User.query.filter_by(username='admin').first()
#     if admin_user:
#         admin_user.is_admin = True
#         db.session.commit()
#         print("✅ is_admin set to True for 'admin'")

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5000))
