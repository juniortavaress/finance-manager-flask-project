import json
import calendar

from datetime import date
from collections import defaultdict

from app import database as db
from app.models import UserTradeSummary


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
    
