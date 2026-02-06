from app.finance_tools.api_prices import CompanyPricesFetcher, CriptoPricesFetcher

class PriceUpdate:
    """
    Handles market price updates (crypto and equities).
    """

    @staticmethod
    def update_prices(trades):
        cripto_assets = list({t.ticker for t in trades if t.investment_type == "cripto"})
        equities_assets = list({t.ticker for t in trades if t.investment_type not in ["fixed_income", "cripto"]})

        if cripto_assets:
            CriptoPricesFetcher.run_api_cripto_history_prices_brl(cripto_assets)
        
        if equities_assets:
            CompanyPricesFetcher.run_api_company_history_prices(equities_assets)

