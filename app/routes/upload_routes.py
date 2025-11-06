from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user
from app.services import process_trade_statements, process_manually_input
from app.models import PersonalTradeStatement
from app import database as db
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload_notes', methods=['POST'])
@login_required
def upload_notes():
    data_type = request.form.get("data_type")
    files = request.files.getlist("files")

    if data_type == "trade_statements":
        process_trade_statements(files, current_user.id)

    return redirect(url_for("finance.investments"))


# NOVO
@upload_bp.route('/upload_incomes', methods=['POST'])
def upload_incomes():
    """Importa base de dados de rendimentos (arquivos, pode ter subpastas)."""
    files = request.files.getlist('files')
    # exemplo básico
    for file in files:
        print("Importing income file:", file.filename)
        # processar e salvar no banco

    return redirect(url_for('finance.investments'))



@upload_bp.route('/manual_entry', methods=['POST'])
def manual_entry():
    """Cria um registro manual de investimento."""
    data = request.form
    process_manually_input(current_user.id, data)

    return redirect(url_for('finance.investments'))