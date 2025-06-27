from flask import Blueprint, render_template 

main = Blueprint('main', __name__)


def carregar_dados_excel():
    # Leitura do Excel e processamento, exemplo simplificado:
    datas = {
        '2024': {
            'labels': ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            'entrada': [1023.80, 1023.80, 1023.80, 1023.80, 1023.80, 1023.80],
            'saida': [908.63, 1035.85, 1044.42, 1225.02, 1074.49, 939.96]
        },
        '2025': {
            'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul'],
            'entrada': [1015.19, 1015.19, 1015.19, 1015.19, 1015.19, 1015.19, 1015.19],
            'saida': [972.88, 837.66, 1179.89, 1240.69, 1283.40, 1193.71, 500]
        }
    }

    cumulative_balance = 0
    for year in sorted(datas.keys()):
        entradas = datas[year]['entrada']
        saidas = datas[year]['saida']
        saldo_mensal = [round(e - s, 2) for e, s in zip(entradas, saidas)]
        datas[year]['saldo'] = saldo_mensal

        accumulated_balance = []
        for saldo in saldo_mensal:
            cumulative_balance += saldo
            accumulated_balance.append(round(cumulative_balance, 2))
        datas[year]['saldo acumulado'] = accumulated_balance
        
    print(datas)
    return datas

@main.route('/')
def homepage():
    import json
    dados = carregar_dados_excel()
    dados_json = json.dumps(dados)
    print(dados_json)
    return render_template("homepage.html", datas_graph01=dados_json)