
from flask import Blueprint, request, render_template, redirect, url_for
import pandas as pd
import json
from app.get_datas import getDatas

from datetime import datetime
from app import database as db
from app.models import Transaction, Contribution, EuroIncomesAndExpenses, RealIncomesAndExpenses

main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    values = getDatas.get_datas_home_page()
    return render_template('homepage.html', values=values, transactions=transactions, active_page='home')


@main.route('/add-transaction', methods=['POST'])
def add_transaction():
    user_id = 1
    category=request.form['category']
    type=request.form['type']
    coin_type=request.form['coin']
    print(coin_type)

    new_transaction = Transaction(
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


    return redirect(url_for('main.homepage'))

@main.route('/delete-transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):

    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    
    db.session.commit()
    return redirect(url_for('main.homepage'))


@main.route('/finance-euro')
def finance_euro():    
    euro_real_relation, _ = getDatas.gerar_dados_eur_brl_simulados()
    datas_incomes_and_expenses = getDatas.load_datas_incomes_and_expenses_euro()
    datas_json_incomes_and_expenses = json.dumps(datas_incomes_and_expenses)
    months_graph03, datas_by_category = getDatas.load_datas_by_category()
    datas_json_by_category = json.dumps(datas_by_category)
    return render_template('finance_euro.html', datas_graphs_01_02=datas_json_incomes_and_expenses, datas_graph_03=datas_json_by_category, months_graph03=months_graph03, cotacao_euro_brl=euro_real_relation, active_page='finance_euro')


@main.route('/finance-real')
def finance_real():
    _, datas_real_euro = getDatas.gerar_dados_eur_brl_simulados()
    datas_incomes_and_expenses = getDatas.load_datas_page_real()
    datas_incomes_and_expenses = json.dumps(datas_incomes_and_expenses)
    # print('\n\n\n', datas_incomes_and_expenses)
    return render_template('finance_real.html' , datas_graphs_page_real=datas_incomes_and_expenses, datas_currency_euro_real=datas_real_euro, active_page='finance_real')


@main.route('/investments')
def investments():
    return render_template('investments.html' , active_page='investments')


@main.route('/tables')
def tables():
    return render_template('tables.html' , active_page='tables')

