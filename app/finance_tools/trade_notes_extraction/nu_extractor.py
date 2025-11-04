import re
import fitz  # PyMuPDF
import traceback
import numpy as np
import pandas as pd 
from datetime import datetime
from app import database as db
from app.models import PersonalTradeStatement

class NuExtractor:
    OBS_CODES = {"#", "F", "B", "A", "H", "X", "P", "Y", "L", "T", "I", "@", '@#', 'D#', 'D'}
    HEADER = ["Market", "B/S", "Market Type", "Ticker", "Quantity", "Unit Price", "Value Without Fee"]

    @staticmethod
    def get_info_from_nu(filename, file, user_id):
        """
        Processes a brokerage note PDF file, extracts trade data,
        calculates proportional fees, and saves the data to the database.
        Returns a list of unique traded tickers.
        """
        try:
            with fitz.open(stream=file, filetype="pdf") as doc:
                text = "".join(page.get_text() for page in doc)  
        
            if "Nota de Negociação de Títulos" in text:
                NuExtractor._extract_data_from_fixed_statement(user_id, text)

            else:
                date, total_price, negotiation_number = NuExtractor._extract_data_from_statement(text)

                # exists = PersonalTradeStatement.query.filter_by(user_id=user_id, statement_number=negotiation_number).first()
                # if exists:
                #     print(f"Nota {negotiation_number} já registrada.")
                #     return None
                    
                # cleaned_lines = NuExtractor._clean_content(text)
                # df = NuExtractor._create_df_records(cleaned_lines, date, negotiation_number, total_price)
                # NuExtractor._save_to_database(df, user_id)
                # return df['Ticker'].unique()
        
        except Exception as e:
            print(f"Could not extract data from file: {filename}")
            print("Error:", e)
            traceback.print_exc() 
            return None
        
    @staticmethod
    def _extract_data_from_statement(text):
        """Extracts raw text and metadata from the PDF statement."""       
        date = re.search(r'(Data Preg[aã]o)\s*[:\-]?\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE).group(2)
        total_price = re.search(r'L[ií]quido para.*?(-?[\d\.]+,\d{2})', text, re.IGNORECASE | re.DOTALL).group(1)
        negotiation_number = re.search(r'Número da nota\s*\n\s*(\d+)', text, re.IGNORECASE).group(1)
        return date, total_price, negotiation_number
        
    @staticmethod
    def _extract_data_from_fixed_statement(user_id, text):
        """Extracts raw text and metadata from the PDF statement.""" 
        statement_code = re.search(r'Número(\s*do\s*protocolo)?\s*[\n]*\s*(\S+[-/]\S+|\d+)', text).group(2)
        existing_trade = PersonalTradeStatement.query.filter_by(
            user_id=user_id,
            statement_number=statement_code
        ).first()

        if existing_trade:
            print(f"Statement {statement_code} already exists for user {user_id}. Skipping insertion.")
            return  
        
        try:
            text = re.sub(r'.*?Nota de Negociação de Títulos', '', text, flags=re.DOTALL)
            operation_type = re.search(r'Nota de\s+(.+?)(?:\n|$)', text, re.DOTALL).group(1).strip()
            if operation_type not in ["VENDA FINAL", "RESGATE"]:
                operation_type = re.search(r'Tipo(?:/Emitente)?\s*([\w\s]+)(?=\s*\n(?!Data))', text).group(1)[0]
            operation_type = "B" if operation_type == "C" or operation_type == "VENDA FINAL" else "S"


            date = re.search(r'(Data de Operação|Data)\s+(\d{2}/\d{2}/\d{4})', text).group(2)
            code = re.search(r'Título\s+([A-Za-z0-9\s]+?)(?=\s*(?:Valor|Tx|\d{1,2}\s*t))', text.replace('\n', ' ')).group(1).strip()
            tax = re.search(r'Tx\.\s*/\s*CUPON\s*%\s*([\d.,]+)', text)
            tax = tax.group(1) if tax else 0
            broadcaster = re.search(r'Emissor\s+([A-Za-z0-9\s]+?)(?=\s+Comando)', text.replace('\n', ' ')).group(1).strip() if not "Tesouro" in code else "Banco Central"
            total_price = re.search(r'(Valor da Operação|Valor Total)\s*(R?\$\s?[\d.,]+|\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', text).group(2)
            quantity = re.search(r'(Quantidade|Quantidade/Valor nominal)\s*([\d.,]+)', text).group(2)
            unit_price = re.search(r'(Valor 1 título|Preço Unitário da Operação|Valor da Operação)\s*(R?\$\s?[\d.,]+|\d+,\d{2})', text)
            unit_price = re.search(r'(Valor 1 título|Preço Unitário da Operação|Valor da Operação)\s*[\n\r]*\s*(R?\$\s?)?([\d.,]+)', text).group(3)


            if "Banco Central" in broadcaster:
                ticker = code  # Apenas a terceira linha
            else:
                print(statement_code)
                bank_name = ' '.join(broadcaster.split()[:2])
                formated_tax = "CDI" if tax in ["0", "0.00"] else f"{tax}%"
                ticker = f"{bank_name} - {formated_tax} - {code}"
            print(ticker)

            
            trade = PersonalTradeStatement(
                user_id=user_id,
                brokerage="NuInvest",
                investment_type="fixed_income",
                date=datetime.strptime(date, "%d/%m/%Y").date(),
                statement_number=statement_code,
                operation=operation_type,
                ticker=ticker,
                quantity=float(str(quantity).replace(",", ".")),  # usa float para aceitar valores como '0,56'
                unit_price=float(str(unit_price).replace("R$", "").strip().replace(".", "").replace(",", ".")),  # trata moeda brasileira
                final_value=float(str(total_price).replace("R$", "").strip().replace(".", "").replace(",", "."))  # idem
            )
            db.session.add(trade)
            db.session.commit()

        except Exception as e:
            print(f"Could not extract data from file: {statement_code}")
            print("Error:", e)
            traceback.print_exc() 
            return None
        
    @staticmethod
    def _clean_content(text):
        """Cleans and filters the raw text to isolate trade lines."""
        # OBS_CODES = {"#", "F", "B", "A", "H", "X", "P", "Y", "L", "T", "I", "@", '@#', 'D#', 'D'}
        HEADER = ["Market", "B/S", "Market Type", "Ticker", "Quantity", "Unit Price", "Value Without Fee"]
        start_idx = text.find("Valor/Ajuste D/C")
        end_idx = text.find("Resumo dos Negócios")
        lines = text[start_idx:end_idx].strip().splitlines()[1:]
        return [line for line in lines if line.strip() not in NuExtractor.OBS_CODES]
    
    @staticmethod
    def _create_df_records(cleaned_lines, date, negotiation_number, total_price):
        """Persists the trade records to the database."""
        records = []
        current_record = []
        for item in cleaned_lines:
            if item == 'BOVESPA':
                if current_record:
                    records.append(current_record[:7])
                current_record = [item]
            else:
                current_record.append(item)
        if current_record:
            records.append(current_record[:7])

        # Create DataFrame and clean structure
        df = pd.DataFrame(records, columns=NuExtractor.HEADER)
        df["Date"] = datetime.strptime(date, "%d/%m/%Y").date()
        df["Negotiation Number"] = negotiation_number
        df.drop(columns=['Market', 'Market Type'], inplace=True)
        df = df[["Date"] + ["Negotiation Number"] + [col for col in df.columns if col != "Date" and col != "Negotiation Number"]]
        df['Value Without Fee'] = df['Value Without Fee'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)
        df['B/S'] = df['B/S'].replace({'C': 'B', 'V': 'S'})
        df['Ticker'] = df['Ticker'].str.extract(r'^(.{5}\d?)')
        df['Ticker'] = df['Ticker'].replace({'BBPO11': 'TVRI11', 'RBED11': 'RBVA11'})

        # Define stock split eventes
        split_events = [
            {"ticker": "BBAS3", "date": datetime.strptime("15/04/2024", "%d/%m/%Y").date(), "ratio": 2.0},
            {"ticker": "RBVA11", "date": datetime.strptime("31/05/2025", "%d/%m/%Y").date(), "ratio": 10}
            ]
        
        for event in split_events:
            affected_rows = (df["Ticker"] == event["ticker"]) & (df["Date"] < event["date"])

            # Ajuste especial para RBVA11 em 29/04/2025
            if event["ticker"] == "RBVA11":
                special_date = datetime.strptime("29/04/2025", "%d/%m/%Y").date()
                special_rows = affected_rows & (df["Date"] == special_date)
                df.loc[special_rows, "Quantity"] = np.floor((df.loc[special_rows, "Quantity"].astype(int) + 4) * event["ratio"] + 0.5).astype(int)

                # Aplica o split normalmente para os demais afetados
                normal_rows = affected_rows & (df["Date"] != special_date)
                df.loc[normal_rows, "Quantity"] = np.floor(df.loc[normal_rows, "Quantity"].astype(int) * event["ratio"] + 0.5).astype(int)
            else:
                # Split padrão para outros tickers
                df.loc[affected_rows, "Quantity"] = np.floor(df.loc[affected_rows, "Quantity"].astype(int) * event["ratio"] + 0.5).astype(int)

            # Ajuste de preço unitário
            df["Unit Price"] = df["Unit Price"].astype(str).str.replace(",", ".", regex=False).astype(float)
            df.loc[affected_rows, "Unit Price"] = df.loc[affected_rows, "Unit Price"] / event["ratio"]

        # Compute sums for buys and sells
        buy_sum = df.loc[df['B/S'] == 'B', 'Value Without Fee'].sum()
        sell_sum = df.loc[df['B/S'] == 'S', 'Value Without Fee'].sum()
        base_total = buy_sum + sell_sum

        # Calculate the proportional fee ("taxa")
        value_before_tax = abs(sell_sum - buy_sum)
        total_price_float = float(total_price.replace('.', '').replace(',', '.'))
        taxa = abs(abs(value_before_tax) - abs(total_price_float))

        # Apply fee proportionally to buys
        if buy_sum > 0:
            taxa_c = (df.loc[df['B/S'] == 'B', 'Value Without Fee'] / base_total) * taxa
            df.loc[df['B/S'] == 'B', 'Final Value'] = (df.loc[df['B/S'] == 'B', 'Value Without Fee'] + taxa_c).round(2)

        # Apply fee proportionally to sells
        if sell_sum > 0:
            taxa_v = (df.loc[df['B/S'] == 'S', 'Value Without Fee'] / base_total) * taxa
            df.loc[df['B/S'] == 'S', 'Final Value'] = (df.loc[df['B/S'] == 'S', 'Value Without Fee'] - taxa_v).round(2)
        
        return df

    @staticmethod
    def _save_to_database(df, user_id):
        """Persists the trade records to the database."""
        for _, row in df.iterrows():
            ticker = str(row["Ticker"]).strip()

            # Define o tipo de investimento com base no final do ticker
            if ticker.endswith("11"):
                investment_type = "real_state"
            elif ticker.endswith(("3", "4", "5", "6")):
                investment_type = "stock"
            else:
                investment_type = "other"  # caso o ticker não siga o padrão

            trade = PersonalTradeStatement(
                user_id=user_id,
                brokerage="NuInvest",
                investment_type=investment_type,
                date=row["Date"],
                statement_number=row["Negotiation Number"],
                operation=row["B/S"],
                ticker=row["Ticker"],
                quantity=int(row["Quantity"]),
                unit_price=float(str(row["Unit Price"]).replace(",", ".")),
                final_value=float(row["Final Value"])
            )
            db.session.add(trade)
        db.session.commit()

  
