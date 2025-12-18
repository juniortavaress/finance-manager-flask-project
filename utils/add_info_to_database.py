import os 
import sys
import pandas as pd
from datetime import datetime, date
from sqlalchemy import func
from collections import defaultdict
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
from app import create_app, database as db
from app.models import Transaction, Contribution, CompanyDatas, Assets, User, PersonalTradeStatement, BrokerStatus, UserTradeSummary, UserDividents

app = create_app()

def add_transaction_from_dict(data):
    """Recebe um dict simulando o request.form e adiciona no banco."""
    user_id = data['user_id']
    category = data['category']
    type_ = data['type']
    coin_type = data['coin']


    try:
        value = float(data['value'])
    except ValueError:
        value = 0


    # Garantir que 'date' é datetime.date
    if isinstance(data['date'], pd.Timestamp):
        date_value = data['date'].date()
    elif isinstance(data['date'], datetime):
        date_value = data['date'].date()
    else:
        date_value = datetime.strptime(data['date'], '%d/%m/%Y').date()

    new_transaction = Transaction(
        user_id=user_id,
        date=date_value,
        description=data['description'],
        type=type_,
        category=category,
        coin_type=coin_type,
        value=value
    )

    try:
        db.session.add(new_transaction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar Transaction: {e}")
        return

    # Se for investimento
    if category.lower() == "investments":
        new_contribution = Contribution(
            user_id=user_id,
            transaction=new_transaction,
            date=new_transaction.date,
            type=type_,
            brokerage=data['description'],
            amount=new_transaction.value
        )
        db.session.add(new_contribution)

   
    try:
        db.session.commit()
        print(f"Transação adicionada: {data['description']} - {data['date']}")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar dados extras: {e}")


def importar_excel_para_banco(caminho_excel):
    df = pd.read_excel(caminho_excel, sheet_name="test_db_new")
    # print(df)

    with app.app_context():
        for _, row in df.iterrows():
            add_transaction_from_dict({
                'user_id': row['User'],
                'date': row['Date'],
                'description': row['Description'],
                'type': row['Type'],
                'category': row['Category'],
                'coin': row['Coin Type'],  
                'value': str(row['Amount']).replace('R$', '').replace(',', '.').strip()
            })



def add_dividend(user_id=1):
    excel_path = "rend.xlsx"
    sheets = pd.read_excel(excel_path, sheet_name=None)
    with app.app_context():
        for ticker, df in sheets.items():
            for _, row in df.iterrows():
                date_obj = pd.to_datetime(row["Período de Referência"]).date()
                companies = UserDividents(
                    user_id=user_id,
                    date=date_obj,
                    ticker=ticker,
                    value=float(str(row["Total"]).replace(",", "."))  )
                db.session.add(companies)
        db.session.commit()
        print(companies)





def delete():
    # deleted = (
    #     db.session.query(User)
    #     .filter(
    #         User.id == 1,
    #     )
    #     .delete(synchronize_session=False)
    # )

    # deleted = (
    #     db.session.query(PersonalTradeStatement)
    #     .filter(
    #         PersonalTradeStatement.user_id == 1,
    #     )
    #     .delete(synchronize_session=False)
    # )

    # deleted = (
    #     db.session.query(BrokerStatus)
    #     .filter(
    #         BrokerStatus.user_id == 1,
    #     )
    #     .delete(synchronize_session=False)
    # )
    # deleted = (
    #     db.session.query(CompanyDatas)
    #     .delete(synchronize_session=False)
    # )

    
    # db.session.query(BrokerStatus).filter(
    #     BrokerStatus.user_id == 1
    # ).update(
    #     {BrokerStatus.cash: BrokerStatus.total_contributions, 
    #     BrokerStatus.invested_value: 0}, 
    #     synchronize_session=False
    # )


    # deleted = (
    #     db.session.query(Transaction)
    #     .filter(
    #         Transaction.user_id == 1,
    #     )
    #     .delete(synchronize_session=False)
    # )

    # deleted = (
    #     db.session.query(UserTradeSummary)
    #     .filter(
    #         UserTradeSummary.user_id == 1,
    #     )
    #     .delete(synchronize_session=False)
    # )
    # deleted = (
    #     db.session.query(CompanyDatas)

    #     .delete(synchronize_session=False)
    # )


    # deleted = (
    #     db.session.query(Assets)
    #     .filter(
    #         Assets.user_id == 1,
    #     )
    #     .delete(synchronize_session=False)
    # )


    # cutoff = date(2025, 12, 5)

    # Excluir BrokerStatus do user 1 antes da data especificada
    # deleted_broker = (
    # db.session.query(BrokerStatus)
    #     .filter(
    #         BrokerStatus.user_id == 1,
    #         # BrokerStatus.date < cutoff
    #     )
    #     .delete(synchronize_session=False)
    # )
    deleted = (
        db.session.query(Transaction)
        .filter(
            Transaction.user_id == 1,
        )
        .delete(synchronize_session=False)
    )



    db.session.commit()
    # print(f"{deleted} registros deletados com sucesso.")
    #    Apaga os registros da PersonalTradeStatement

    # deleted_personal = (
    #     db.session.query(PersonalTradeStatement)
    #     .filter(
    #         PersonalTradeStatement.id == 5,
    # )
    #     .delete(synchronize_session=False)
    # )
    # trade = db.session.query(PersonalTradeStatement).filter_by(id=6).first()
    # if trade:
    #     trade.quantity = 2
    #     trade.final_value = 3000.0
    #     trade.unit_price = 3000.0
    #     db.session.commit()
    #     print("Trade atualizado com sucesso!")
    # else:
    #     print("Trade não encontrado")
    # # Apaga os registros da Asset
    # deleted_assets = (
    #     db.session.query(Assets)
    #     .filter(Assets.user_id == 1)
    #     .delete(synchronize_session=False)
    # )

    # db.session.commit()

    # print("aqui")
    # print(f"{deleted_personal} registros deletados da PersonalTradeStatement.")
    # print(f"{deleted_assets} registros deletados da Asset.")

def add():

    dados = [
        {"user_id": 1, "brokerage": "Nomad", "investment_type": "foreign stock (USD)", "date": "21/10/23", "company": "NVI", "quantity": 1, "current_price": 20, "avg_price": 30, "dividend": 1},
        {"user_id": 1, "brokerage": "Nomad", "investment_type": "foreign stock (USD)", "date": "21/11/23", "company": "XXP", "quantity": 2, "current_price": 30, "avg_price": 30, "dividend": 2},
        {"user_id": 1, "brokerage": "Nomad", "investment_type": "foreign stock (USD)", "date": "21/10/22", "company": "XXP", "quantity": 1, "current_price": 30, "avg_price": 30, "dividend": 2},
        {"user_id": 1, "brokerage": "Nomad", "investment_type": "foreign stock (USD)", "date": "21/11/23", "company": "NVI", "quantity": 3, "current_price": 50, "avg_price": 55, "dividend": 3},
        {"user_id": 1, "brokerage": "NuInvest", "investment_type": "stock", "date": "21/10/23", "company": "Nu", "quantity": 2, "current_price": 30, "avg_price": 20, "dividend": 2},
        {"user_id": 1, "brokerage": "NuInvest", "investment_type": "stock", "date": "21/11/23", "company": "Nu", "quantity": 1, "current_price": 40, "avg_price": 27, "dividend": 2},
        {"user_id": 1, "brokerage": "NuInvest", "investment_type": "stock", "date": "23/12/23", "company": "Nu", "quantity": 1, "current_price": 35, "avg_price": 27, "dividend": 2},
        {"user_id": 1, "brokerage": "NuInvest", "investment_type": "real estate fund", "date": "21/10/22", "company": "LP", "quantity": 3, "current_price": 50, "avg_price": 26, "dividend": 3},
        {"user_id": 1, "brokerage": "XP", "investment_type": "fixed income", "date": "21/10/23", "company": "TD", "quantity": 1, "current_price": 20, "avg_price": 20, "dividend": 1},
        {"user_id": 1, "brokerage": "XP", "investment_type": "fixed income", "date": "21/11/23", "company": "TD", "quantity": 2, "current_price": 35, "avg_price": 20, "dividend": 2},
        {"user_id": 1, "brokerage": "XP", "investment_type": "fixed income", "date": "21/12/23", "company": "TD", "quantity": 3, "current_price": 60, "avg_price": 50, "dividend": 3},
        {"user_id": 1, "brokerage": "XP", "investment_type": "crypto", "date": "21/10/23", "company": "TDS", "quantity": 2, "current_price": 35, "avg_price": 20, "dividend": 2},
        {"user_id": 1, "brokerage": "XP", "investment_type": "crypto", "date": "21/11/23", "company": "TDS", "quantity": 3, "current_price": 60, "avg_price": 20, "dividend": 3},
    ]

    # Inserção em lote
    for linha in dados:
        linha["date"] = datetime.strptime(linha["date"], "%d/%m/%y").date()
        
        registro = UserTradeSummary(**linha)
        db.session.add(registro)

    db.session.commit()


def add_investment_type_column():
    from sqlalchemy import inspect, text
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user_trade_summary')]

        # Adicionar coluna se não existir
        if 'investment_type' not in columns:
            print("Adicionando coluna 'investment_type'...")
            db.session.execute(text(
                "ALTER TABLE user_trade_summary ADD COLUMN investment_type VARCHAR(50) DEFAULT 'stock' NOT NULL;"
            ))
            db.session.commit()
        else:
            print("Coluna 'investment_type' já existe.")

        # Atualizar registros existentes
        all_trades = UserTradeSummary.query.all()
        for trade in all_trades:
            if trade.brokerage == "Nomad":
                trade.investment_type = "foreign stock (USD)"
            elif trade.brokerage == "NuInvest" and trade.company == "Nu":
                trade.investment_type = "stock"
            elif trade.brokerage == "NuInvest" and trade.company == "LP":
                trade.investment_type = "real estate fund"
            elif trade.brokerage == "XP" and trade.company == "TD":
                trade.investment_type = "fixed income"
            elif trade.brokerage == "XP" and trade.company == "TDS":
                trade.investment_type = "crypto"

        db.session.commit()
        print(f"Coluna 'investment_type' adicionada e {len(all_trades)} registros atualizados.")



if __name__ == "__main__":
    with app.app_context():
        # importar_excel_para_banco(r"app\static\datas\aportes.xlsx")
        delete()
        # from app import db

      