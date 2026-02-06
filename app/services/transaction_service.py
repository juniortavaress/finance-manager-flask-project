from datetime import datetime
from app import database as db
from app.models import Transaction, Contribution


class TransactionService:
    """
    Application service responsible for handling user transactions
    and their side effects (e.g. investment contributions).
    """
        
    @classmethod
    def process_transaction(cls, form_data, user_id):
        """
        Entry point for processing a transaction request.

        This method:
        - Creates a Transaction record
        - Creates a Contribution if the transaction category is 'Investments'
        """

        transaction = cls._add_transaction(user_id, form_data)

        if transaction.category == "Investments":
            cls._process_investiments(user_id, transaction)

        db.session.commit()


    @staticmethod
    def create_transaction(user_id, form_data):
        """
        Builds and persists a Transaction entity.

        This method does NOT commit the session.
        """
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
    def process_post_contribution_updates(user_id, transaction):
        """
        Handles investment-related side effects of a transaction.

        This includes:
        - Determining the brokerage
        - Creating a Contribution entry
        """
        desc_lower = transaction.description.lower()
        if "nu" in desc_lower:
            brokerage_key = "NuInvest"
        elif "xp" in desc_lower:
            brokerage_key = "XPInvest"
        elif "nomad" in desc_lower:
            brokerage_key = "Nomad"
        else:
            return

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

