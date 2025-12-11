from datetime import date
from collections import defaultdict

from app import database as db
from app.models import UserTradeSummary


class UserInvestmentsFetcher():
    def get_individual_invested_values(user_id: int) -> dict:
        """
        Build the historical investment data per brokerage and company,
        accumulating values over time and keeping only the last record
        of each month. Includes the 'investment_type' field.
        
        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: Nested dictionary with brokerages as keys, each containing
                companies with a list of monthly investment records.
        """
        all_histories = {}

        # Fetch all distinct brokerages for the user
        brokerages = (db.session.query(UserTradeSummary.brokerage).filter(UserTradeSummary.user_id == user_id).distinct().all())

        for brokerage_tuple in brokerages:
            brokerage = brokerage_tuple[0]
            if not brokerage:
                continue

            # Fetch all trade entries for this brokerage
            entries = (
                db.session.query(UserTradeSummary)
                .filter(UserTradeSummary.user_id == user_id, UserTradeSummary.brokerage == brokerage)
                .order_by(UserTradeSummary.date.asc())
                .all()
            )

            # Group entries by company
            companies = defaultdict(list)
            for e in entries:
                companies[e.company].append(e)
            brokerage_data = {}

            # Process each company separately
            for company, company_entries in companies.items():
                # Organize entries by date
                history_by_date = defaultdict(dict)
                for entry in company_entries:
                    history_by_date[entry.date][entry.company] = entry

                accumulated_history = []
                latest_entry = None
                all_dates = sorted(history_by_date.keys())

                # Ensure today's date is included for final state
                if date.today() not in all_dates:
                    all_dates.append(date.today())

                for current_date in all_dates:
                    # Update the latest known state for the company
                    if company in history_by_date[current_date]:
                        latest_entry = history_by_date[current_date][company]

                    if latest_entry:
                        current_price = latest_entry.current_price
                        avg_price = latest_entry.avg_price
                        dividends = latest_entry.dividend
                        quantity = latest_entry.quantity
                        investment_type = latest_entry.investment_type

                        if quantity > 0:
                            profit = (current_price - avg_price) * quantity + dividends
                            profitability = (profit * 100 / (quantity * avg_price)
                                            if avg_price > 0 else 0)

                            accumulated_history.append({
                                "date": current_date,
                                "current_invested": current_price,
                                "quantity": quantity,
                                "invested": avg_price,
                                "dividends": dividends,
                                "profit": profit,
                                "profitability": profitability,
                                "investment_type": investment_type
                            })

                # Keep only the last record of each month
                monthly_entries = defaultdict(list)
                for entry in accumulated_history:
                    key = (entry["date"].year, entry["date"].month)
                    monthly_entries[key].append(entry)

                filtered_history = [
                    max(entries_in_month, key=lambda x: x["date"])
                    for entries_in_month in monthly_entries.values()
                ]
                filtered_history.sort(key=lambda x: x["date"])

                brokerage_data[company] = filtered_history

            all_histories[brokerage] = brokerage_data

        return all_histories


