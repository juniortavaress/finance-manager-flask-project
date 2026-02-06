from flask_login import login_required, current_user
from flask import request, jsonify, redirect, url_for, Blueprint, render_template
from app import database as db
from app.models import Transaction, Assets, Contribution, UserTradeSummary
from app.finance_tools.financials import UserInvestmentsFetcher, UserBankFetcher, GraphAux


finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/finance/<currency>')
@login_required
def finance(currency):
    """
    Displays income and expense charts filtered by currency.
    """
    coin_type = currency.upper()
    active_page = f'finance_{currency.lower()}'
    exchange_rate = UserBankFetcher.get_coin_prices(coin=coin_type) if coin_type != "BRL" else {}
    years, income_expense_data = UserBankFetcher.get_monthly_incomes_and_expenses(current_user.id, Transaction, coin_type)
    months, category_data = UserBankFetcher.get_expenses_by_category(current_user.id, Transaction, coin_type)

    return render_template(
        'finance.html',
        datas_income_expense=income_expense_data,
        datas_category=category_data,
        months=months,
        years=years,
        coin_exchange_brl=exchange_rate,
        active_page=active_page,
        currency_code=coin_type
    )


@finance_bp.route('/investments')
@login_required
def investments():    
    """
    Main investment dashboard with cross-brokerage charts.
    """
    trade_brokerages = db.session.query(UserTradeSummary.brokerage).filter_by(user_id=current_user.id).distinct().all()
    active_trade_brokers = [b[0] for b in trade_brokerages]
    brokerages = db.session.query(Contribution.brokerage).filter_by(user_id=current_user.id).distinct().all()
    brokerage_list_cards = [b[0] for b in brokerages]

    if not brokerage_list_cards:
        return redirect(url_for('user.user_homepage', user_id=current_user.id))
    
    historic_by_broker, last_datas = GraphAux.get_historic_by_broker(user_id=current_user.id)
    summary_by_investment_type = GraphAux.get_current_by_investment_type(user_id=current_user.id)
    
    return render_template(
        'investments.html',
        brokerages_cards=brokerage_list_cards, 
        brokerages_menu=active_trade_brokers,
        summary_by_brokerage=historic_by_broker,
        summary_by_investment_type=summary_by_investment_type,
        formatted_summary=last_datas,
        active_page='investments', 
        invest_type='home_invest'
    )


@finance_bp.route('/nuinvest')
@login_required
def nuinvest():
    return render_investment_page("NuInvest", "nuinvest")


@finance_bp.route('/xpinvest')
@login_required
def xpinvest():
    return render_investment_page("XPInvest", "xpinvest")


@finance_bp.route('/nomad')
@login_required
def nomad():
    return render_investment_page("Nomad", "nomad")
    

@finance_bp.route('/user-assets-api')
@login_required
def user_assets_api():
    assets = db.session.query(Assets.company).filter_by(user_id=current_user.id).all()
    assets = [a[0] for a in assets]
    return jsonify({"assets": assets})


def render_investment_page(broker_name, invest_type):
    """
    Generic helper to render detailed investment pages for any broker.
    """
    trade_brokerages = db.session.query(UserTradeSummary.brokerage).filter_by(user_id=current_user.id).distinct().all()
    active_trade_brokers = [b[0] for b in trade_brokerages]
    company_name = request.args.get("name")
    datas_ativos = UserInvestmentsFetcher.get_individual_invested_values(user_id=current_user.id)
    companies = datas_ativos.get(broker_name, {})
    selected_company_name = company_name if company_name in companies else next(iter(companies), None)
    selected_company = companies.get(selected_company_name) if selected_company_name else None

    return render_template(
        'investments.html',
        datas_ativos=datas_ativos,
        brokerages_menu=active_trade_brokers,
        selected_company=selected_company,
        selected_company_name=selected_company_name,
        active_page='investments',
        broker_name=broker_name,
        invest_type=invest_type   
    )

