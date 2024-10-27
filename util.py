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
    for age in range(current_age+1,retirement_age+1):
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


def roth_ira_calculator(
    current_age, 
    retirement_age, 
    current_balance,
    current_salary,
    annual_contribution_percentage,
    expected_annual_return, 
    annual_salary_growth_rate, 
    annual_tax_rate, max_out
):
    # Constants
    MAX_CONTRIBUTION = 7000  # 2024 max contribution limit
    CATCH_UP_CONTRIBUTION = 1000  # Catch-up contribution for age 50 and over
    CATCH_UP_AGE = 50
    balances = []
    ira_balance = current_balance
    total_contributions = 0

    for age in range(current_age+1, retirement_age+1):
        age_data=dict()
        age_data["age"]=age
        age_data["current_salary"]=round(current_salary*(1+annual_salary_growth_rate)**(age-current_age),2)
        annual_contribution=MAX_CONTRIBUTION
        if max_out and age >= CATCH_UP_AGE:
                annual_contribution += CATCH_UP_CONTRIBUTION
        age_data["employee_contribution"]=round(min(annual_contribution,age_data["current_salary"]*annual_contribution_percentage),2)
        # Update total contributions
        total_contributions += age_data["employee_contribution"]
        age_data["total_contribution"]=total_contributions
        # IRA balance calculation
        age_data["total_gains"]=ira_balance *expected_annual_return*(1 - ((0.1+annual_tax_rate) if retirement_age<59 else 0))
        ira_balance = ira_balance + annual_contribution+age_data["total_gains"]
        age_data["ira_balance"]=ira_balance
        # Append data for the current year
        balances.append(age_data)
    return balances


def trad_ira_calculator(
    starting_balance, 
    annual_contrib, 
    current_age, 
    retire_age, 
    maximize_contrib,
    rate_of_return, 
    current_tax_rate
):

    data = []
    balance = starting_balance
    taxable_balance = 0
    max_annual_contrib = 7000 if current_age < 50 else 8000

    for age in range(current_age+1, retire_age+1):
        # Determine contribution for the year
        contribution = max_annual_contrib if maximize_contrib else annual_contrib
        if age >= 50:
            contribution += 1000  # Catch-up contribution for age 50+

        # Calculate IRA balance after contribution and interest
        balance = (balance + contribution) * (1 + rate_of_return / 100)

        # Taxable account deposit calculation
        tax_savings = contribution * (current_tax_rate / 100)
        taxable_deposit = contribution - tax_savings
        taxable_balance = (taxable_balance + taxable_deposit) * (1 + rate_of_return / 100)

        # Append row data to yearly table
        data.append({
            "age": age,
            "ira_contribution": f"{contribution:.2f}",
            "ira_balance": f"{balance:.2f}",
            "taxable_deposit": f"{taxable_deposit:.2f}",
            "taxable_balance": f"{taxable_balance:.2f}"
        })

    return data   
