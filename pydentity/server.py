from flask import Flask

APP = Flask(__name__)

def run(server_args):
    APP.run(**server_args.__dict__)
