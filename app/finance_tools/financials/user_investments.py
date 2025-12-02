import json
import calendar

from datetime import date
from collections import defaultdict

from app import database as db
from app.models import UserTradeSummary, Contribution


class UserInvestmentsFetcher():
    """Class responsible for fetching and calculating user investment data."""

    def get_historic_deposits(user_id: int) -> dict:
        """
        Retrieve and accumulate historical investment deposits for a given user.

        Args:
            user_id (int): ID of the user.
            summary_by_brokerage (dict): Dictionary to accumulate deposit data per brokerage.

        Returns:
            dict: Updated summary_by_brokerage containing accumulated deposits by date.
        """
        summary_by_brokerage = defaultdict(lambda: {"date": [], "deposit": []})

        results = (
            Contribution.query
            .with_entities(Contribution.brokerage, Contribution.amount, Contribution.date)
            .filter(Contribution.user_id == user_id)
            .order_by(Contribution.date.asc())
            .all()
        )

        running_totals = defaultdict(float) 

        for desc, value, date_ in results:
            desc_lower = desc.lower()

            if "nu" in desc_lower:
                key = "NuInvest"
            elif "xp" in desc_lower:
                key = "XPInvest"
            elif "nomad" in desc_lower:
                key = "Nomad"
            else:
                key = desc  

            running_totals[key] += value
            summary_by_brokerage[key]["date"].append(date_)
            summary_by_brokerage[key]["deposit"].append(running_totals[key])
        
        for key, data in summary_by_brokerage.items():
            first_date = data["date"][0] if data["date"] else None
            summary_by_brokerage[key]["first_date"] = first_date

        return summary_by_brokerage







    def get_invested_values(user_id: int, deposits: dict) -> dict:
        """
        Build a month-by-month historical view of investments per brokerage.

        Returns cumulative values, profit, profitability, deposits, and cash.
        """
        entries = (db.session.query(UserTradeSummary).filter_by(user_id=user_id).order_by(UserTradeSummary.date.asc()).all())

        start_date =  min([v.get("first_date") for v in deposits.values() if v.get("first_date") is not None])
        end_date = date.today()
        brokerages = list(deposits.keys())

        # Organize entries by brokerage and company
        data_by_broker = defaultdict(lambda: defaultdict(list))
        for e in entries:
            data_by_broker[e.brokerage][e.company].append(e)

        all_histories = defaultdict(list)
        for brokerage in brokerages:
            pass
            # all_histories[brokerage] = UserInvestmentsFetcher._process_broker_history(user_id, brokerage, data_by_broker[brokerage], deposits.get(brokerage, {}), start_date, end_date)

        all_histories["all"] = UserInvestmentsFetcher._aggregate_all_brokerages(all_histories, brokerages)
        return all_histories


    @staticmethod
    def _month_range(start, end):
        """Generate the first day of each month from start to end inclusive."""
        current = date(start.year, start.month, 1)
        while current <= end:
            yield current
            year = current.year + (current.month // 12)
            month = current.month % 12 + 1
            current = date(year, month, 1)


    # @staticmethod
    # def _process_broker_history(user_id, brokerage, company_data, deposit_data, start_date, end_date):
    #     """Calculate the month-by-month investment history for a single brokerage."""
    #     old_entries = db.session.query(OldInvestment).filter_by(user_id=user_id, brokerage=brokerage).all()
    #     old_profit = sum(e.profit for e in old_entries)

    #     filled_deposits = {}
    #     dep_data = sorted(zip(deposit_data.get("date", []), deposit_data.get("deposit", [])))
    #     last_dep = 0.0

    #     month_history = []
    #     latest_by_company = {}

    #     for month_start in UserInvestmentsFetcher._month_range(start_date, end_date):
    #         month_end_day = calendar.monthrange(month_start.year, month_start.month)[1]
    #         month_end = date(month_start.year, month_start.month, month_end_day)

    #         # Update cumulative deposits for this month
    #         while dep_data and dep_data[0][0] <= month_end:
    #             last_dep = dep_data.pop(0)[1]
    #         filled_deposits[month_start] = last_dep

    #         # Update latest entry per company until end of month
    #         for company, entries_list in company_data.items():
    #             entries_sorted = sorted(entries_list, key=lambda x: x.date)
    #             last_entry = None
    #             for e in entries_sorted:
    #                 if e.date <= month_end:
    #                     last_entry = e
    #                 else:
    #                     break
    #             if last_entry:
    #                 latest_by_company[company] = last_entry

    #         # Compute invested, current value, dividends, profit, cash, profitability
    #         invested = sum(e.quantity * e.avg_price for e in latest_by_company.values())
    #         current_invested = sum(e.quantity * e.current_price for e in latest_by_company.values())
    #         dividends_total = sum(e.dividend for e in latest_by_company.values())
    #         profit = sum((e.quantity * (e.current_price - e.avg_price) + e.dividend) for e in latest_by_company.values())
    #         deposit = filled_deposits.get(month_start, 0)
    #         cash = deposit - invested + dividends_total + old_profit
    #         profitability = profit / invested if invested > 0 else 0

    #         month_history.append({
    #             "month": month_start.strftime("%Y-%m"),
    #             "invested": invested,
    #             "current_invested": current_invested,
    #             "profit": profit,
    #             "profitability": profitability,
    #             "deposit": deposit,
    #             "cash": cash,
    #             "dividends": dividends_total
    #         })

    #     return month_history
    
    @staticmethod
    def _aggregate_all_brokerages(all_histories, brokerages):
        """Aggregate month-by-month data across all brokerages."""
        all_months = sorted({h["month"] for hist in all_histories.values() for h in hist})
        aggregate_history = []

        for month in all_months:
            invested_total = sum(next((h["invested"] for h in all_histories[b] if h["month"] == month), 0) for b in brokerages)
            current_invested_total = sum(next((h["current_invested"] for h in all_histories[b] if h["month"] == month), 0) for b in brokerages)
            profit_total = sum(next((h["profit"] for h in all_histories[b] if h["month"] == month), 0) for b in brokerages)
            deposit_total = sum(next((h["deposit"] for h in all_histories[b] if h["month"] == month), 0) for b in brokerages)
            cash_total = sum(next((h["cash"] for h in all_histories[b] if h["month"] == month), 0) for b in brokerages)
            dividends_total = sum(next((h["dividends"] for h in all_histories[b] if h["month"] == month), 0) for b in brokerages)
            profitability = profit_total / invested_total if invested_total > 0 else 0

            aggregate_history.append({
                "month": month,
                "invested": invested_total,
                "current_invested": current_invested_total,
                "profit": profit_total,
                "profitability": profitability,
                "deposit": deposit_total,
                "cash": cash_total,
                "dividends": dividends_total
            })
        return aggregate_history


    @staticmethod
    def get_current_values(summary_by_brokerage: dict) -> dict:
        """Return the latest investment values per brokerage formatted as currency strings."""
        def format_currency(value: float) -> str:
            return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        latest_values = {}
        for brokerage, history in summary_by_brokerage.items():
            if not history:
                continue

            last_entry = history[-1]
            latest_values[brokerage] = {
                "date": last_entry.get("month", last_entry.get("date")),
                "current_invested": format_currency(last_entry.get("current_invested", 0.0)),
                "invested": format_currency(last_entry.get("invested", 0.0)),
                "dividends": format_currency(last_entry.get("dividends", 0.0)),
                "deposit": format_currency(last_entry.get("deposit", 0.0)),
                "cash": format_currency(last_entry.get("cash", 0.0)),
                "profit": format_currency(last_entry.get("profit", 0.0))
            }
        return latest_values


    @staticmethod
    def get_history_values(user_id) -> None:
        """Fetch, process, and return historical investment data per brokerage."""
        summary_by_brokerage = UserInvestmentsFetcher.get_historic_deposits(user_id)
        # UserInvestmentsFetcher.update_broker_status(user_id, summary_by_brokerage)

        if summary_by_brokerage:
            summary_by_brokerage = UserInvestmentsFetcher.get_invested_values(user_id, summary_by_brokerage)
            
            
            
            last_datas = UserInvestmentsFetcher.get_current_values(summary_by_brokerage)       
            return last_datas, json.dumps(summary_by_brokerage)
    
        return None, None
    
    
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


