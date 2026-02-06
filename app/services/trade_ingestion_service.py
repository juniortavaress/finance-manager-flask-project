from datetime import datetime
from app import database as db
from app.models import PersonalTradeStatement
from app.finance_tools.trade_notes_extraction import ManagerNotesExtractor


class TradeIngestionService:
    """
    Service responsible for ingesting trades into the system.

    This service ONLY creates PersonalTradeStatement records.
    It does NOT trigger any derived updates (summaries, assets, prices).
    """

    @staticmethod
    def from_pdf(user_id, files):
        """
        Extracts and persists trades from uploaded brokerage PDFs.

        Parameters:
            files (Iterable[FileStorage]): Uploaded PDF files
            user_id (int): Owner of the trades
        """
        trades = []

        for file in files:
            extracted = ManagerNotesExtractor.get_info_from_trade_statement(
                file, file.read(), user_id
            )
            if extracted:
                trades.extend(extracted)

        return trades


    @staticmethod
    def from_manual_input(user_id, data):
        """
        Persists a manually entered trade.

        Parameters:
            user_id (int): Owner of the trade
            data (dict): Trade form payload
        """
        trade = PersonalTradeStatement(
            user_id=user_id,
            brokerage=data.get("brokerage"),
            investment_type=data.get("investment_type"),
            date=datetime.strptime(data.get("date"), "%Y-%m-%d").date(),
            statement_number=data.get("statement_number"),
            operation=data.get("operation"),
            ticker=data.get("ticker"),
            quantity=float(data.get("quantity", 0)),
            unit_price=float(data.get("unit_price", 0)),
            final_value=float(data.get("final_value", 0)),
        )

        db.session.add(trade)
        db.session.commit()
        return [trade]
