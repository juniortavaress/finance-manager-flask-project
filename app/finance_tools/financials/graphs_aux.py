import json
import calendar

from datetime import date
from collections import defaultdict

from app import database as db
from app.models import UserTradeSummary, BrokerStatus


class GraphAux():
    """Class responsible for fetching and calculating user investment data."""
    @staticmethod
    def get_current_by_investment_type(user_id: int) -> dict:
        """Return current investment values grouped by investment type."""
        entries = (db.session.query(UserTradeSummary).filter_by(user_id=user_id).order_by(UserTradeSummary.date.asc()).all())
        if not entries:
            return {}

        latest_by_company = {}
        for e in entries:
            if e.company not in latest_by_company or e.date > latest_by_company[e.company].date:
                latest_by_company[e.company] = e

        investment_summary = defaultdict(float)
        for e in latest_by_company.values():
            investment_summary[e.investment_type] += e.quantity * e.current_price
        return json.dumps(dict(investment_summary))
    

    def format_currency(value: float) -> str:
        value = float(value or 0)
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @staticmethod
    def get_historic_by_broker(user_id: int) -> dict:
        historic = (db.session.query(BrokerStatus).filter_by(user_id=user_id).order_by(BrokerStatus.date.asc()).all())

        result = {}
        for record in historic:
            broker_name = record.brokerage
            if broker_name not in result:
                result[broker_name] = {
                    "date": [],
                    "invested": [],
                    "contributions": [],
                    "cash": [],
                    "profit": [],
                }

            result[broker_name]["date"].append(record.date.strftime("%Y-%m-%d"))
            result[broker_name]["invested"].append(GraphAux.format_currency(record.invested_value))
            result[broker_name]["contributions"].append(GraphAux.format_currency(record.total_contributions))
            result[broker_name]["cash"].append(GraphAux.format_currency(record.cash))
            result[broker_name]["profit"].append(GraphAux.format_currency(record.profit_loss))

        last_datas = {}
        for broker, data in result.items():
            last_datas[broker] = {
                "invested": data["invested"][-1],
                "contributions": data["contributions"][-1],
                "cash": data["cash"][-1],
                "profit": data["profit"][-1],
            }


        return json.dumps(dict(result)), last_datas