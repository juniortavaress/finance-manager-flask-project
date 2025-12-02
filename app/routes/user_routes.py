
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Transaction
from app.finance_tools import UserBankFetcher

from app.finance_tools import CompanyPricesFetcher, UpdateDatabases, ManagerNotesExtractor

user_bp = Blueprint('user', __name__)

@user_bp.route('/user_page/<int:user_id>')
@login_required
def user_homepage(user_id):
    if user_id != current_user.id:
        return redirect(url_for('auth.logout'))

    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    values = UserBankFetcher.get_home_page_data(user_id)

    return render_template(
        'user_homepage.html',
        values=values,
        transactions=transactions,
        active_page='home'
    )

# @user_bp.route('/tables')
# @login_required
# def tables():
#     return render_template('tables.html', active_page='tables')
