from datetime import date
from collections import defaultdict
from app import database as db
from app.models import UserTradeSummary


class UserInvestmentsFetcher():
    """
    Service class responsible for retrieving and processing 
    historical investment performance data at a granular level.
    """

    @staticmethod
    def get_individual_invested_values(user_id: int) -> dict:
        """
        Builds historical investment data per brokerage and company.
        
        This method accumulates asset values over time, calculates profit 
        and profitability metrics, and downsamples the data to keep only 
        the last record of each month for performance optimization.
        
        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            dict: A nested structure: {brokerage: {company: [monthly_records]}}.
        """
        all_histories = {}

        # Fetch all unique brokerages where the user has trade history
        brokerages = (db.session.query(UserTradeSummary.brokerage)
                      .filter(UserTradeSummary.user_id == user_id)
                      .distinct().all())

        for brokerage_tuple in brokerages:
            brokerage = brokerage_tuple[0]
            if not brokerage:
                continue

            # Retrieve all trade summaries for this specific brokerage ordered by date
            entries = (
                db.session.query(UserTradeSummary)
                .filter(UserTradeSummary.user_id == user_id, 
                        UserTradeSummary.brokerage == brokerage)
                .order_by(UserTradeSummary.date.asc())
                .all()
            )

            # Group entries by company name for individual asset tracking
            companies = defaultdict(list)
            for e in entries:
                companies[e.company].append(e)
            
            brokerage_data = {}

            # Process the timeline for each company individually
            for company, company_entries in companies.items():
                # Map entries to their specific dates for quick lookup
                history_by_date = defaultdict(dict)
                for entry in company_entries:
                    history_by_date[entry.date][entry.company] = entry

                accumulated_history = []
                latest_entry = None
                all_dates = sorted(history_by_date.keys())

                # Inject today's date to ensure the final state is represented
                if date.today() not in all_dates:
                    all_dates.append(date.today())

                for current_date in all_dates:
                    # Carry forward the last known state if no entry exists for this date
                    if company in history_by_date[current_date]:
                        latest_entry = history_by_date[current_date][company]

                    if latest_entry:
                        current_price = latest_entry.current_price
                        avg_price = latest_entry.avg_price
                        dividends = latest_entry.dividend
                        quantity = latest_entry.quantity
                        investment_type = latest_entry.investment_type

                        # Only process active positions
                        if quantity > 0:
                            # Profit = (Capital Gain/Loss) + Dividends
                            profit = ((current_price - avg_price) * quantity + 
                                      dividends)
                            
                            # Profitability percentage based on average cost
                            profitability = (
                                (profit * 100 / (quantity * avg_price))
                                if avg_price > 0 else 0
                            )

                            accumulated_history.append({
                                "date": current_date,
                                "current_invested": current_price,
                                "quantity": quantity,
                                "invested": avg_price,
                                "dividends": dividends,
                                "profit": profit,
                                "profitability": profitability,
                                "investment_type": investment_type,
                                "price_total_current": current_price*quantity,
                                "price_total_invested": avg_price*quantity
                            })

                # Downsampling: Group daily/transactional records into months
                monthly_entries = defaultdict(list)
                for entry in accumulated_history:
                    key = (entry["date"].year, entry["date"].month)
                    monthly_entries[key].append(entry)

                # Select the latest available record for each month to represent the state
                filtered_history = [
                    max(entries_in_month, key=lambda x: x["date"])
                    for entries_in_month in monthly_entries.values()
                ]
                
                # Ensure the final list is chronologically sorted
                filtered_history.sort(key=lambda x: x["date"])

                brokerage_data[company] = filtered_history

            all_histories[brokerage] = brokerage_data

        return all_histories
    
