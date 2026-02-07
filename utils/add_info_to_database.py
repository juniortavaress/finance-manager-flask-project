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
from datetime import timedelta
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
    
    # for dbs in [Transaction, PersonalTradeStatement, BrokerStatus, Contribution, UserTradeSummary, PersonalTradeStatement]:
    for dbs in [UserTradeSummary]:
        for id in range(22074, 22101):
            deleted = (
                db.session.query(dbs)
                .filter(
                    dbs.id == id
                )
                .delete(synchronize_session=False)
            )

  
    # # Executa a deleção
    # deleted_count = db.session.query(BrokerStatus).filter(
    #     BrokerStatus.brokerage == "Conversão BRL - USD"
    # ).delete(synchronize_session='fetch')
   
   
    db.session.commit()

def fix_nomad_balances():
    try:
        # Filtra registros da Nomad
        nomad_records = BrokerStatus.query.filter_by(brokerage="Nomad").all()
        
        updated_count = 0
        for record in nomad_records:
            # 1. Zera os valores de investimento e lucro/perda
            record.invested_value = 0.0
            record.profit_loss = 0.0
            
            # 2. Se total_contributions não for nulo, fixa em 950
            if record.total_contributions is not None:
                record.total_contributions = 950.0
            
            # 3. Igualar o cash ao total_contributions (opcional, mas mantém a consistência)
            record.cash = record.total_contributions
            
            updated_count += 1
        
        db.session.commit()
        print(f"Sucesso! {updated_count} registros da Nomad atualizados para 950.")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar Nomad: {e}")


def add_div():
    try:
        user_id = 1  # ajuste se necessário
        ticker = "JPPA11"
        value = 1.21

        dates = [
            date(2025, 2, 10),
            date(2025, 3, 10),
            date(2025, 4, 10),
            date(2025, 5, 10),
            date(2025, 6, 10),
            date(2025, 7, 10),
            date(2025, 8, 10),
            date(2025, 9, 10),
            date(2025, 10, 10),
            date(2025, 11, 10),
            date(2025, 12, 10),
            date(2026, 1, 10),
        ]

        inserted_count = 0

        for d in dates:
            exists = (
                db.session.query(UserDividents)
                .filter_by(
                    user_id=user_id,
                    ticker=ticker,
                    date=d
                )
                .first()
            )

            if exists:
                continue

            db.session.add(UserDividents(
                user_id=user_id,
                ticker=ticker,
                date=d,
                value=value
            ))

            inserted_count += 1

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao inserir dividendos: {e}")


def extend_company_prices_until_today():
    """
    Extends the last known CompanyDatas price for each company
    until today using forward-fill.

    This function is safe to run multiple times.
    """

    today = date.today()

    # 1. Get last available date per company
    last_entries = (
        db.session.query(
            CompanyDatas.company,
            func.max(CompanyDatas.date).label("last_date")
        )
        .group_by(CompanyDatas.company)
        .all()
    )

    inserted = 0

    for company, last_date in last_entries:
        if last_date >= today:
            continue

        # 2. Load the last price record
        last_record = (
            db.session.query(CompanyDatas)
            .filter_by(company=company, date=last_date)
            .first()
        )

        if not last_record:
            continue

        # 3. Forward-fill until today
        current_day = last_date + timedelta(days=1)

        while current_day <= today:
            exists = (
                db.session.query(CompanyDatas)
                .filter_by(company=company, date=current_day)
                .first()
            )

            if not exists:
                db.session.add(
                    CompanyDatas(
                        company=company,
                        date=current_day,
                        current_price=last_record.current_price
                    )
                )
                inserted += 1

            current_day += timedelta(days=1)

    db.session.commit()
    print(f"✅ {inserted} CompanyDatas records inserted.")


def delete_trade_summaries_by_id_range(start_id=22024, end_id=22049):
    """
    Deletes UserTradeSummary records within a specific ID range.
    """

    deleted = (
        db.session.query(UserTradeSummary)
        .filter(
            UserTradeSummary.id >= start_id,
            UserTradeSummary.id <= end_id
        )
        .delete(synchronize_session=False)
    )

    db.session.commit()
    print(f"✅ Deleted {deleted} UserTradeSummary records (IDs {start_id}–{end_id}).")


if __name__ == "__main__":
    with app.app_context():
        # importar_excel_para_banco(r"app\static\datas\aportes.xlsx")
        # add_div()
        delete()
        # fix_nomad_balances()
        # from app import db
        pass

      