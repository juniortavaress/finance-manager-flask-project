import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import PersonalTradeStatement
from app import create_app, database
from collections import defaultdict
app = create_app()

with app.app_context():
    trades = PersonalTradeStatement.query.order_by(
        PersonalTradeStatement.ticker.asc(),
        PersonalTradeStatement.date.asc()
    ).all()
    
    if not trades:
        print("Nenhuma transação encontrada.")
    else:
        posicoes = defaultdict(int)  # posição acumulada por ticker
        historico = defaultdict(list)  # salva o histórico para cada ticker
        
        for trade in trades:
            # Compra = +qtd | Venda = -qtd
            signed_qty = trade.quantity if trade.operation == "B" else -trade.quantity
            posicoes[trade.ticker] += signed_qty
            
            historico[trade.ticker].append({
                "date": trade.date,
                "operation": trade.operation,
                "quantity": trade.quantity,
                "acumulado": posicoes[trade.ticker]
            })
        
        # Exibir histórico
        for ticker, registros in historico.items():
            print(f"\n📈 Histórico de {ticker}:")
            for r in registros:
                print(f"{r['date']} | {r['operation']} {r['quantity']} -> posição acumulada: {r['acumulado']}")
        

