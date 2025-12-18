
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Transaction, Currency
from app.finance_tools import UserBankFetcher

from app.finance_tools import CompanyPricesFetcher, UpdateDatabases, ManagerNotesExtractor

user_bp = Blueprint('user', __name__)

@user_bp.route('/user_page/<int:user_id>')
@login_required
def user_homepage(user_id):
    if user_id != current_user.id:
        return redirect(url_for('auth.logout'))

    user_currencies = [uc.currency for uc in current_user.user_currencies]
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    values = UserBankFetcher.get_home_page_data(user_id, user_currencies)
    

    print(user_currencies)
    return render_template(
        'user_homepage.html',
        values=values,
        transactions=transactions,
        active_page='home'
    )

@user_bp.route("/setup_wallet", methods=["POST"])
@login_required
def setup_wallet():
    # Pega os dados do form
    currency_names = request.form.getlist("currency_name[]")
    currency_icons = request.form.getlist("currency_icon[]")
    investments_enabled = request.form.get("investments_enabled") == "on"

    # Aqui você processa e salva no banco de dados
    print(currency_names, currency_icons, investments_enabled)

    # Redireciona para a homepage ou outra página
    return redirect(url_for("user.user_homepage", user_id=current_user.id))

# @user_bp.route('/tables')
# @login_required
# def tables():
#     return render_template('tables.html', active_page='tables')
