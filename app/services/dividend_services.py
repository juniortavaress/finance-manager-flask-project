from datetime import datetime
from app import database as db
from app.models import UserDividents, UserTradeSummary


class DividendService:
    """
    Service responsible for dividend persistence and propagation
    into daily trade summaries.
    """

    @staticmethod
    def add_dividend(user_id, ticker, dividend_date, dividend_amount):
        """
        Persists a dividend if it does not already exist and
        recomputes accumulated dividends for the asset.

        Parameters:
            user_id (int)
            ticker (str)
            dividend_date (str | date)
            dividend_amount (float)
        """
        dividend_date_obj = datetime.strptime(dividend_date, "%Y-%m-%d").date()
        existing = db.session.query(UserDividents).filter_by(user_id=user_id, ticker=ticker, date=dividend_date_obj, value=dividend_amount).first()


        if existing:
            return existing

        dividend = UserDividents(
            user_id=user_id,
            ticker=ticker,
            date=dividend_date_obj,
            value=float(dividend_amount)
        )
        db.session.add(dividend)
        db.session.commit()

        DividendService._recompute_dividends(user_id, ticker)
        return dividend


    @staticmethod
    def _recompute_dividends(user_id, ticker):
        """
        Recomputes accumulated dividends for all trade summaries
        of a given asset.
        """
        dividends = (
            db.session.query(UserDividents)
            .filter_by(user_id=user_id, ticker=ticker)
            .order_by(UserDividents.date.asc())
            .all()
        )

        summaries = (
            db.session.query(UserTradeSummary)
            .filter_by(user_id=user_id, company=ticker)
            .order_by(UserTradeSummary.date.asc())
            .all()
        )

        total = 0.0
        div_idx = 0

        for summary in summaries:
            while div_idx < len(dividends) and dividends[div_idx].date <= summary.date:
                total += dividends[div_idx].value
                div_idx += 1

            summary.dividend = total

        db.session.commit()
