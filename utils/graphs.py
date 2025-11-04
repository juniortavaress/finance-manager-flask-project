import os 
import sys
import pandas as pd
from datetime import datetime

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)
from app import create_app, database as db
from app.models import Transaction, Contribution, EuroIncomesAndExpenses, PersonalTradeStatement, CompanyDatas, RealIncomesAndExpenses, User, Assets, UserTradeSummary,UserDividents

app = create_app()


def graphs():
    with app.app_context():
        # Filtra todos os registros da empresa RBVA11 para o usuário 1
        data = (
            UserTradeSummary.query
            .filter_by(user_id=1, company="TGAR11")
            .order_by(UserTradeSummary.date.asc())
            .all()
        )

        dates = [entry.date for entry in data]
        quantity = [entry.quantity for entry in data]
        avg_price = [entry.avg_price for entry in data]
        dividend = [entry.dividend for entry in data]
        current_price = [entry.current_price for entry in data]
        profit = [entry.dividend + (entry.quantity * (entry.current_price - entry.avg_price)) for entry in data]
        # print(quantity)


        # Exemplo de plot com matplotlib:
        import matplotlib.pyplot as plt
        plt.plot(dates, avg_price)
        plt.plot(dates, current_price, marker='o')
        # plt.plot(dates, profit)
        plt.xlabel('Data')
        plt.ylabel('Dividendos')
        plt.title('Dividendos ao longo do tempo')
        plt.show()

        # for entry in data:
        #     # if qtd != entry.quantity:
        #     #     qtd = entry.quantity
        #     value = entry.quantity * entry.current_price
        #     print(f"📅 {entry.date.strftime('%d/%m/%Y')}")
        #     print(f"   Quantidade: {entry.quantity}")
        #     print(f"   Preço Médio: {entry.avg_price}")
        #     print(f"   Preço Atual: {entry.current_price}")
        #     print(f"   Valor Total: {value:.2f}")
        #     print(f"   Dividendos: {entry.dividend}")
        #     print("-" * 40)


if __name__ == "__main__":
    graphs()
