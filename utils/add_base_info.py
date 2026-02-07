
import os, sys
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import random
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from app import create_app, database as db
from app.models import Transaction

app = create_app()

import os, sys
import random
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from app import create_app, database as db
from app.models import Transaction

app = create_app()

def seed_finance_data():
    user_id = 1
    currencies = ["BRL"]
    
    expense_categories = [
        "Food", "Monthly Bills", "Cleaning/Hygiene", "Takeout", 
        "Travel", "Housing", "Mensa", "Others", "Restaurant", "Clothing"
    ]

    start_date = date(2025, 1, 1)
    today = datetime.now().date()
    current_date = start_date

    transactions_to_add = []

    while current_date <= today:
        for coin in currencies:
            # 1. Gerar o INCOME (Salary) - entre 1000 e 1500
            salary_value = round(random.uniform(1000.0, 1500.0), 2)
            
            transactions_to_add.append(Transaction(
                user_id=user_id,
                date=current_date,
                description=f"Monthly Salary {coin}",
                type="Income",
                category="Salary",
                coin_type=coin,
                value=salary_value
            ))

            # 2. Definir a meta de gastos (80% a 100% do salário)
            target_expense_total = round(salary_value * random.uniform(0.50, 1), 2)
            
            # 3. Gerar 4 EXPENSES que somadas dão o target_expense_total
            selected_cats = random.sample(expense_categories, k=4)
            
            remaining_to_spend = target_expense_total
            for i in range(4):
                if i < 3:
                    # Sorteia um valor, mas deixa margem para os próximos (mínimo 10% do total por item)
                    max_possible = remaining_to_spend - ( (3 - i) * (target_expense_total * 0.1) )
                    val = round(random.uniform(target_expense_total * 0.1, max_possible), 2)
                    remaining_to_spend -= val
                else:
                    # O último gasta exatamente o que sobrou para fechar a conta
                    val = round(remaining_to_spend, 2)

                transactions_to_add.append(Transaction(
                    user_id=user_id,
                    date=current_date,
                    description=f"Payment {selected_cats[i]}",
                    type="Expense",
                    category=selected_cats[i],
                    coin_type=coin,
                    value=val
                ))
        
        current_date += relativedelta(months=1)

    try:
        db.session.add_all(transactions_to_add)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao inserir dados: {e}")

if __name__ == "__main__":
    with app.app_context():
        db.session.query(Transaction).filter_by(user_id=2).delete()
        seed_finance_data()
