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

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

# 👆 We're continuing from the steps above. Append this to your server.py file.

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

# 👆 We're continuing from the steps above. Append this to your server.py file.

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
    return render_template("home.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

# def get_db():
#     """
#     Configuration method to return db instance
#     """
#     db = getattr(g, "_database", None)
#
#     if db is None:
#         db = g._database = PyMongo(current_app).db
#
#     return db
#
#
# # Use LocalProxy to read the global db instance with just `db`
# db = LocalProxy(get_db)

db = PyMongo(app).db


@app.route('/select/<string:id>', methods=['GET'])
def select(id):
    # Find the user by ObjectId
    user = db.users.find_one({"_id": ObjectId(id)})

    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
        return jsonify({'message': 'success', 'user': user}), 200
    else:
        return jsonify({'message': 'user not found'}), 404


@app.route('/update_userinfo/<string:user_id>', methods=['PUT'])
def update_userinfo(user_id):
    # Get the JSON data from the request
    data = request.json

    # Ensure that user_id is a valid ObjectId
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

@app.route('/dashboard')
def index():
    # TODO : Get user data about the TRS montly pension
    # TODO: Salary increment data over years.
    # Final Roth IRS Balance
    # Final Roth Tranditional Balance
    # Final 403(b) Balance



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
