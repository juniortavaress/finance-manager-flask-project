import re
import fitz  
from .nu_extractor import NuExtractor
from .nomad_extractor import NomadExtractor

class ManagerNotesExtractor:
    """
    Responsible for identifying brokerage statements
    and delegating parsing to the correct extractor.
    """

    BROKER_NU = "nu"
    BROKER_XP = "xp"
    BROKER_NOMAD = "nomad"

    OBS_CODES = {"#", "F", "B", "A", "H", "X", "P", "Y", "L", "T", "I", "@", '@#', 'D#', 'D'}
    HEADER = ["Market", "B/S", "Market Type", "Ticker", "Quantity", "Unit Price", "Value Without Fee"]


    @staticmethod
    def _extract_broker_from_statement(pdf_bytes):
        """
        Identifies the brokerage based on PDF content.

        Returns:
            str | None: normalized broker key
        """
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            text = "".join(page.get_text() for page in doc)
            broker_match = re.search(r'Nu\s*Investimentos|XP\s*Investimentos|Nomad', text, re.IGNORECASE)
            if not broker_match:
                return 
            
            raw_broker = broker_match.group(0).lower().replace(" ", "")
            if "nu" in raw_broker:
                return ManagerNotesExtractor.BROKER_NU
            elif "xp" in raw_broker:
                return ManagerNotesExtractor.BROKER_XP
            elif "nomad" in raw_broker:
                return ManagerNotesExtractor.BROKER_NOMAD
            else:
                return None


    @staticmethod
    def get_info_from_trade_statement(filename, file, user_id):
        """
        Processes a brokerage note PDF file, extracts trade data,
        calculates proportional fees, and saves the data to the database.
        Returns a list of unique traded tickers.
        """
        broker = ManagerNotesExtractor._extract_broker_from_statement(file)
        if broker == ManagerNotesExtractor.BROKER_NU:
            trades = NuExtractor.get_info_from_nu(filename, file, user_id)
        elif broker == ManagerNotesExtractor.BROKER_NOMAD:
            trades = NomadExtractor.get_info_from_nomad(filename.filename, file, user_id)
        elif broker == ManagerNotesExtractor.BROKER_XP:
            pass
        return trades


