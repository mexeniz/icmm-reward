#!/usr/bin/env python
from flask import Flask, render_template, request, jsonify, g, abort, send_file
import json
import os
from loguru import logger
from datetime import datetime, timezone, timedelta
from db import RunnerDB

DEFAULT_CONFIG_PATH = "./config.json"
DEFAULT_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

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
config = load_json_config(DEFAULT_CONFIG_PATH)
server_conf = config['server']
db_conf = config['db']
RunnerDB.init(db_conf['mongodbUri'], db_conf['mongodbDBName'])
RunnerDB.set_collection(db_conf['mongodbCollection'])

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
    base_url = config["template"]["baseUrl"]
    base_challenge_cert_url = config["template"]["baseChallengeCertUrl"]
    base_e_reward1_url = config["template"]["baseEReward1Url"]
    base_e_reward2_url = config["template"]["baseEReward2Url"]
    return render_template("index.html", 
        baseUrl=base_url,
        baseChallengeCertUrl=base_challenge_cert_url,
        baseEReward1Url=base_e_reward1_url,
        baseEReward2Url=base_e_reward2_url)

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
    debug_flag = False
    if 'debug' in config['server']:
        debug_flag = config['server']['debug']
    
    try:
        app.run(host=server_conf['bindAddress'], port=server_conf['port'], debug=debug_flag)
    finally:
        # Caught an interrupt or some error.
        RunnerDB.close()

if __name__ == "__main__":
    main()
