from app.services.upload_service import UploadService
from flask_login import login_required, current_user
from flask import Blueprint, request, redirect, url_for


upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload_notes', methods=['POST'])
@login_required
def upload_notes():
    """
    Handles PDF or document uploads for trade statements.
    Processes multiple files via the UploadService.
    """
    files = request.files.getlist("files")
    UploadService.handle_trades_inputs(current_user.id, "statement", files)
    return redirect(url_for("finance.investments"))


@upload_bp.route('/manual_entry', methods=['POST'])
@login_required
def manual_entry():
    """
    Processes manual trade entry from a form.
    """
    data = request.form
    UploadService.handle_trades_inputs(current_user.id, "manual", data)
    return redirect(url_for('finance.investments'))


@upload_bp.route('/upload_incomes', methods=['POST'])
@login_required
def upload_incomes():
    """
    Processes dividend and income entries.
    """
    dividend_date = request.form.get('dividend_date')
    dividend_ticker = request.form.get('dividend_ticker')
    dividend_amount = request.form.get('dividend_amount')

    UploadService.handle_dividend_input(current_user.id, dividend_date, dividend_ticker, dividend_amount)

    return redirect(url_for('finance.investments'))


