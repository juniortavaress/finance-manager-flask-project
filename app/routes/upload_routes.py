from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user

from app import database as db
from app.services import process_trade_statements, process_manually_input

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
def upload_incomes():
    """Importa base de dados de rendimentos (arquivos, pode ter subpastas)."""
    files = request.files.getlist('files')
    for file in files:
        print("Importing income file:", file.filename)
    return redirect(url_for('finance.investments'))


