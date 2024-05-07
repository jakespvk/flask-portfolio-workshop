import os
from flask import Flask 

from blogwise.models import Article
from blogwise.views import bp

current_env = os.getenv('FLASK_ENV', 'blogwise.settings.prod')


def create_app(env: str = 'blogwise.settings.prod') -> Flask:
    app = Flask(__name__)
    app.config.from_object(env)
    app.config.from_object(current_env)
    Article.init_db(app.config.get('DB_URI'))

    app.register_blueprint(bp)
    return app
