from datetime import date, timedelta
from app.finance_tools.summaries_updaters.broker_status_rebuilder import BrokerStatusRebuilder
from app.finance_tools.summaries_updaters.update_equity_investiments import UpdateEquityDatabases
from app.finance_tools.summaries_updaters.update_fixed_income_investments import UpdateFixedIncomesDatabases


class RealtimeUpdates:
    """
    Handles real-time update operations triggered by user actions
    such as adding, deleting or importing trades.
    """
           
    @staticmethod
    def after_trade_changes(user_id, trades):
        """
        Executes all required updates after trade-related changes.

        This method is intended to be lightweight and event-driven.
        """
        if not trades:
            return

        brokerages = list({t.brokerage for t in trades})
        oldest_date = min(t.date for t in trades)

        for trade in trades:
            if trade.investment_type == "fixed_income":
                UpdateFixedIncomesDatabases.atualize_fixed_income(user_id, trade)
            else:
                UpdateEquityDatabases.atualize_equities_trades(user_id, trade)

        BrokerStatusRebuilder.rebuild(user_id=user_id, target_date=oldest_date, brokerage_name=brokerages)


    @staticmethod
    def daily_summary_changes():
        """
        Executes daily update routines for all users.

        Intended to be called by a scheduler.
        """
        UpdateFixedIncomesDatabases.update_fixed_income_daily()
        # If necessary define start_date to fix the summary
        start_date=(date.today() - timedelta(days=3))
        UpdateEquityDatabases.update_equities_daily()
        # If necessary define target date to fix the broker status
        target_date=(date.today() - timedelta(days=4))
        BrokerStatusRebuilder.rebuild()
