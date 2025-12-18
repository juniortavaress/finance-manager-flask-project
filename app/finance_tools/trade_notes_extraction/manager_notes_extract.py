import re
import fitz  
from .nu_extractor import NuExtractor
from .nomad_extractor import NomadExtractor

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
        broker = ManagerNotesExtractor._extract_broker_from_statement(file)
        print(broker)
        if broker == "Nu Invest":
            trades = NuExtractor.get_info_from_nu(filename, file, user_id)
        elif broker == "Nomad":
            trades = NomadExtractor.get_info_from_nomad(filename.filename, file, user_id)
        elif broker == "Xp Invest":
            pass
        return trades


