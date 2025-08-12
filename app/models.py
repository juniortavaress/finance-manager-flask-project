from app import database as db
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    contribution = db.relationship('Contribution', backref='user', lazy=True)
    assets = db.relationship('Assets', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'



# class MonthlyExpenses(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
#     date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
#     category = db.Column(db.String(20), nullable=False)
#     amount = db.Column(db.Float, nullable=False)
    
#     transaction = db.relationship('Transaction', back_populates='monthlyExpenses')

#     def __repr__(self):
#         return f'<Monthly Expenses {self.category} {self.amount}>'


class EuroIncomesAndExpenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)

    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    transaction = db.relationship('Transaction', back_populates='euroIncomesAndExpenses')

    def __repr__(self):
        return f'<EuroIncomesAndExpenses {self.type} {self.amount}>'


class RealIncomesAndExpenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)

    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    transaction = db.relationship('Transaction', back_populates='realIncomesAndExpenses')

    def __repr__(self):
        return f'<RealIncomesAndExpenses {self.type} {self.amount}>'
    

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    transaction = db.relationship('Transaction', back_populates='contributions')

    def __repr__(self):
        return f'<Contribution {self.type} {self.amount}>'


class Assets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    company = db.Column(db.String(100), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    average_price = db.Column(db.Float, nullable=False)
    atual_price = db.Column(db.Float, nullable=False)
    dividends = db.Column(db.Float, default=0.0)
    sales_profit = db.Column(db.Float, default=0.0)
    profit = db.Column(db.Float, default=0.0)
    profitability = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Assets {self.company} ({self.shares} shares)>'
    



class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contributions = db.relationship('Contribution', back_populates='transaction', cascade="all, delete-orphan")
    euroIncomesAndExpenses = db.relationship('EuroIncomesAndExpenses', back_populates='transaction', cascade="all, delete-orphan")
    realIncomesAndExpenses = db.relationship('RealIncomesAndExpenses', back_populates='transaction', cascade="all, delete-orphan")

    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # Entrada / Saída
    category = db.Column(db.String(50), nullable=False)
    coin_type = db.Column(db.String(10), nullable=False)  # Entrada / Saída
    value = db.Column(db.Float, nullable=False)

    
    def __repr__(self):
        return f'<Transaction {self.description}>'
