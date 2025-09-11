
from flask import Blueprint, request, render_template, redirect, url_for
import json
from app.get_datas import GetDatas
from datetime import datetime
from app import bcrypt, database as db
from app.models import User, Transaction, Contribution, EuroIncomesAndExpenses, RealIncomesAndExpenses
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegistrationForm

main = Blueprint('main', __name__)


# Login and Create Account Routes
@main.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('main.user_page', user_id=user.id)) 
            else:
                form.password.errors.append("Incorrect password")
                form.password.data = ""
        else:
            form.email.errors.append("Email not registered")
    return render_template("login_page.html", page="login", form=form)

@main.route("/create_account", methods=["GET", "POST"], endpoint="create_account")
def create_account():
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data, password=password, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("main.user_page", user_id=user.id))
    else:
        if "email" in form.errors:
            form.name.data = ""
            form.email.data = "" 
            form.password.data = ""
            form.confirm_password.data = ""
        return render_template("login_page.html", page="create_account", form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))


# User Routes
@main.route('/user_page/<int:user_id>')
@login_required
def user_page(user_id):
    if int(user_id) == int(current_user.id):
        transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
        values = GetDatas.get_datas_home_page(user_id)
        return render_template('user_homepage.html', values=values, transactions=transactions, active_page='home')
    return redirect(url_for('main.logout'))


@main.route('/add-transaction', methods=['POST'])
def add_transaction():
    user_id = current_user.id
    category=request.form['category']
    type=request.form['type']
    coin_type=request.form['coin']
    print(coin_type)

    new_transaction = Transaction(
        user_id=current_user.id,
        date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
        description=request.form['description'],
        type=type,
        category=category,
        coin_type=coin_type,
        value=float(request.form['value']))

    try:
        db.session.add(new_transaction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar no banco: {e}")
    
    if category == "Investments":
        new_contribution = Contribution(
            user_id=user_id,
            transaction=new_transaction,
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            description = request.form['description'],
            amount=float(request.form['value']))

        try:
            db.session.add(new_contribution)
            db.session.commit()
            print("deu certo")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar no banco: {e}")

    elif coin_type == "Euro":
        new_euro_information = EuroIncomesAndExpenses(
            user_id=user_id,
            transaction=new_transaction,
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            type=type,
            category=category,
            amount=float(request.form['value']))
        
        try:
            db.session.add(new_euro_information)
            db.session.commit()
            print("deu certo")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar no banco: {e}")

    elif coin_type == "Real":
        new_real_information = RealIncomesAndExpenses(
            user_id=user_id,
            transaction=new_transaction,
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            type=type,
            category=category,
            amount=float(request.form['value']))
        
        try:
            db.session.add(new_real_information)
            db.session.commit()
            print("deu certo")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar no banco: {e}")


    return redirect(url_for('main.user_page', user_id=current_user.id))


@main.route('/delete-transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('main.user_page', user_id=current_user.id))





@main.route('/finance-euro')
@login_required
def finance_euro():    
    user_id = current_user.id
    euro_brl, _ = GetDatas.get_euro_prices()
    months_available, datas_category = GetDatas.load_datas_by_category(current_user.id)
    years_available, geral_datas = GetDatas.load_datas_incomes_and_expenses(EuroIncomesAndExpenses, current_user.id)
    return render_template('finance_euro.html', datas_income_expense=geral_datas, datas_category=datas_category, months=months_available, years=years_available, euro_brl=euro_brl, active_page='finance_euro')


@main.route('/finance-real')
@login_required
def finance_real():
    _, datas_real_euro = GetDatas.get_euro_prices()
    years_available, datas_incomes_and_expenses = GetDatas.load_datas_incomes_and_expenses(RealIncomesAndExpenses, current_user.id)
    

    datas = GetDatas.load_datas_page_real2()
    datas = json.dumps(datas)
    

    return render_template('finance_real.html' , datas=datas, datas_graphs_page_real=datas_incomes_and_expenses, datas_currency_euro_real=datas_real_euro, years_available=years_available, active_page='finance_real')


@main.route('/investments')
@login_required
def investments():
    return render_template('investments.html' , active_page='investments')


@main.route('/tables')
@login_required
def tables():
    return render_template('tables.html' , active_page='tables')

