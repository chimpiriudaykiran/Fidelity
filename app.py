import os
import random

from flask import Flask, jsonify, request,redirect,url_for, current_app, g
from util import trs_retirement_calculator,retirement_403b_calculator, roth_ira_calculator, trad_ira_calculator
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy
from urllib.parse import quote_plus
from bson.objectid import ObjectId
from os import environ as env
import json
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

username = quote_plus(env.get("MONGO_USERNAME"))
password = quote_plus(env.get("MONGO_PASSWORD"))

uri = f"mongodb+srv://{username}:{password}@cluster0.omdcv.mongodb.net/db-fidelity?retryWrites=true&w=majority"

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
app.config['MONGO_URI'] = uri

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

def serialize_objectid(data):
    if isinstance(data, dict):
        return {k: serialize_objectid(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_objectid(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    return data

@app.route("/login")
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("callback", _external=True)
        )

# 👆 We're continuing from the steps above. Append this to your server.py file.

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

# 👆 We're continuing from the steps above. Append this to your server.py file.

@app.route("/")
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template("home.html", session=session.get('user'), indent=4)


db = PyMongo(app).db

@app.route('/403b_calculator')
def index():
    return render_template('403b.html')

@app.route('/ira_roth_calculator')
def index2():
    return render_template('ira_roth.html')

@app.route('/ira_trad_calculator')
def index4():
    return render_template('ira_trad.html')

@app.route('/get_user/<string:id>', methods=['GET'])
def select(id):
    # Find the user by ObjectId
    user = db.users.find_one({"_id": ObjectId(id)})

    if user:
        user = serialize_objectid(user)  # Convert ObjectId to string for JSON serialization
        return jsonify({'message': 'success', 'user': user}), 200
    else:
        return jsonify({'message': 'user not found'}), 404


@app.route('/update_userinfo/', methods=['PUT'])
def update_userinfo():
    user_id = session.get("user")['userinfo']['sub'].split('|')[1]
    data = request.json

    if not ObjectId.is_valid(user_id):
        return jsonify({"message": "Invalid user ID format"}), 400

    # Check if the user exists in the users collection
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Attempt to update userinfo in the userinfo collection
    result = db.users_info.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": data}
    )

    if result.matched_count > 0:
        return jsonify({"message": "User information updated successfully"}), 200
    else:
        # If no userinfo was found, create a new one
        data['user_id'] = ObjectId(user_id)  # Reference to the user
        db.users_info.insert_one(data)
        return jsonify({"message": "User information created successfully"}), 201

@app.route('/get_userinfo/', methods=['GET'])
def get_userinfo():

    user_id = session.get("user")['userinfo']['sub'].split('|')[1]

    if not user_id:
        return jsonify({"error": "User not logged in."}), 401

    try:
        # Fetch user information based on user_id
        user_info = db.users_info.find_one({"user_id": ObjectId(user_id)})

        if user_info:
            user_info = serialize_objectid(user_info)
            return jsonify({'message': 'success', 'user_info': user_info}), 200
        else:
            return jsonify({"error": "User not found."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

#functional End Points
@app.route('/api/trs_calculator/', methods=['GET'])
def get_trs_calculator():
    # FETCH data from db, if doesn't exists, redirect to data creation page
    sandbox_data=None
    return jsonify(trs_retirement_calculator(sandbox_data["current_age"],
                              sandbox_data["current_years_service"],
                              sandbox_data["retirement_age"],
                              sandbox_data["current_salary"],
                              sandbox_data["annual_growth_rate"],
                              sandbox_data["penalty_rate_per_year"]))


# @app.route('/api/403b_calculator/', methods=['POST'])
# def post_403b_calculator():
#     # TODO: Look for data if exists, update, else create
#     sandbox_data=request.json
#     result=retirement_403b_calculator(sandbox_data["current_age"],
#                               sandbox_data["retirement_age"],
#                               sandbox_data["current_balance"],
#                               sandbox_data["current_salary"],
#                               sandbox_data["annual_growth_rate"],
#                               sandbox_data["penalty_rate_per_year"],
#                               sandbox_data["annual_contribution_percentage"],
#                               sandbox_data["employer_match_percentage"],
#                               sandbox_data["expected_annual_return"],
#                               sandbox_data["annual_salary_growth_rate"],
#                               sandbox_data["annual_investment_fee_rate"],
#                               sandbox_data["max_out"])
#     return jsonify(result)

@app.route('/api/403b_calculator/', methods=['POST'])
def post_403b_calculator():
    # TODO: Look for data if exists, update, else create
    sandbox_data=request.json
    result=retirement_403b_calculator(sandbox_data["current_age"],
                              sandbox_data["retirement_age"],
                              sandbox_data["current_balance"],
                              sandbox_data["current_salary"],
                              sandbox_data["annual_contribution_percentage"],
                              sandbox_data["employer_match_percentage"],
                              sandbox_data["expected_annual_return"],
                              sandbox_data["annual_salary_growth_rate"],
                              sandbox_data["annual_investment_fee_rate"],
                              sandbox_data["max_out"])
    return jsonify(result)

@app.route('/api/ira_roth_calculator/', methods=['POST'])
def get_irs_roth_calculator():
    sandbox_data=request.json
    result=roth_ira_calculator(sandbox_data["current_age"],
                              sandbox_data["retirement_age"],
                              sandbox_data["current_balance"],
                              sandbox_data["current_salary"],
                              sandbox_data["annual_contribution_percentage"],
                              sandbox_data["expected_annual_return"],
                              sandbox_data["annual_salary_growth_rate"],
                              sandbox_data["annual_tax_rate"],
                              sandbox_data["max_out"])
    return jsonify(result)

@app.route('/api/ira_trad_calculator/', methods=['POST'])
def get_irs_trad_calculator():
    sandbox_data=request.json
    result=trad_ira_calculator(sandbox_data["current_age"],
                              sandbox_data["retirement_age"],
                              sandbox_data["current_balance"],
                              sandbox_data["current_salary"],
                              sandbox_data["annual_contribution_percentage"],
                              sandbox_data["expected_annual_return"],
                              sandbox_data["annual_salary_growth_rate"],
                              sandbox_data["annual_tax_rate"],
                              sandbox_data["max_out"])
    return jsonify(result)

@app.route('/api/403b_calculator/', methods=['GET'])
def get_403b_calculator():
    user_id = session.get("user")['userinfo']['sub'].split('|')[1]
    user_data = db.users_info.find_one({"user_id": ObjectId(user_id)})
    if not user_data:
        return redirect(url_for("/ira_trad_calculator"))
    personal_data=user_data["personal_info"]
    b403_data=user_data["b403"]
    sandbox_data={"current_age":personal_data["current_age"],
                  "retirement_age":personal_data["retirement_age"],
                  "current_salary":personal_data["current_salary"],
                  "annual_salary_growth_rate":personal_data["annual_salary_growth_rate"],
                  "current_balance":b403_data["current_balance"],
                  "annual_contribution_percentage":b403_data["annual_contribution_percentage"],
                  "expected_annual_return":b403_data["expected_annual_return"],
                  "annual_investment_fee_rate":b403_data["annual_investment_fee_rate"],
                  "employer_match_percentage":b403_data["employer_match_percentage"],
                  "max_out":b403_data["max_out"]}
    result=retirement_403b_calculator(sandbox_data["current_age"],
                              sandbox_data["retirement_age"],
                              sandbox_data["current_balance"],
                              sandbox_data["current_salary"],
                              sandbox_data["annual_contribution_percentage"],
                              sandbox_data["employer_match_percentage"],
                              sandbox_data["expected_annual_return"],
                              sandbox_data["annual_salary_growth_rate"],
                              sandbox_data["annual_investment_fee_rate"],
                              sandbox_data["max_out"])
    return jsonify(result)

@app.route('/api/ira_trad_calculator/', methods=['GET'])
def get_data_irs_trad_calculator():
    user_id = session.get("user")['userinfo']['sub'].split('|')[1]
    user_data = db.users_info.find_one({"user_id": ObjectId(user_id)})
    if not user_data:
        return redirect(url_for("/ira_trad_calculator"))
    personal_data=user_data["personal_info"]
    ira_data=user_data["ira_trad"]
    sandbox_data={"current_age":personal_data["current_age"],
                  "retirement_age":personal_data["retirement_age"],
                  "current_salary":personal_data["current_salary"],
                  "annual_salary_growth_rate":personal_data["annual_salary_growth_rate"],
                  "current_balance":ira_data["current_balance"],
                  "annual_contribution_percentage":ira_data["annual_contribution_percentage"],
                  "expected_annual_return":ira_data["expected_annual_return"],
                  "annual_tax_rate":ira_data["annual_tax_rate"],
                  "max_out":ira_data["max_out"]}
    result=trad_ira_calculator(sandbox_data["current_age"],
                              sandbox_data["retirement_age"],
                              sandbox_data["current_balance"],
                              sandbox_data["current_salary"],
                              sandbox_data["annual_contribution_percentage"],
                              sandbox_data["expected_annual_return"],
                              sandbox_data["annual_salary_growth_rate"],
                              sandbox_data["annual_tax_rate"],
                              sandbox_data["max_out"])
    return jsonify(result)

@app.route('/api/ira_roth_calculator/', methods=['GET'])
def get_data_irs_roth_calculator():
    user_id = session.get("user")['userinfo']['sub'].split('|')[1]
    user_data = db.users_info.find_one({"user_id": ObjectId(user_id)})
    if not user_data:
        return redirect(url_for("/ira_roth_calculator"))
    personal_data=user_data["personal_info"]
    ira_data=user_data["ira_roth"]
    sandbox_data={"current_age":personal_data["current_age"],
                  "retirement_age":personal_data["retirement_age"],
                  "current_salary":personal_data["current_salary"],
                  "annual_salary_growth_rate":personal_data["annual_salary_growth_rate"],
                  "current_balance":ira_data["current_balance"],
                  "annual_contribution_percentage":ira_data["annual_contribution_percentage"],
                  "expected_annual_return":ira_data["expected_annual_return"],
                  "annual_tax_rate":ira_data["annual_tax_rate"],
                  "max_out":ira_data["max_out"]}
    result=roth_ira_calculator(sandbox_data["current_age"],
                              sandbox_data["retirement_age"],
                              sandbox_data["current_balance"],
                              sandbox_data["current_salary"],
                              sandbox_data["annual_contribution_percentage"],
                              sandbox_data["expected_annual_return"],
                              sandbox_data["annual_salary_growth_rate"],
                              sandbox_data["annual_tax_rate"],
                              sandbox_data["max_out"])
    return jsonify(result)


