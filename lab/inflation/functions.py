import django
from django.apps import apps
import json
import sys
from .methodology import sectors
from ..core.output import printTabs
from ..database.hp.update_prices import batch_refresh_prices
django.setup()


def refresh_sector_prices():
    batch_refresh_prices(batch=sectors(), timeframe='max')





def fetch_names():
    """
    python -c "from lab.inflation.functions import fetch_names; print(fetch_names())"
    """

    Stock = apps.get_model('database', 'Stock')
    companies = {}
    for ticker in sectors():
        stock = Stock.objects.get(ticker=ticker)
        companies[ticker] = stock.name

    printTabs(companies)
