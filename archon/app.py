from flask import Flask
import logging
from flask_sockets import Sockets


def create_app(settings=None):
    app = Flask(__name__)

    if settings:
        app.config.from_object(settings)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    sockets = Sockets(app)

    from archon.models import db
    db.init_app(app)

    from archon.hub import Hub
    from archon.router import Router
    app.hub = Hub()
    app.router = Router()

    @sockets.route('/api/')
    def open_socket(ws):
        connection = app.hub.add(ws)
        while not connection.ws.closed:
            message = connection.ws.receive()
            if message:
                try:
                    connection.handle(db, app.router, message)
                except Exception as e:
                    logging.error(e, exc_info=True)

    return app, db
