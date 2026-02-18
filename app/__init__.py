from flask import Flask
from config import config
import os



def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.config.from_mapping(DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'))
    
    os.makedirs(app.instance_path, exist_ok=True)

    from .main import db
    db.init_app(app)

    from .main.views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .main import auth
    app.register_blueprint(auth.bp)

    return app
