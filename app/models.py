from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from app import database as db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------- User Model --------------------
class User(db.Model, UserMixin):
    """
    Represents an authenticated application user.
    Handles credential security, session management, and relational integrity
    for financial and investment records.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    
    # Relationships with cascading deletes to maintain database integrity
    transactions = db.relationship('Transaction', back_populates='user', cascade="all, delete-orphan")
    assets = db.relationship('Assets', back_populates='user', cascade="all, delete-orphan")
    trade_statements = db.relationship('PersonalTradeStatement', back_populates='user', cascade="all, delete-orphan")
    dividends = db.relationship('UserDividents', back_populates='user', cascade="all, delete-orphan")
    trade_summaries = db.relationship('UserTradeSummary', back_populates='user', cascade="all, delete-orphan")
    broker_status = db.relationship('BrokerStatus', back_populates='user', cascade="all, delete-orphan")
    user_currencies = db.relationship('UserCurrency', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes and stores the user's password."""
        self.password = generate_password_hash(password).decode('utf8')
    
    def check_password(self, password):
        """Validates a plain-text password against the stored hash."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User: {self.email}>'


# -------------------- Transaction Model --------------------
class Transaction(db.Model):
    """
    Primary financial ledger entry. 
    Tracks cash inflows and outflows for the user's general balance.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False)  
    category = db.Column(db.String(50), nullable=False)
    coin_type = db.Column(db.String(10), nullable=False)  
    value = db.Column(db.Float, nullable=False)

    user = db.relationship('User', back_populates='transactions')
    contributions = db.relationship('Contribution', back_populates='transaction', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Transaction {self.description} | {self.value}>'
    

# -------------------- Investment Models --------------------
class Contribution(db.Model):
    """
    Specific investment capital injections linked to a primary transaction.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(10), nullable=False)  # Entrada / Saída
    brokerage = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    transaction = db.relationship('Transaction', back_populates='contributions')

    def __repr__(self) -> str:
        return f'<Contribution {self.type} {self.amount}>'


class Assets(db.Model):
    """
    Represents current holdings and custody of specific assets per user.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    current_quantity = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship("User", back_populates="assets")

    def __repr__(self) -> str:
        return f'<Asset {self.company} x{self.current_quantity}>'

    
class CompanyDatas(db.Model):
    """
    Market pricing data for stocks and real estate.
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    company = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)

    def __repr__(self) -> str:
        return f'<CompanyData {self.company} @ {self.current_price}>'
    

class CriptoDatas(db.Model):
    """
    Market pricing data for cryptocurrencies.
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    coin = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(100), nullable=False)

    def __repr__(self) -> str:
        return f'<CriptoData {self.company} @ {self.current_price}>'
    

# -------------------- Trade and Dividend Models --------------------
class PersonalTradeStatement(db.Model):
    """
    Detailed execution log for individual buy/sell operations (Brokerage notes).
    """
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
    """
    Tracks historical dividend payments and earnings per user.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    ticker = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="dividends")

    def __repr__(self):
        return f'<Dividend {self.ticker} {self.value}>'


class UserTradeSummary(db.Model):
    """
    Consolidated performance summary for active assets.
    """
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
    

class BrokerStatus(db.Model):
    """
    Snapshot of a user's financial standing within a specific brokerage.
    Includes current equity, liquidity, and historical P&L.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    brokerage = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False) 
    invested_value = db.Column(db.Float, nullable=False, default=0.0)
    total_contributions = db.Column(db.Float, nullable=False, default=0.0)
    cash = db.Column(db.Float, nullable=False, default=0.0)
    profit_loss = db.Column(db.Float, nullable=False, default=0.0)

    user = db.relationship("User", back_populates="broker_status")

    def __repr__(self):
        return (f"<BrokerStatus {self.brokerage} invested={self.invested_value} "
                f"contributions={self.total_contributions} cash={self.cash} profit={self.profit_loss}>")


# -------------------- Currency Models --------------------
class Currency(db.Model):
    """
    Global reference table for supported currencies.
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(5), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    users = db.relationship("UserCurrency", back_populates="currency", cascade="all, delete-orphan")
    def __repr__(self):
        return f'<Currency {self.name}>'


class UserCurrency(db.Model):
    """
    Associative model linking users to their preferred or active currencies.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    currency_id = db.Column(db.Integer, db.ForeignKey("currency.id"), nullable=False)

    user = db.relationship("User", back_populates="user_currencies")
    currency = db.relationship("Currency", back_populates="users")

    __table_args__ = (db.UniqueConstraint("user_id", "currency_id", name="uq_user_currency"),)

    def __repr__(self):
        return f'<User: {self.user_id}\nCurrency: {self.name}>'