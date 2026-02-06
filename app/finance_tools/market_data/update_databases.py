from app.finance_tools.api_prices import PriceUpdate
from app.finance_tools.market_data.assets_updater import AssetsUpdater
from app.finance_tools.market_data.realtime_updates import RealtimeUpdates


class UpdateDatabases:
    """
    Facade responsible for orchestrating database update operations.

    Its responsibility is to delegate update tasks to specialized modules.
    """
    @staticmethod
    def process_post_trade_updates(user_id, trades):
        """
        Centralized post-trade update pipeline.

        IMPORTANT:
        - This method must be called after trades are persisted.
        - It assumes all trades are already committed to the database.

        Responsibilities:
        - Update assets
        - Fetch market prices when required
        - Update trade summaries
        """
        if not trades:
            return 
        
        AssetsUpdater.update_from_trades(user_id, trades)
        PriceUpdate.update_prices(trades)
        RealtimeUpdates.after_trade_changes(user_id, trades)

        
   