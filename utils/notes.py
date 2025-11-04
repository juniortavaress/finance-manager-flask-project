import re
import fitz  # PyMuPDF
import traceback
import numpy as np
import pandas as pd 
from app.get_information.update_databases import UpdateDatabases
# from app.models import PersonalTradeStatement
from app.get_information.get_info_from_notes.nu_extractor import NuExtractor
from app.get_information.get_info_from_notes.nomad_extractor import NomadExtractor
# from app.get_information.get_info_from_notes.xp_extractor import XpExtractor

class ManagerNotesExtractor:
    OBS_CODES = {"#", "F", "B", "A", "H", "X", "P", "Y", "L", "T", "I", "@", '@#', 'D#', 'D'}
    HEADER = ["Market", "B/S", "Market Type", "Ticker", "Quantity", "Unit Price", "Value Without Fee"]

    @staticmethod
    def _extract_broker_from_statement(file):
        with fitz.open(stream=file, filetype="pdf") as doc:
            text = "".join(page.get_text() for page in doc)
            broker_match = re.search(r'Nu\s*Investimentos|XP\s*Investimentos|Nomad', text, re.IGNORECASE)
            if broker_match:
                raw_broker = broker_match.group(0).lower().replace(" ", "")
                if "nu" in raw_broker:
                    broker_name = "Nu Invest"
                elif "xp" in raw_broker:
                    broker_name = "Xp Invest"
                elif "nomad" in raw_broker:
                    broker_name = "Nomad"
            else:
                broker_name = "Desconhecido"
        return broker_name


    @staticmethod
    def get_info_from_trade_statement(filename, file, user_id):
        """
        Processes a brokerage note PDF file, extracts trade data,
        calculates proportional fees, and saves the data to the database.
        Returns a list of unique traded tickers.
        """
        unique_tickers = False
        broker = ManagerNotesExtractor._extract_broker_from_statement(file)
        # print(broker)
        if broker == "Nu Invest":
            NuExtractor.get_info_from_nu(filename, file, user_id)
        #     pass
        # elif broker == "Nomad":
            
        #     with fitz.open(stream=file, filetype="pdf") as doc:
        #         text = "".join(page.get_text() for page in doc)
        #     # print(text)
        #     unique_tickers = NomadExtractor.get_info_from_nomad(filename, file, user_id)
        # elif broker == "Xp Invest":
            
        #     # XpExtractor.get_info_from_xp(filename, file, user_id)
        #     pass

        return unique_tickers


import os
def process_trade_statements(files, user_id):
    tickers = []
    for file_path in files:  # 'files' é uma lista de paths (str)
        with open(file_path, "rb") as f:  # abrir em modo binário
            extracted = ManagerNotesExtractor.get_info_from_trade_statement(file_path, f.read(), user_id)
        # if extracted is not None:
        #     tickers.extend(extracted)

  

def get_all_pdfs_from_dir(root_dir):
    """Retorna uma lista de caminhos completos para todos os PDFs dentro do root_dir e subpastas."""
    pdf_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(dirpath, f))
    return pdf_files

from app import create_app
app = create_app()
with app.app_context():
    UpdateDatabases.atualize_summary_db(1)
    # pdfs = get_all_pdfs_from_dir("notes")
    # process_trade_statements(pdfs, 1)