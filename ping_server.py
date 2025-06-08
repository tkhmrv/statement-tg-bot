from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

@app.route("/ping")
def ping():
    return "pong"

def start_ping_server():
    from threading import Thread
    def run():
        app.run(host="0.0.0.0", port=3000)
    Thread(target=run).start()
