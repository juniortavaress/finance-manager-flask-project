from datetime import datetime
from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user

from app import database as db
from app.models import Transaction
from app.services.upload_service import UploadService
from app.finance_tools.market_data.update_databases import UpdateDatabases
from app.finance_tools.summaries_updaters.broker_status_rebuilder import BrokerStatusRebuilder


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
    try:
        UploadService.handle_transaction_upload(current_user.id, request.form)

        if request.form['category'] == "Investments":
            target_date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()
            brokerage_key = BrokerStatusRebuilder.get_brokerage_key( request.form['description'])
            BrokerStatusRebuilder.rebuild(user_id=current_user.id, target_date=target_date, brokerage_name=[brokerage_key])

    except:
        db.session.rollback()

    return redirect(url_for("user.user_homepage", user_id=current_user.id))


@transaction_bp.route("/delete-transaction/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    """
    Delete a transaction specified by its ID.

    This function retrieves the transaction from the database,
    deletes it, commits the change, and redirects the user
    to their homepage.
    """
    transaction = Transaction.query.get_or_404(transaction_id)
    user_id = transaction.user_id
    date = transaction.date

    db.session.delete(transaction)
    db.session.commit()
    
    if transaction.category == "Investments":
        brokerage_key = BrokerStatusRebuilder.get_brokerage_key( request.form['description'])
        BrokerStatusRebuilder.rebuild(user_id=user_id, target_date=date, brokerage_name=[brokerage_key])

    return redirect(url_for("user.user_homepage", user_id=current_user.id))
