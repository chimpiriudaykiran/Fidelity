from flask import Flask, jsonify, request,redirect,url_for
from util import traditional_ira_calculator,trs_retirement_calculator,retirement_403b_calculator,roth_ira_calculator
app = Flask(__name__)



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
    

@app.route('/api/trs_calculator/', methods=['POST'])
def post_trs_calculator():
    # TODO: Look for data if exists, update, else create
    return redirect(url_for("/api/trs_calculator/"))

    
    

@app.route('/api/403b_calculator/', methods=['GET'])
def get_403b_calculator():
    sandbox_data=None
    return jsonify(trs_retirement_calculator(sandbox_data["current_age"],
                              sandbox_data["retirement_age"],
                              sandbox_data["current_403b_balance"],
                              sandbox_data["current_salary"],
                              sandbox_data["annual_growth_rate"],
                              sandbox_data["penalty_rate_per_year"]))
