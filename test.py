# from app.models import Transaction
# from app import create_app, database

# app = create_app()

# with app.app_context():
#     transactions = Transaction.query.all()
    
#     if not transactions:
#         print("Nenhuma transação encontrada.")
#     else:
#         for t in transactions:
#             print(f"ID: {t.id}")
#             print(f"Data: {t.date}")
#             print(f"Descrição: {t.description}")
#             print(f"Tipo: {t.type}")
#             print(f"Categoria: {t.category}")
#             print(f"Moeda: {t.coin_type}")
#             print(f"Valor: {t.value}")
#             print("-" * 40)

""""""
# import pandas as pd
# def load_datas_by_category():
#     # Carregando os dados
#     df = pd.read_excel(r'app\static\datas\datas.xlsx', sheet_name='Categoria')
#     df = df.fillna(0) 
#     df.columns = ["Categoria" if col == "Categoria" else pd.to_datetime(col).strftime("%Y-%m")for col in df.columns]
#     results = {pd.to_datetime(data).strftime("%m/%y"): dict(zip(df["Categoria"], df[data])) for data in df.columns if data != "Categoria"}
#     months_graph03 = list(results.keys()) 
#     return months_graph03, results
# x, y = load_datas_by_category()

# print(x)
# print('\n\n\n', y)

""""""

def get():
    from datetime import date
    from sqlalchemy import func, extract
    from app.models import Transaction, Contribution, EuroIncomesAndExpenses, RealIncomesAndExpenses
    from app import create_app, database as db

    app = create_app()

    today = date.today()
    with app.app_context():
        all_months_data  = (
            db.session.query(
                func.sum(EuroIncomesAndExpenses.amount).filter(EuroIncomesAndExpenses.type == "Expense"),
                func.sum(EuroIncomesAndExpenses.amount).filter(EuroIncomesAndExpenses.type == "Income")
            ).one()
        )

        current_month_data  = (
            db.session.query(
                func.sum(EuroIncomesAndExpenses.amount).filter(EuroIncomesAndExpenses.type == "Expense"),
                func.sum(EuroIncomesAndExpenses.amount).filter(EuroIncomesAndExpenses.type == "Income")
            )
            .filter(extract("month", EuroIncomesAndExpenses.date) == today.month)
            .filter(extract("year", EuroIncomesAndExpenses.date) == today.year)
            .one()
        )


    balance = all_months_data[1] - all_months_data[0]
    month_expense = current_month_data[0]
    month_income = current_month_data[1]
   


get()