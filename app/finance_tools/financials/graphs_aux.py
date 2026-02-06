import json
from collections import defaultdict
from app import database as db
from app.models import UserTradeSummary, BrokerStatus
from app.finance_tools.financials.user_bank import UserBankFetcher


class GraphAux():
    """
    Helper class responsible for fetching, calculating, and formatting 
    investment data for user dashboards and graphs.
    """

    @staticmethod
    def get_current_by_investment_type(user_id: int) -> dict:
        """
        Calculates the current net worth distribution by investment type.
        
        Fetches the latest trade summaries and broker balances to group
        assets into categories like Stocks, REITs, etc., including Cash.
        """
        investment_summary = defaultdict(float)
        usd_rate = json.loads(UserBankFetcher.get_coin_prices("USD"))[-1]["valor_usd_brl"]

        # Retrieve all trade entries for the user to determine current holdings
        entries = (db.session.query(UserTradeSummary).filter_by(user_id=user_id).order_by(UserTradeSummary.date.asc()).all())
        if entries:
            # Logic to filter only the most recent entry for each unique company
            latest_by_company = {}
            for e in entries:
                if (e.company not in latest_by_company or 
                        e.date > latest_by_company[e.company].date):
                    latest_by_company[e.company] = e

            # Sum the current total value (Price * Quantity) per investment category
            for e in latest_by_company.values():
                current_value = (e.quantity * e.current_price)

                if e.brokerage.lower() == "nomad":
                    current_value *= usd_rate

                investment_summary[e.investment_type] += current_value

        # Retrieve broker status entries to account for liquid cash in accounts
        broker_entries = (db.session.query(BrokerStatus)
                          .filter_by(user_id=user_id)
                          .order_by(BrokerStatus.date.desc()).all())
        
        if broker_entries:
            total_cash = 0.0
            processed_brokers = set()
            
            # Since entries are sorted by date DESC, the first occurrence 
            # per broker is the most recent
            for b in broker_entries:
                if b.brokerage not in processed_brokers:
                    cash_value = b.cash
                    
                    # 3. SE O CASH FOR DA NOMAD, CONVERTE TAMBÉM
                    if b.brokerage.lower() == "nomad":
                        cash_value *= usd_rate
                        
                    total_cash += cash_value
                    processed_brokers.add(b.brokerage)
            
            # Include cash as a specific category in the summary if it exists
            if total_cash > 0:
                investment_summary["Cash"] = total_cash
                
        return json.dumps(dict(investment_summary))


    def format_currency(value: float, currency:str = "BRL") -> str:
        """
        Converts a float value into a Brazilian Real (BRL) formatted string.
        Example: 1234.56 -> R$ 1.234,56
        """
        value = float(value or 0)
        # Using a character swap logic to handle BRL thousands and decimal separators
        if currency == "USD":
            return (f"$ {value:,.2f}".replace(",", "X")
                .replace(".", ",").replace("X", "."))

        return (f"R$ {value:,.2f}".replace(",", "X")
                .replace(".", ",").replace("X", "."))
    

    @staticmethod
    def get_historic_by_broker(user_id: int) -> dict:
        """
        Aggregates historical performance data grouped by brokerage.
        
        Returns a JSON-formatted dictionary containing time-series data
        and a 'last_datas' dictionary with the most recent snapshot for cards.
        """
        # Fetch historical records sorted chronologically
        historic = (db.session.query(BrokerStatus)
                    .filter_by(user_id=user_id)
                    .order_by(BrokerStatus.date.asc()).all())

        result = {}
        for record in historic:
            broker_name = record.brokerage
            # Initialize the broker structure if not present
            if broker_name not in result:
                result[broker_name] = {
                    "date": [],
                    "invested": [],
                    "contributions": [],
                    "cash": [],
                    "profit": [],
                }

            currency_type = "USD" if broker_name.lower() == "nomad" else "BRL"

            # Populate time-series lists with formatted data
            result[broker_name]["date"].append(record.date.strftime("%Y-%m-%d"))
            result[broker_name]["invested"].append(GraphAux.format_currency(record.invested_value, currency_type))
            result[broker_name]["contributions"].append(GraphAux.format_currency(record.total_contributions, currency_type))
            result[broker_name]["cash"].append(GraphAux.format_currency(record.cash, currency_type))
            result[broker_name]["profit"].append(GraphAux.format_currency(record.profit_loss, currency_type))

        # Extract the last element from each list to display the current status
        last_datas = {}
        for broker, data in result.items():
            last_datas[broker] = {
                "invested": data["invested"][-1],
                "contributions": data["contributions"][-1],
                "cash": data["cash"][-1],
                "profit": data["profit"][-1],
            }

        return json.dumps(dict(result)), last_datas
