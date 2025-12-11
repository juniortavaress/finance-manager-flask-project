import os, sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from datetime import datetime
from app import create_app, database as db
from app.models import Contribution, Transaction

app = create_app()

def add_finance_data():
    contribuition_data = [
        {"id": 1, "user_id": 1, "transaction_id": 4, "date": "2025-01-02", "type": "Expense", "brokerage": "NuInvest", "amount": 1500.0},
        {"id": 2, "user_id": 1, "transaction_id": 5, "date": "2025-01-02", "type": "Expense", "brokerage": "XPInvest", "amount": 1500.0},
        {"id": 3, "user_id": 1, "transaction_id": 6, "date": "2025-01-02", "type": "Expense", "brokerage": "Nomad", "amount": 1500.0},
    ]

    transaction_data = [
        {"id": 1, "user_id": 1, "date": "2025-01-04", "description": "Payment", "type": "Income", "category": "Salary", "coin_type": "BRL", "value": 1000.0},
        {"id": 2, "user_id": 1, "date": "2025-01-01", "description": "Payment", "type": "Income", "category": "Salary", "coin_type": "BRL", "value": 5000.0},
        {"id": 3, "user_id": 1, "date": "2025-01-01", "description": "Payment", "type": "Income", "category": "Salary", "coin_type": "EUR", "value": 1500.0},
        {"id": 4, "user_id": 1, "date": "2025-01-02", "description": "NuInvest", "type": "Expense", "category": "Investments", "coin_type": "BRL", "value": 1500.0},
        {"id": 5, "user_id": 1, "date": "2025-01-02", "description": "XpInvest", "type": "Expense", "category": "Investments", "coin_type": "BRL", "value": 1500.0},
        {"id": 6, "user_id": 1, "date": "2025-01-02", "description": "Nomad", "type": "Expense", "category": "Investments", "coin_type": "BRL", "value": 1500.0},
        {"id": 7, "user_id": 1, "date": "2025-12-02", "description": "Kaufland", "type": "Expense", "category": "Food", "coin_type": "EUR", "value": 200.0},
    ]

    # ---------- INSERT CONTRIBUITIONS ----------
    for linha in contribuition_data:
        linha["date"] = datetime.strptime(linha["date"], "%Y-%m-%d").date()
        registro = Contribution(**linha)
        db.session.add(registro)

    # ---------- INSERT TRANSACTION ----------
    for linha in transaction_data:
        linha["date"] = datetime.strptime(linha["date"], "%Y-%m-%d").date()
        registro = Transaction(**linha)
        db.session.add(registro)

    db.session.commit()
    print("Dados inseridos com sucesso!")

if __name__ == "__main__":
    with app.app_context():
        add_finance_data()