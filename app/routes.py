from flask import Blueprint, render_template 

main = Blueprint('main', __name__)


def carregar_dados_excel():
    # Leitura do Excel e processamento, exemplo simplificado:
    dados = {
        '2024': {
            'labels': ['Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
            'entrada': [1023.80, 1023.80, 1023.80, 1023.80, 1023.80, 1023.80],
            'saida': [908.63, 1035.85, 1044.42, 1225.02, 1074.49, 939.96]
        },
        '2025': {
            'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul'],
            'entrada': [1015.19, 1015.19, 1015.19, 1015.19, 1015.19, 1015.19, 1015.19],
            'saida': [972.88, 837.66, 1179.89, 1240.69, 1283.40, 1193.71, 0]
        }
    }

    print(dados)
    return dados

@main.route('/')
def homepage():
    import json
    dados = carregar_dados_excel()
    dados_json = json.dumps(dados)
    print(dados_json)
    return render_template("homepage.html", datas_graph01=dados_json)