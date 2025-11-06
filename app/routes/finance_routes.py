import json
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.finance_tools import UserInvestmentsFetcher, UserBankFetcher
from app.models import EuroIncomesAndExpenses, RealIncomesAndExpenses

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/finance/<currency>')
@login_required
def finance(currency):
    # Define o modelo e dados de acordo com a moeda
    if currency == 'euro':
        euro_brl, _ = UserBankFetcher.get_euro_prices()
        # euro_brl = {"valor_eur_brl": 5.23}
        model = EuroIncomesAndExpenses
        active_page = 'finance_euro'
        exchange_rate = euro_brl
    elif currency == 'real':
        _, euro_real_data = UserBankFetcher.get_euro_prices()
        model = RealIncomesAndExpenses
        active_page = 'finance_real'
        exchange_rate = euro_real_data

    # Dados financeiros do usuário
    years, income_expense_data = UserBankFetcher.get_monthly_incomes_and_expenses(model=model, user_id=current_user.id)
    months, category_data = UserBankFetcher.get_expenses_by_category(current_user.id, model)

    # Renderiza o template
    return render_template(
        'finance.html',
        datas_income_expense=income_expense_data,
        datas_category=category_data,
        months=months,
        years=years,
        euro_brl=exchange_rate,
        active_page=active_page
    )


@finance_bp.route('/investments')
@login_required
def investments():     
    last_datas, summary_by_brokerage = UserInvestmentsFetcher.get_history_values(user_id=current_user.id)
    summary_by_investment_type = UserInvestmentsFetcher.get_current_by_investment_type(user_id=current_user.id)
    
    datas_json = json.dumps(summary_by_brokerage)
    assets_json = json.dumps(summary_by_investment_type)
    
    return render_template(
        'investments.html',
        datas=datas_json,
        assets=assets_json,
        formatted_summary=last_datas,
        active_page='investments', 
        invest_type='home_invest'
    )

@finance_bp.route('/nuinvest')
@login_required
def nuinvest():
    return render_investment_page("NuInvest", "nu_invest")

@finance_bp.route('/xpinvest')
@login_required
def xpinvest():
    return render_investment_page("XPInvest", "xpinvest")

@finance_bp.route('/nomad')
@login_required
def nomad():
    return render_investment_page("Nomad", "nomad")
    

def render_investment_page(broker_name: str, invest_type: str):
    from flask import request
    company_name = request.args.get("name")

    datas_ativos = UserInvestmentsFetcher.get_individual_invested_values(user_id=current_user.id)
    _, summary_by_brokerage = UserInvestmentsFetcher.get_history_values(user_id=current_user.id)

    broker_data = summary_by_brokerage.get(broker_name, {})
    datas_json = json.dumps({broker_name: broker_data})

    selected_company = None
    selected_company_name = None

    if company_name and company_name in datas_ativos.get(broker_name, {}):
        selected_company = datas_ativos[broker_name][company_name]
        selected_company_name = company_name

    if not selected_company:
        companies = datas_ativos.get(broker_name, {})
        if companies:
            first_item = sorted(companies.items())[0]
            selected_company_name = first_item[0]
            selected_company = companies[selected_company_name]

    return render_template(
        'investments.html',
        datas_ativos=datas_ativos,
        datas=datas_json,
        selected_company=selected_company,
        selected_company_name=selected_company_name,
        active_page='investments',
        broker_name=broker_name,
        invest_type=invest_type   # <- envia exatamente o valor esperado
    )
