import re
import os
import fitz  # PyMuPDF
import traceback
import pandas as pd 
from app import database as db
from datetime import datetime
from app.models import PersonalTradeStatement

class NomadExtractor:
    OBS_CODES = {"#", "F", "B", "A", "H", "X", "P", "Y", "L", "T", "I", "@", '@#', 'D#', 'D'}

    @staticmethod
    def get_info_from_nomad(filename, file, user_id):
        """
        Processes a brokerage note PDF file, extracts trade data,
        calculates proportional fees, and saves the data to the database.
        Returns a list of unique traded tickers.
        """
        try:
            negotiation_number = os.path.basename(filename)
            text, date = NomadExtractor._extract_data_from_statement(file)

            # print(text)
            exists = PersonalTradeStatement.query.filter_by(user_id=user_id, statement_number=negotiation_number).first()
            if exists:
                print(f"Nota {negotiation_number} já registrada.")
                return None
                
            cleaned_lines = NomadExtractor._clean_content(text)
            df = NomadExtractor._create_df_records(cleaned_lines, date, negotiation_number)

            NomadExtractor._save_to_database(df, user_id)
            return df['Ticker'].unique()
        
        except Exception as e:
            print(f"Could not extract data from file: {filename}")
            print("Error:", e)
            traceback.print_exc() 
            return None
        
    @staticmethod
    def _extract_data_from_statement(file):
        """Extracts raw text and metadata from the PDF statement."""
        with fitz.open(stream=file, filetype="pdf") as doc:
            text = "".join(page.get_text() for page in doc)                
            date = re.search(r'Confirmation Date\s*[:\-]?\s*(\d{1,2}/\d{1,2}/\d{4})', text, re.IGNORECASE).group(1)
        return text, date


        
    @staticmethod
    def _clean_content(text):
        """Cleans and filters the raw text to isolate trade lines, including multi-page data."""
        # Encontra todas as seções entre 'Symbol' e 'Clearing and'
        pattern = re.compile(r"Capacity(.*?)Clearing and", re.DOTALL)
        matches = pattern.findall(text)

        if not matches:
            raise ValueError("Could not find trading sections between 'Symbol' and 'Clearing and'.")

        all_lines = []
        for match in matches:
            lines = match.strip().splitlines()
            lines = [line for line in lines if line.strip() and "page" not in line.lower()]
            all_lines.extend(lines)

        return all_lines



    @staticmethod
    def _create_df_records(cleaned_lines, date, statement_number):
        """Transforma os dados limpos da nota da Nomad em um DataFrame estruturado."""
        user_id = 1
        brokerage = "Nomad"
        records = []

        block_size = 21
        for i in range(0, len(cleaned_lines), block_size):
            block = cleaned_lines[i:i + block_size]
            if len(block) < block_size:
                continue  # ignora blocos incompletos

            try:
                ticker = block[0].strip()
                operation = block[3].strip()[0].upper()  # 'Buy' → 'B'
                quantity = float(block[5].strip())
                unit_price = float(block[6].strip())
                final_value = float(block[20].replace("$", "").strip())
            except Exception as e:
                print(f"Erro ao processar bloco: {block}\n{e}")
                continue

            records.append({
                "user_id": user_id,
                "brokerage": brokerage,
                "Date": date,
                "Negotiation Number": statement_number,
                "B/S": operation,
                "Ticker": ticker,
                "Quantity": quantity,
                "Unit Price": unit_price,
                "Final Value": final_value,
            })
        return pd.DataFrame(records)
    

    @staticmethod
    def _save_to_database(df, user_id):
        """Persists the trade records to the database."""
        def parse_date(date_str):
            for fmt in ("%d/%m/%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Unknown date format: {date_str}")



        for _, row in df.iterrows():
            # Uso:
            date_obj = parse_date(row["Date"])
            trade = PersonalTradeStatement(
                user_id=user_id,
                brokerage="Nomad",
                investment_type="foreign stock (USD)",
                date=date_obj,
                statement_number=row["Negotiation Number"],
                operation=row["B/S"],
                ticker=row["Ticker"],
                quantity=float(row["Quantity"]),
                unit_price=float(str(row["Unit Price"]).replace(",", ".")),
                final_value=float(row["Final Value"])
            )
            db.session.add(trade)
        db.session.commit()