from app.services.dividend_services import DividendService
from app.services.transaction_service import TransactionService
from app.services.trade_ingestion_service import TradeIngestionService
from app.finance_tools.market_data.update_databases import UpdateDatabases


class UploadService:
    """
    Application-level orchestration service for user-submitted financial data.

    This service acts as a façade between HTTP routes and domain services.
    - Trade ingestion (PDF or manual)
    - Dividend registration
    - Transaction creation
    - Triggering post-processing pipelines (summaries, assets, prices)
    """
    
    @staticmethod
    def handle_trades_inputs(user_id, input_type, data):
        """
        Handles trade-related user uploads and triggers downstream updates.

        Supported input types:
        - "statement": PDF brokerage notes
        - "manual": manual trade form input
        """
        if input_type == "statement":
            trades = TradeIngestionService.from_pdf(user_id, data)
        elif input_type == "manual":
            trades = TradeIngestionService.from_manual_input(user_id, data)
        else:
             return
        
        if not trades:
            return
        
        UpdateDatabases.process_post_trade_updates(user_id=user_id, trades=trades)


    @staticmethod
    def handle_dividend_input(user_id, dividend_date, ticker, dividend_amount):
        """
        Handles dividend insertion and recomputation.
        """
        return DividendService.add_dividend(
            user_id=user_id,
            ticker=ticker,
            dividend_date=dividend_date,
            dividend_amount=dividend_amount
        )
    

    @staticmethod
    def handle_transaction_upload(user_id, data):
        """
        Handles user financial transaction uploads.

        Workflow:
        1. Creates a Transaction record
        2. If the transaction category is 'Investments',
           triggers contribution-related side effects
        """
        transaction = TransactionService.create_transaction(user_id, data)

        if transaction.category == "Investments":
            TransactionService.process_post_contribution_updates(user_id, transaction)