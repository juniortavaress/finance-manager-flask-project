"""
financial_data package

This package provides tools to access and manage:
- User financial data (financials)
- Trade notes extraction (trade_notes)
- Market data updates and company prices (market_data)

All main classes and functions are re-exported here for simplified imports.
"""

# Import main classes from subpackages for easy access
from .financials import UserInvestmentsFetcher, UserBankFetcher, GraphAux
from .trade_notes_extraction import ManagerNotesExtractor, NomadExtractor, NuExtractor, XpExtractor
from .market_data import CompanyPricesFetcher, UpdateDatabases

# Define public interface of the package
__all__ = [
    "UserInvestmentsFetcher",
    "UserBankFetcher",
    "ManagerNotesExtractor",
    "NomadExtractor",
    "NuExtractor",
    "XpExtractor",
    "CompanyPricesFetcher",
    "UpdateDatabases",
    "GraphAux"
]
