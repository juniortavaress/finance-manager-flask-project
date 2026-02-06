
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Transaction
from app.finance_tools.financials import UserBankFetcher


user_bp = Blueprint('user', __name__)


@user_bp.route('/user_page/<int:user_id>')
@login_required
def user_homepage(user_id):
    """
    Renders the user's main dashboard.
    
    Security: Ensures that the logged-in user can only access their own data.
    Data: Fetches current transactions and consolidated bank values.
    """
    if user_id != current_user.id:
        return redirect(url_for('auth.logout'), user_id=current_user.id)

    user_currencies = [uc.currency for uc in current_user.user_currencies]
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    values = UserBankFetcher.get_home_page_data(user_id, user_currencies)

    return render_template(
        'user_homepage.html',
        values=values,
        transactions=transactions,
        active_page='home'
    )



