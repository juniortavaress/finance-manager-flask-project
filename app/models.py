from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from app import database as db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------- User Model --------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    
    transactions = db.relationship('Transaction', back_populates='user', cascade="all, delete-orphan")
    assets = db.relationship('Assets', back_populates='user', cascade="all, delete-orphan")
    trade_statements = db.relationship('PersonalTradeStatement', back_populates='user', cascade="all, delete-orphan")
    dividends = db.relationship('UserDividents', back_populates='user', cascade="all, delete-orphan")
    trade_summaries = db.relationship('UserTradeSummary', back_populates='user', cascade="all, delete-orphan")
    broker_status = db.relationship('BrokerStatus', back_populates='user', cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password = generate_password_hash(password).decode('utf8')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}>'


# -------------------- Transaction Model --------------------
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='transactions')
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # Entrada / Saída
    category = db.Column(db.String(50), nullable=False)
    coin_type = db.Column(db.String(10), nullable=False)  # Entrada / Saída
    value = db.Column(db.Float, nullable=False)

    contributions = db.relationship('Contribution', back_populates='transaction', cascade="all, delete-orphan")
    # incomesAndExpenses = db.relationship('IncomesAndExpenses', back_populates='transaction', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Transaction {self.description}>'



# class IncomesAndExpenses(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
#     date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
#     type = db.Column(db.String(10), nullable=False)
#     category = db.Column(db.String(50), nullable=False)
#     amount = db.Column(db.Float, nullable=False)
#     coin_type = db.Column(db.String(10), nullable=False)

#     transaction = db.relationship('Transaction', back_populates='incomesAndExpenses')

#     def __repr__(self):
#         return f'<EuroEntry {self.type} {self.amount}>'



    

# -------------------- Investment Models --------------------
class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(10), nullable=False)  # Entrada / Saída
    brokerage = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    transaction = db.relationship('Transaction', back_populates='contributions')

    def __repr__(self):
        return f'<Contribution {self.type} {self.amount}>'


class Assets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    current_quantity = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship("User", back_populates="assets")
    def __repr__(self):
        return f'<Asset {self.company} x{self.current_quantity}>'

    
class CompanyDatas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    company = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<CompanyData {self.company} @ {self.current_price}>'
    

class CriptoDatas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    coin = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(100), nullable=False)




# -------------------- Trade and Dividend Models --------------------
class PersonalTradeStatement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    brokerage = db.Column(db.String(50), nullable=False, default="NuInvest")
    investment_type = db.Column(db.String(50), nullable=False, default="Others")
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    statement_number = db.Column(db.String(100), nullable=False)
    operation = db.Column(db.String(100), nullable=False)
    ticker = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    final_value = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="trade_statements")
    def __repr__(self):
        return f'<Trade {self.operation} {self.ticker}>'


class UserDividents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    ticker = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="dividends")
    def __repr__(self):
        return f'<Dividend {self.ticker} {self.value}>'


class UserTradeSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    brokerage = db.Column(db.String(50), nullable=False, default="NuInvest")
    investment_type = db.Column(db.String(50), nullable=False, default="Others")
    date = db.Column(db.Date, nullable=False)
    company = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    avg_price = db.Column(db.Float, nullable=False)
    dividend = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="trade_summaries")
    def __repr__(self):
        return f'<TradeSummary {self.company} x{self.quantity}>'
    

# class OldInvestment(db.Model):
#     __tablename__ = "old_investments"

#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
#     date = db.Column(db.Date, nullable=False)
#     brokerage = db.Column(db.String(120), nullable=False)
#     asset_name = db.Column(db.String(255), nullable=False)
#     investment_type = db.Column(db.String(50), nullable=False, default="Others")
#     # Lucro positivo, prejuízo negativo
#     profit = db.Column(db.Float, nullable=False)

#     user = db.relationship("User", backref=db.backref("old_investments", lazy=True))

#     def __repr__(self):
#         return f"<OldInvestment {self.asset_name} ({self.brokerage}) profit={self.profit}>"
    

class BrokerStatus(db.Model):
    __tablename__ = "broker_status"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    brokerage = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)  # <-- NOVO
    # Total de ativos atuais (quantidade x preço atual)
    invested_value = db.Column(db.Float, nullable=False, default=0.0)
    
    # Total de aportes históricos
    total_contributions = db.Column(db.Float, nullable=False, default=0.0)
    
    # Caixa disponível (livre)
    cash = db.Column(db.Float, nullable=False, default=0.0)
    
    # Lucro/prejuízo acumulado
    profit_loss = db.Column(db.Float, nullable=False, default=0.0)

    user = db.relationship("User", back_populates="broker_status")
    def __repr__(self):
        return (f"<BrokerStatus {self.brokerage} invested={self.invested_value} "
                f"contributions={self.total_contributions} cash={self.cash} profit={self.profit_loss}>")
