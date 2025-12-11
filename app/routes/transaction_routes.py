from datetime import datetime
from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user

from app import database as db
from app.models import Transaction
from app.finance_tools import UpdateDatabases
from app.services import process_transaction


transaction_bp = Blueprint("transaction", __name__)


@transaction_bp.route("/add-transaction", methods=["POST"])
@login_required
def add_transaction():
    """
    Handle the addition of a new transaction for the current user.

    This function processes the form data submitted via POST,
    saves the transaction using the `process_transaction` service,
    and redirects the user to their homepage.
    """
    process_transaction(request.form, current_user.id)

    if request.form['category'] == "Investments":
        target_date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()
        desc_lower = request.form['description'].lower()
        if "nu" in desc_lower:
            brokerage_key = "NuInvest"
        elif "xp" in desc_lower:
            brokerage_key = "XPInvest"
        elif "nomad" in desc_lower:
            brokerage_key = "Nomad"
        else:
            brokerage_key = None

        UpdateDatabases.update_broker_status(user_id=current_user.id, target_date=target_date, brokerage=[brokerage_key])
    return redirect(url_for("user.user_homepage", user_id=current_user.id))


@transaction_bp.route("/delete-transaction/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    """
    Delete a transaction specified by its ID.

    This function retrieves the transaction from the database,
    deletes it, commits the change, and redirects the user
    to their homepage.
    
    Args:
        transaction_id (int): The ID of the transaction to delete.
    """

    """aqui vai precisar chamar para atualizar o broker status"""
    transaction = Transaction.query.get_or_404(transaction_id)
    user_id = transaction.user_id
    date = transaction.date

    db.session.delete(transaction)
    db.session.commit()
    
    if transaction.category == "Investments":
        desc_lower = transaction.description.lower()
        if "nu" in desc_lower:
            brokerage_key = "NuInvest"
        elif "xp" in desc_lower:
            brokerage_key = "XPInvest"
        elif "nomad" in desc_lower:
            brokerage_key = "Nomad"
        else:
            brokerage_key = transaction.description

        UpdateDatabases.update_broker_status(user_id=user_id, target_date=date, brokerage=[brokerage_key])

    return redirect(url_for("user.user_homepage", user_id=current_user.id))
