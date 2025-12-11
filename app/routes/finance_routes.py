import json
from flask import request
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.finance_tools import UserInvestmentsFetcher, UserBankFetcher, GraphAux
from app.models import Transaction

from flask import redirect, url_for

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/finance/<currency>')
@login_required
def finance(currency):
    # Define o modelo e dados de acordo com a moeda
    if currency == 'euro':
        _, euro_real_data = UserBankFetcher.get_euro_prices()
        coin_type = 'EUR'
        active_page = 'finance_euro'
        exchange_rate = euro_real_data
    elif currency == 'real':
        _, euro_real_data = UserBankFetcher.get_euro_prices()
        coin_type = 'BRL'
        active_page = 'finance_real'
        exchange_rate = euro_real_data

    # model = Transaction.query.filter_by(coin_type=coin_type)
    years, income_expense_data = UserBankFetcher.get_monthly_incomes_and_expenses(current_user.id, Transaction, coin_type)
    months, category_data = UserBankFetcher.get_expenses_by_category(current_user.id, Transaction, coin_type)

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
    historic_by_broker, last_datas = GraphAux.get_historic_by_broker(user_id=current_user.id)
    summary_by_investment_type = GraphAux.get_current_by_investment_type(user_id=current_user.id)
    
    return render_template(
        'investments.html',
        summary_by_brokerage=historic_by_broker,
        summary_by_investment_type=summary_by_investment_type,
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

    company_name = request.args.get("name")

    datas_ativos = UserInvestmentsFetcher.get_individual_invested_values(user_id=current_user.id)

    companies = datas_ativos.get(broker_name, {})

    # Seleciona a empresa específica ou a primeira disponível
    selected_company_name = company_name if company_name in companies else next(iter(companies), None)
    selected_company = companies.get(selected_company_name) if selected_company_name else None


    return render_template(
        'investments.html',
        datas_ativos=datas_ativos,
        selected_company=selected_company,
        selected_company_name=selected_company_name,
        active_page='investments',
        broker_name=broker_name,
        invest_type=invest_type   
    )
