def trs_retirement_calculator(
        current_age, current_years_service, expected_retirement_age, 
        current_salary, annual_growth_rate, penalty_rate_per_year=0.06,
        trs_multiplier=0.023):
    # Step 1: Calculate Total Years of Service at Retirement
    total_years_service = current_years_service + (expected_retirement_age - current_age)

    # Step 2: Project Final Salary at Retirement
    final_salary = current_salary * ((1 + annual_growth_rate) ** (expected_retirement_age - current_age))

    # Step 3: Determine if Early Retirement Penalty Applies
    rule_of_80 = expected_retirement_age + total_years_service >= 80
    if rule_of_80 or (expected_retirement_age >= 65 and total_years_service >= 5):
        # No penalty for early retirement
        adjusted_salary = final_salary
    else:
        # Apply penalty based on years below age 65
        years_early = max(0, 65 - expected_retirement_age)
        total_penalty = years_early * penalty_rate_per_year
        adjusted_salary = final_salary * (1 - total_penalty)

    # Step 4: Calculate Annual and Monthly Pension
    annual_pension = total_years_service * trs_multiplier * adjusted_salary
    monthly_pension = annual_pension / 12
    return monthly_pension, total_years_service, final_salary



def retirement_403b_calculator(
    current_age: int,
    retirement_age: int,
    current_balance: float,
    current_salary:float,
    annual_contribution_percentage: float,
    employer_match_percentage: float,
    expected_annual_return: 0.06,
    annual_salary_growth_rate:float=0.0026,
    annual_investment_fee_rate:float = 0.0015,
    max_out:float=True
):
    report_data=[]
    for age in range(age+1,retirement_age+1):
        yearly_data=dict()
        yearly_data["age"]=age
        yearly_data["current_salary"]=current_salary*(1+annual_salary_growth_rate)**(age-current_age)
        yearly_data["employee_contribution"]=min(30500 if (current_age>=50 and max_out) else 23000,yearly_data["current_salary"]*annual_contribution_percentage)
        yearly_data["employer_contribution"]=min(53000,employer_match_percentage*yearly_data["current_salary"])
        yearly_data["total_contribution"]=yearly_data["employee_contribution"]+yearly_data["employee_contribution"]
        yearly_data["current_balance_without_employee_match"]=yearly_data["employee_contribution"]*(1+expected_annual_return-annual_investment_fee_rate)
        yearly_data["current_balance_with_employee_match"]=yearly_data["total_contribution"]*(1+expected_annual_return-annual_investment_fee_rate)
        yearly_data["current_withdraw_amount"]=yearly_data["current_balance_with_employee_match"](1+(0 if age>59 else -0.1))
        report_data.append(yearly_data)
