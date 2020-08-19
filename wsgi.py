from balepos import create_app
from flask_socketio import SocketIO
from balepos import socketio

app=create_app()
if __name__ == "__main__":
    socketio.run(app,port='8080',debug=True)
