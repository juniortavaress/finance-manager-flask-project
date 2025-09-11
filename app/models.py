from app import database as db, login_manager

from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    transactions = db.relationship('Transaction', back_populates='user', cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password = generate_password_hash(password).decode('utf8')
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

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
    type = db.Column(db.String(10), nullable=False)  # Entrada / Saída
    description = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    transaction = db.relationship('Transaction', back_populates='contributions')

    def __repr__(self):
        return f'<Contribution {self.type} {self.amount}>'


class Assets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    company = db.Column(db.String(100), nullable=False)

    
class CompanyDatas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    company = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)

    # def __repr__(self):
    #     return f'<Assets {self.company} ({self.shares} shares)>'
    


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='transactions')

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
