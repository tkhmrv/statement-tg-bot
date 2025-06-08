from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route("/")
@app.route("/ping")
def ping():
    return "pong", 200

def start_ping_server():
    def run():
        port = int(os.environ.get("PORT", 3000))
        app.run(host="0.0.0.0", port=port)
    Thread(target=run).start()
