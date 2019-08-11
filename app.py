#!/usr/bin/env python
from flask import Flask, render_template, request, jsonify, g, abort, send_file
import json
import os
from loguru import logger
from datetime import datetime, timezone, timedelta
from db import RunnerDB

DEFAULT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

BIND_ADDRESS= os.environ.get('BIND_ADDESS', 'localhost')
PORT = int(os.environ.get('PORT', 5000))
ENV_MODE = os.environ.get('ENV_MODE', 'production').lower()
# MongoDB Config
MONGODB_URI = os.environ.get('MONGODB_URI')
MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME')
MONGODB_COLLECTION = os.environ.get('MONGODB_COLLECTION')
# UI Config
UI_TEMPLATE_BASE_URL = os.environ.get('UI_TEMPLATE_BASE_URL')
UI_TEMPLATE_BASE_CHALLENGE_CERT_URL = os.environ.get('UI_TEMPLATE_BASE_CHALLENGE_CERT_URL')
UI_TEMPLATE_BASE_E_REWARD1_URL = os.environ.get('UI_TEMPLATE_BASE_E_REWARD1_URL')
UI_TEMPLATE_BASE_E_REWARD2_URL = os.environ.get('UI_TEMPLATE_BASE_E_REWARD2_URL')

print('NUM_WORKER:', os.environ.get('NUM_WORKER'))

template_dir = os.path.abspath("./views")
app = Flask(__name__,  template_folder=template_dir, static_url_path="/static")
# Auto reload if a template file is changed
app.config["TEMPLATES_AUTO_RELOAD"] = True

img_dir = os.path.abspath("./images")
img_type = "png"

def load_json_config(config_path):
    config = None
    with open(config_path) as f:
        config = json.load(f)
    return config

RunnerDB.init(MONGODB_URI, MONGODB_DB_NAME)
RunnerDB.set_collection(MONGODB_COLLECTION)

def create_json_response(data=None, statusCode=0, status=""):
    status = "Success" if statusCode == 0 else status
    resp = {"statuscode": statusCode, "status": status, "data": data}
    return jsonify(resp)

def get_db():
    """Function for get db inside Flask app.
    Must call this funtions inside app context and do not connect database before app run.
    Example:
        with app.app_context():
            db = get_db()
    """
    return RunnerDB
#     if 'db' not in g:
#         # Init database
#         RunnerDB.init(db_conf['mongodbUri'], db_conf['mongodbDBName'])
#         RunnerDB.set_collection(db_conf['mongodbCollection'])
#         g.db = RunnerDB
#     return g.db

# @app.teardown_appcontext 
# def close_connection(exception): 
#     RunnerDB.close()


@app.route("/static/<path:path>")
def send_js(path):
    return send_from_directory("./static", path)

@app.route("/")
def index_get():
    return render_template("index.html", 
        baseUrl=UI_TEMPLATE_BASE_URL,
        baseChallengeCertUrl=UI_TEMPLATE_BASE_CHALLENGE_CERT_URL,
        baseEReward1Url=UI_TEMPLATE_BASE_E_REWARD1_URL,
        baseEReward2Url=UI_TEMPLATE_BASE_E_REWARD2_URL)

def check_user(user, telNumber):
    if user == None or telNumber == None:
        # Not found
        return False
    if not user.tel_4_digit and telNumber == "":
        # Not have tel number data, ignore.
        return True

    if user.tel_4_digit != telNumber:
        # Not found
        return False
    return True

@app.route("/api/runners/<string:bibNumber>", methods=["GET"])
def get_user(bibNumber):
    telNumber = request.args.get("pin")
    if telNumber == None:
        return create_json_response(statusCode=-1, status="Runner not found")

    with app.app_context():
        db = get_db()
        data = db.find_one_runner({'bibNumber': int(bibNumber)})
        if check_user(data, telNumber) == False:
            return create_json_response(statusCode=-1, status="Runner not found")
        
        return create_json_response(statusCode=0, data=data.to_doc())

@app.route("/api/runners/<string:bibNumber>/feedback", methods=["PUT"])
def feedback_user(bibNumber):
    req = request.get_json(silent=True, force=True)
    logger.info('receive feedback for bib={}: {}', bibNumber, req)
    try:
        feedback = req.get('feedback')
        challenge_result = req.get('challengeResult')
        telNumber = req.get('pin')
    except AttributeError:
        return create_json_response(statusCode=-1, status="JSON error")
    
    with app.app_context():
        db = get_db()
        data = db.find_one_runner({'bibNumber': int(bibNumber)})
        if check_user(data, telNumber) == False:
            return create_json_response(statusCode=-1, status="Runner not found")

        db.update_one_runner_feedback({'bibNumber':int(bibNumber)}, feedback, challenge_result)
        data.feedback = feedback    
        return create_json_response(statusCode=0, data=data.to_doc())

@app.route("/img/challengeCert/<string:bibNumber>", methods=["GET"])
def get_cert_img(bibNumber):
    telNumber = request.args.get("pin")
    with app.app_context():
        db = get_db()
        data = db.find_one_runner({'bibNumber': int(bibNumber)})
        if check_user(data, telNumber) == False:
            abort(404)

        file_name = img_dir + "/cert-%s.png" % (bibNumber)
        if not os.path.isfile(file_name):
            abort(404)

        return send_file(file_name, mimetype='image/%s' % img_type)

@app.route("/img/eReward/<string:templateId>/<string:bibNumber>", methods=["GET"])
def get_ereward_img(templateId, bibNumber):
    telNumber = request.args.get("pin")
    with app.app_context():
        db = get_db()
        data = db.find_one_runner({'bibNumber': int(bibNumber)})
        if check_user(data, telNumber) == False:
            abort(404)

def load_json_config(config_path):
    config = None
    with open(config_path) as f:
        config = json.load(f)
    return config

def main():
    debug_flag = ENV_MODE != 'production'

    try:
        app.run(host=BIND_ADDRESS, port=PORT, debug=debug_flag)
    finally:
        # Caught an interrupt or some error.
        RunnerDB.close()

if __name__ == "__main__":
    main()
