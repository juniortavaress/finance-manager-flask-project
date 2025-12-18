from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user

from app import database as db
from app.services import process_trade_statements, process_manually_input, process_dividends

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload_notes', methods=['POST'])
@login_required
def upload_notes():
    files = request.files.getlist("files")
    process_trade_statements(files, current_user.id)
    return redirect(url_for("finance.investments"))


@upload_bp.route('/manual_entry', methods=['POST'])
def manual_entry():
    data = request.form
    process_manually_input(current_user.id, data)
    return redirect(url_for('finance.investments'))


"""AQUI RENDIMENTOS"""
@upload_bp.route('/upload_incomes', methods=['POST'])
@login_required
def upload_incomes():
    # Para pegar campos do formulário
    dividend_date = request.form.get('dividend_date')
    dividend_ticker = request.form.get('dividend_ticker')
    dividend_amount = request.form.get('dividend_amount')
    print("Data:", dividend_date)
    print("Ativo:", dividend_ticker)
    print("Valor:", dividend_amount)

    process_dividends(current_user.id, dividend_date, dividend_ticker, dividend_amount)

    return redirect(url_for('finance.investments'))


