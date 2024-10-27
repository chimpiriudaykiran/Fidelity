import random

from flask import Flask, jsonify, request,redirect,url_for, current_app, g
from util import trs_retirement_calculator,retirement_403b_calculator
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy
from urllib.parse import quote_plus
from bson.objectid import ObjectId
from os import environ as env
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

username = quote_plus('udaykiranchimpiri')
password = quote_plus('HackUNT123')

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


@app.route('/api/403b_calculator/', methods=['POST'])
def post_403b_calculator():
    # TODO: Look for data if exists, update, else create
    sandbox_data=request.json
    result=retirement_403b_calculator(sandbox_data["current_age"],
                              sandbox_data["retirement_age"],
                              sandbox_data["current_balance"],
                              sandbox_data["current_salary"],
                              sandbox_data["annual_growth_rate"],
                              sandbox_data["penalty_rate_per_year"],
                              sandbox_data["annual_contribution_percentage"],
                              sandbox_data["employer_match_percentage"],
                              sandbox_data["expected_annual_return"],
                              sandbox_data["annual_salary_growth_rate"],
                              sandbox_data["annual_investment_fee_rate"],
                              sandbox_data["max_out"])
    return jsonify(result)


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


@app.route('/api/chart-data', methods=['GET'])
def chart_data():
    # Generate some example data
    line_data = [random.randint(50, 100) for _ in range(6)]
    bar_data = [random.randint(20, 60) for _ in range(4)]
    pie_data = [random.randint(100, 300) for _ in range(3)]

    # Return data as JSON
    return jsonify({
        "lineChartData": line_data,
        "barChartData": bar_data,
        "pieChartData": pie_data
    })
                 


@app.route('/post_roth_ira_calculate', methods=['POST'])
def post_roth_ira_calculate():
    starting_balance = float(request.form['starting_balance'])
    annual_contribution = float(request.form['annual_contribution'])
    current_age = int(request.form['current_age'])
    retirement_age = int(request.form['retirement_age'])
    rate_of_return = float(request.form['rate_of_return'])
    tax_rate = float(request.form['tax_rate'])
    maximize_contributions = 'maximize_contributions' in request.form

    balances, total_contributions, ira_total_at_retirement, taxable_amount = roth_ira_calculator(
        starting_balance,
        annual_contribution,
        current_age,
        retirement_age,
        rate_of_return,
        tax_rate,
        maximize_contributions
    )

    return jsonify({
        'balances': balances,
        'total_contributions': total_contributions,
        'ira_total_at_retirement': ira_total_at_retirement,
        'taxable_amount': taxable_amount
    })    
