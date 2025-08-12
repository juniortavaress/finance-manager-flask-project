from datetime import date, timedelta, datetime
import pandas as pd
import json
import requests
from collections import defaultdict

class getDatas():
    def gerar_dados_eur_brl_simulados():
        lista_precos_por_dia = []
        datas_adicionadas = set()  # para garantir que só adicione 1 por dia

        moeda = 'EUR-BRL'
        quantidade = 500
        start_date = '20240601'
        end_date = datetime.today().strftime('%Y%m%d')
        url = f'https://economia.awesomeapi.com.br/json/daily/{moeda}/{quantidade}?start_date={start_date}&end_date={end_date}'

        response = requests.get(url)

        if response.status_code == 200:
            dados = response.json()
            for item in dados:
                data_completa = datetime.fromtimestamp(int(item['timestamp']))
                data_somente = data_completa.strftime('%Y-%m-%d')
                price = item['bid']

                # adiciona só o primeiro preço de cada dia
                if data_somente not in datas_adicionadas:
                    lista_precos_por_dia.append({
                        "data": data_somente,
                        "valor_eur_brl": float(price)
                    })
                    datas_adicionadas.add(data_somente)

            # ordena por data crescente
            lista_precos_por_dia.sort(key=lambda x: x['data'])
            json_string = json.dumps(lista_precos_por_dia)

            current_price = lista_precos_por_dia[-1]
            current_price["data"] = datetime.strptime(lista_precos_por_dia[-1]["data"], "%Y-%m-%d").strftime("%d/%m")
            return current_price, json_string
        else:
            print(f"Erro na requisição: {response.status_code}")
            return None

            # dados.append({"data": dia.isoformat(), "valor_eur_brl": valor})
        


    def load_datas_by_category():
        # Carregando os dados
        df = pd.read_excel(r'app\static\datas\datas.xlsx', sheet_name='Categoria')
        df = df.fillna(0) 
        df.columns = ["Categoria" if col == "Categoria" else pd.to_datetime(col).strftime("%Y-%m")for col in df.columns]
        results = {pd.to_datetime(data).strftime("%m/%y"): dict(zip(df["Categoria"], df[data])) for data in df.columns if data != "Categoria"}
        months_graph03 = list(results.keys()) 
        return months_graph03, results

    def load_datas_incomes_and_expenses_euro():
        # Carregando os dados
        df = pd.read_excel(r'app\static\datas\datas.xlsx', sheet_name='Entrada_Saida_Euro')
        # Normalização dos nomes de colunas
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        # Tratando a data
        df['data'] = pd.to_datetime(df['data'])
        df['ano'] = df['data'].dt.year.astype(str)
        df['mes'] = df['data'].dt.strftime('%b')
        #Criando o dict para o js
        acumulado = 0
        dados_por_ano = {}
        for ano, grupo in df.groupby('ano'):
            labels = grupo['mes'].to_list()
            entradas = grupo['entrada'].to_list()
            saidas = grupo['saida'].to_list()
            saldos = grupo['saldo'].to_list()
            
            saldo_acumulado = []
            for saldo in saldos:
                acumulado += saldo
                saldo_acumulado.append(round(acumulado, 2))

            dados_por_ano[ano] = {
                'labels': labels,
                'entrada': entradas,
                'saida': saidas,
                'saldo': saldos,
                'saldo acumulado': saldo_acumulado
            }
        return dados_por_ano


    def load_datas_page_real():
        # Carregando o primeiro DataFrame
        df = pd.read_excel(r'app\static\datas\datas.xlsx', sheet_name='Entrada_Saida_Real')
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df['data'] = pd.to_datetime(df['data'])
        df['ano'] = df['data'].dt.year.astype(str)
        df['mes'] = df['data'].dt.strftime('%b')

        # Carregando o segundo DataFrame
        df2 = pd.read_excel(r'app\static\datas\datas.xlsx', sheet_name='Investido')
        df2.columns = [col.strip().lower().replace(' ', '_') for col in df2.columns]
        df2['data'] = pd.to_datetime(df2['data'])
        df2['ano'] = df2['data'].dt.year.astype(str)
        df2['mes'] = df2['data'].dt.strftime('%b')

        # Dicionário final
        dados_por_ano = defaultdict(dict)

        # Acumuladores globais
        acumulado = 0

        # Processando df (Entrada_Saida_Real)
        for _, row in df.iterrows():
            ano = row['ano']
            mes = row['mes']
            if mes not in dados_por_ano[ano]:
                dados_por_ano[ano][mes] = {}

            dados_por_ano[ano][mes]['entrada'] = round(row['entrada'], 2)
            dados_por_ano[ano][mes]['saida'] = round(row['saida'], 2)
            dados_por_ano[ano][mes]['saldo'] = round(row['saldo'], 2)
            acumulado += row['saldo']
            dados_por_ano[ano][mes]['saldo_acumulado'] = round(acumulado, 2)

        # Processando df2 (Investido)
        for _, row in df2.iterrows():
            ano = row['ano']
            mes = row['mes']
            if mes not in dados_por_ano[ano]:
                dados_por_ano[ano][mes] = {}

            dados_por_ano[ano][mes]['aportes investimentos'] = round(row['aportes'], 2)
            dados_por_ano[ano][mes]['total investido'] = round(row['investido'], 2)
            dados_por_ano[ano][mes]['lucro investimentos'] = round(row['lucro'], 2)

        # Garantir que todos os campos existam em todos os meses
        campos_esperados = [
            'entrada',
            'saida',
            'saldo',
            'saldo_acumulado',
            'aportes investimentos',
            'total investido',
            'lucro investimentos'
        ]

        for ano in dados_por_ano:
            for mes in dados_por_ano[ano]:
                for campo in campos_esperados:
                    if campo not in dados_por_ano[ano][mes]:
                        dados_por_ano[ano][mes][campo] = 0.0  # ou None, se preferir

        # Ordenar meses corretamente
        meses_ordem = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        dados_ordenados = {}
        for ano, meses in dados_por_ano.items():
            dados_ordenados[ano] = {mes: meses[mes] for mes in meses_ordem if mes in meses}
        dados_ordenados = dict(dados_ordenados)
        return dados_ordenados
        

    def get_datas_home_page():
        now = datetime.now()
        year = str(now.year)
        month = now.month
        months_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        atual_month = months_labels[month - 4]

        datas_incomes_and_expenses_real = getDatas.load_datas_page_real()
        if year in datas_incomes_and_expenses_real and atual_month in datas_incomes_and_expenses_real[year]:
            month_data = datas_incomes_and_expenses_real[year][atual_month]
            real_income = month_data["entrada"]
            real_expense = month_data["saida"]
            real_balance = month_data["saldo"]
        
        datas_incomes_and_expenses_euro = getDatas.load_datas_incomes_and_expenses_euro()
        if year in datas_incomes_and_expenses_euro and atual_month in datas_incomes_and_expenses_euro[year]['labels']:
            idx = datas_incomes_and_expenses_euro[year]['labels'].index(atual_month)
            euro_income = datas_incomes_and_expenses_euro[year]['entrada'][idx]
            euro_expense = datas_incomes_and_expenses_euro[year]['saida'][idx]
            euro_balance = datas_incomes_and_expenses_euro[year]['saldo'][idx]
        
        values = {
            "real_income": real_income,
            "euro_income": euro_income,
            "real_expense": real_expense,
            "euro_expense": euro_expense,
            "real_balance": real_balance,
            "euro_balance": euro_balance,
        }

        for key in values:
            values[key] = f"{values[key]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return values