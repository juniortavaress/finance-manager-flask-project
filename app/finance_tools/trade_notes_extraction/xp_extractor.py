import re
import fitz  # PyMuPDF
import traceback
import numpy as np
import pandas as pd 
from datetime import datetime
from app import database as db
from app.models import PersonalTradeStatement

class XpExtractor:
    OBS_CODES = {"#", "F", "B", "A", "H", "X", "P", "Y", "L", "T", "I", "@", '@#', 'D#', 'D'}
    HEADER = ["Market", "B/S", "Market Type", "Ticker", "Quantity", "Unit Price", "Value Without Fee"]

    @staticmethod
    def get_info_from_xp(filename, file, user_id):
        """
        Processes a brokerage note PDF file, extracts trade data,
        calculates proportional fees, and saves the data to the database.
        Returns a list of unique traded tickers.
        """
        print("XP")