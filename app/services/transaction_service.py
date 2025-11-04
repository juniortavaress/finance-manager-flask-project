from datetime import datetime
from app.models import Transaction, Contribution, EuroIncomesAndExpenses, RealIncomesAndExpenses
from app import database as db

def process_transaction(form_data, user_id):
    transaction = Transaction(
        user_id=user_id,
        date=datetime.strptime(form_data['date'], '%Y-%m-%d').date(),
        description=form_data['description'],
        type=form_data['type'],
        category=form_data['category'],
        coin_type=form_data['coin'],
        value=float(form_data['value'])
    )

    try:
        db.session.add(transaction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving transaction: {e}")
        return

    if transaction.category == "Investments":
        contribution = Contribution(
            user_id=user_id,
            transaction=transaction,
            date=transaction.date,
            description=transaction.description,
            amount=transaction.value
        )
        db.session.add(contribution)

    elif transaction.coin_type == "Euro":
        euro_data = EuroIncomesAndExpenses(
            user_id=user_id,
            transaction=transaction,
            date=transaction.date,
            type=transaction.type,
            category=transaction.category,
            amount=transaction.value
        )
        db.session.add(euro_data)

    elif transaction.coin_type == "Real":
        real_data = RealIncomesAndExpenses(
            user_id=user_id,
            transaction=transaction,
            date=transaction.date,
            type=transaction.type,
            category=transaction.category,
            amount=transaction.value
        )
        db.session.add(real_data)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving additional data: {e}")
