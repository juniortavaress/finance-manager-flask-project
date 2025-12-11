from datetime import datetime
from app.models import Transaction, Contribution
# IncomesAndExpenses
from app import database as db

def process_transaction(form_data, user_id):
    transaction = _add_transaction(user_id, form_data)

    if transaction.category == "Investments":
        _process_investiments(user_id, transaction)


@staticmethod
def _add_transaction(user_id, form_data):
    transaction = Transaction(
        user_id=user_id,
        date=datetime.strptime(form_data['date'], '%Y-%m-%d').date(),
        description=form_data['description'],
        type=form_data['type'],
        category=form_data['category'],
        coin_type=form_data['coin'],
        value=float(form_data['value'])
    )

    db.session.add(transaction)
    db.session.commit()
    return transaction

@staticmethod
def _process_investiments(user_id, transaction):
    desc_lower = transaction.description.lower()
    if "nu" in desc_lower:
        brokerage_key = "NuInvest"
    elif "xp" in desc_lower:
        brokerage_key = "XPInvest"
    elif "nomad" in desc_lower:
        brokerage_key = "Nomad"
    else:
        brokerage_key = transaction.description

    contribution = Contribution(
        user_id=user_id,
        transaction=transaction,
        date=transaction.date,
        type=transaction.type,
        brokerage=brokerage_key,
        amount=transaction.value
    )
    db.session.add(contribution)
    db.session.commit()

