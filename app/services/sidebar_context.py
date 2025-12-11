from flask_login import current_user

def sidebar_context():
    from app import database as db
    from app.models import Transaction, PersonalTradeStatement

    if current_user.is_anonymous:
        return {}

    user_id = current_user.id

    coins_query = (
        db.session.query(Transaction.coin_type)
        .filter(Transaction.user_id == user_id)
        .distinct()
        .all()
    )
    user_coins = [c[0] for c in coins_query]

    has_investments = (
        db.session.query(PersonalTradeStatement)
        .filter_by(user_id=user_id)
        .first()
        is not None
    )

    print(user_coins)
    print(has_investments)
    return {
        "user_coins": user_coins,
        "has_investments": has_investments
    }
