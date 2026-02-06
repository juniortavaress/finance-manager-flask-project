from sqlalchemy import func
from app import database as db
from datetime import date, timedelta
from app.models import BrokerStatus, User, UserTradeSummary, Contribution, PersonalTradeStatement


class BrokerStatusRebuilder:
    """
    Handles the full rebuild of BrokerStatus records.

    This class contains heavy business logic and MUST NOT be called
    directly by routes or services. Access should happen through
    UpdateDatabases as a facade.
    """

    @staticmethod
    def get_brokerage_key(description):
        """
        Helper to identify the brokerage name based on the transaction description.
        """
        desc_lower = description.lower()
        if "nu" in desc_lower:
            return "NuInvest"
        elif "xp" in desc_lower:
            return "XPInvest"
        elif "nomad" in desc_lower:
            return "Nomad"
        return description  

    @staticmethod
    def rebuild(user_id=None, target_date=None, brokerage_name=None):
        """
        Internal rebuild implementation.

        This method contains the heavy business logic and should
        not be called directly outside this class.
        """

        start_date = target_date if target_date else date.today() - timedelta(days=4)
        users = db.session.query(User).all() if not user_id else [db.session.query(User).get(user_id)]
            
        for user in users:
            if brokerage_name is not None:
                brokerages = brokerage_name[:]   
            else:
                brokerages = (
                    db.session.query(BrokerStatus.brokerage)
                    .filter(BrokerStatus.user_id == user.id)
                    .distinct()
                    .all()
                )
                brokerages = [b[0] for b in brokerages]

            if not brokerages:
                continue

            if target_date:
                db.session.query(BrokerStatus).filter(
                    BrokerStatus.user_id == user.id,
                    BrokerStatus.date >= target_date,
                    BrokerStatus.brokerage.in_(brokerages)
                ).delete(synchronize_session=False)

            for brokerage in brokerages:
                
                current_date = start_date
                while current_date <= date.today():
                    summaries = (db.session.query(UserTradeSummary).filter_by(user_id=user.id, brokerage=brokerage, date=current_date).all())
                    total_contributions = (db.session.query(func.sum(Contribution.amount)).filter(Contribution.user_id==user.id, Contribution.brokerage==brokerage, Contribution.date<=current_date).scalar()) or 0
                    buy_operations = (db.session.query(func.sum(PersonalTradeStatement.final_value)).filter(PersonalTradeStatement.user_id==user.id, PersonalTradeStatement.brokerage==brokerage, PersonalTradeStatement.date<=current_date, PersonalTradeStatement.operation=="B").scalar()) or 0
                    sell_operations = (db.session.query(func.sum(PersonalTradeStatement.final_value)).filter(PersonalTradeStatement.user_id==user.id, PersonalTradeStatement.brokerage==brokerage, PersonalTradeStatement.date<=current_date, PersonalTradeStatement.operation=="S").scalar()) or 0
                    cash = total_contributions + sell_operations - buy_operations
                    
                    invested_value = 0.0
                    for s in summaries:
                        if s.investment_type != "fixed_income":
                            invested_value += s.quantity * s.current_price
                        else:
                            invested_value += s.current_price

                    broker_status = (db.session.query(BrokerStatus).filter_by(user_id=user.id, brokerage=brokerage, date=current_date).first())
                    
                    if not broker_status:
                        broker_status = BrokerStatus(user_id=user.id, brokerage=brokerage, date=current_date)

                    profit = invested_value + cash - total_contributions

                    broker_status.invested_value = round(invested_value, 2)
                    broker_status.total_contributions = round(total_contributions, 2)
                    broker_status.profit_loss = round(profit, 2)
                    broker_status.cash = round(cash, 2)
                    db.session.add(broker_status)
                    current_date += timedelta(days=1)
        db.session.commit()    


