from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import eventlet
import redis
db=SQLAlchemy()
session=Session()
eventlet.monkey_patch()
socketio=SocketIO()
def create_app():
    app=Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    db.init_app(app)
    session.init_app(app)
    socketio.init_app(app, async_mode='eventlet')
    with app.app_context():
        from .home import home
        from .menu import menu
        from .cart import cart
        app.register_blueprint(home.home_bp)
        app.register_blueprint(menu.menu_bp)
        app.register_blueprint(cart.cart_bp)
        db.create_all()
        return app
