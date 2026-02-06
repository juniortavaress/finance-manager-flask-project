from app import database as db
from app.models import Assets, PersonalTradeStatement

class AssetsUpdater:
    """
    Handles updates to the Assets table based on user trade activity.

    This updater is designed for real-time usage and should be called
    by orchestration layers (e.g. UpdateDatabases).
    """

    @staticmethod
    def update_from_trades(user_id, trades):
        """
        Entry point for asset synchronization triggered by trade changes.

        Determines which tickers are affected and updates their asset state.
        """
        non_fixed_tickers = list({t.ticker for t in trades if t.investment_type not in ["fixed_income"]})
        
        if non_fixed_tickers:
            AssetsUpdater._update_assets(user_id, non_fixed_tickers)


    @staticmethod
    def _update_assets(user_id, list_tickers):
        """
        Updates asset records for a given user and list of tickers.

        Business rules:
        - If net quantity becomes positive, the asset is created or updated
        - If net quantity returns to zero, the asset is removed
        - The earliest trade date defines the asset start_date

        Parameters:
        - user_id: identifier of the user
        - list_tickers: list of asset tickers affected by trade changes
        """

        for ticker in list_tickers:
            trades = PersonalTradeStatement.query.filter_by(
                user_id=user_id,
                ticker=ticker
            ).all()

            # Calculate net quantity based on buy/sell operations
            current_qty = sum(
                t.quantity if t.operation == "B" else -t.quantity
                for t in trades
            )

            asset = Assets.query.filter_by(
                user_id=user_id,
                company=ticker
            ).first()

            if current_qty > 0:
                first_trade = min(trades, key=lambda t: t.date)

                if not asset:
                    asset = Assets(
                        user_id=user_id,
                        company=ticker,
                        start_date=first_trade.date,
                        current_quantity=current_qty
                    )
                else:
                    # Ensure the earliest trade date is preserved
                    if first_trade.date < asset.start_date:
                        asset.start_date = first_trade.date

                    asset.current_quantity = current_qty

                db.session.add(asset)

            elif current_qty == 0 and asset:
                db.session.delete(asset)

        db.session.commit()
