"""
server.py
----------------------------------------------------
Flask Server

Author : Ved Rathod
----------------------------------------------------
"""

from flask import Flask
from flask_cors import CORS

from api.routes import api


app = Flask(__name__)

CORS(app)

app.register_blueprint(api)


@app.route("/")
def home():

    return {

        "message": "AI Crowd Surveillance API Running"
    }


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )