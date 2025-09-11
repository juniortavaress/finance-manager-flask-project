import pandas as pd
from datetime import datetime
from app import create_app, database as db
from app.models import Transaction, Contribution, EuroIncomesAndExpenses, RealIncomesAndExpenses, User, Assets

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
            description=data['description'],
            amount=new_transaction.value
        )
        db.session.add(new_contribution)

    # Se for Euro
    if coin_type.lower() == "euro":
        new_euro_information = EuroIncomesAndExpenses(
            user_id=user_id,
            transaction=new_transaction,
            date=new_transaction.date,
            type=type_,
            category=category,
            amount=new_transaction.value
        )
        db.session.add(new_euro_information)

    # Se for Real
    if coin_type.lower() == "real":
        new_real_information = RealIncomesAndExpenses(
            user_id=user_id,
            transaction=new_transaction,
            date=new_transaction.date,
            type=type_,
            category=category,
            amount=new_transaction.value
        )
        db.session.add(new_real_information)

    try:
        db.session.commit()
        print(f"Transação adicionada: {data['description']} - {data['date']}")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar dados extras: {e}")


def importar_excel_para_banco(caminho_excel):
    df = pd.read_excel(caminho_excel, sheet_name="Test")
    print(df)

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

def add_company(caminho_excel):
    df = pd.read_excel(caminho_excel, sheet_name="Investments")
   

    with app.app_context():
        for _, row in df.iterrows():
            user_id = row['User']
            company = row['Company']
            date = row['Data']

            companies = Assets(
                user_id=user_id,
                start_date=date,
                company=company)
        
            db.session.add(companies)
            db.session.commit()


def delete():
    company_to_delete = "BBSA3"

    with app.app_context():
        # Buscar o registro
        asset = Assets.query.filter_by(company=company_to_delete).first()

        if asset:
            db.session.delete(asset)
            db.session.commit()
            print(f"Empresa {company_to_delete} deletada com sucesso!")
        else:
            print(f"Empresa {company_to_delete} não encontrada.")

if __name__ == "__main__":
    # importar_excel_para_banco(r"C:\Users\Jucel\OneDrive\Documentos\GitHub\finance-manager-flask-project\app\static\datas\aportes.xlsx")
    # add_company(r"C:\Users\Jucel\OneDrive\Documentos\GitHub\finance-manager-flask-project\app\static\datas\aportes.xlsx")
    delete()
# def create_user():
#     user = User(name='Junior Tavares', email='test2@gmail.com')
#     user.set_password('testflask')
#     # database.session.add(user)
#     # database.session.commit()

#     try:
#         db.session.add(user)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         print(f"Erro ao salvar Transaction: {e}")
#         return

# with app.app_context():
#     create_user()