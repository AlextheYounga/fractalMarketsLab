import django
from django.apps import apps
from dotenv import load_dotenv
import json
import sys
from datetime import date
from .functions import dynamicUpdateCreate
from ..core.functions import chunks, dataSanityCheck
from ..core.api import quoteStatsBatchRequest, getHistoricalEarnings, getPriceTarget
from ..core.output import printTable, printFullTable, writeCSV
from ..fintwit.tweet import send_tweet
load_dotenv()
django.setup()

Stock = apps.get_model('database', 'Stock')
Trend = apps.get_model('database', 'Trend')
Watchlist = apps.get_model('database', 'Watchlist')

# Main Thread Start
print('Running...')

results = []
tickers = Stock.objects.all().values_list('ticker', flat=True)

chunked_tickers = chunks(tickers, 100)
for i, chunk in enumerate(chunked_tickers):
    batch = quoteStatsBatchRequest(chunk)

    for ticker, stockinfo in batch.items():
        print('Chunk {}: {}'.format(i, ticker))

        if (stockinfo.get('quote', False) and stockinfo.get('stats', False)):
            quote = stockinfo.get('quote')
            stats = stockinfo.get('stats')
            price = quote.get('latestPrice', 0)

            if (price and isinstance(price, float)):
                stock, created = Stock.objects.update_or_create(
                    ticker=ticker,
                    defaults={'lastPrice': price},
                )
            else:
                continue

            ttmEPS = stats.get('ttmEPS', None)
            day5ChangePercent = round(dataSanityCheck(stats, 'day5ChangePercent') * 100, 2)
            month1ChangePercent = round(dataSanityCheck(stats, 'month1ChangePercent') * 100, 2)
            ytdChangePercent = round(dataSanityCheck(stats, 'ytdChangePercent') * 100, 2)

            # Critical
            week52high = dataSanityCheck(stats, 'week52high')
            changeToday = round(dataSanityCheck(quote, 'changePercent') * 100, 2)            
            volume = dataSanityCheck(quote, 'volume')
            previousVolume = dataSanityCheck(quote, 'previousVolume')

            critical = [changeToday, week52high, volume, previousVolume]

            if ((0 in critical)):
                continue

            fromHigh = round((price / week52high) * 100, 3)

            # Save Data to DB
            data_for_db = {
                'Valuation':  {
                    'peRatio': stats.get('peRatio', None),
                },
                'Trend': {
                    'week52': week52high,
                    'day5ChangePercent': day5ChangePercent if day5ChangePercent else None,
                    'month1ChangePercent': month1ChangePercent if month1ChangePercent else None,
                    'ytdChangePercent': ytdChangePercent if ytdChangePercent else None,
                    'day50MovingAvg': stats.get('day50MovingAvg', None),
                    'day200MovingAvg': stats.get('day200MovingAvg', None),
                    'fromHigh': fromHigh
                },
                'Earnings': {
                    'ttmEPS': ttmEPS
                },
            }
            
            dynamicUpdateCreate(data_for_db, stock)

            if (price > 5):
                if ((fromHigh < 105) and (fromHigh > 95)):
                    if (changeToday > 12):
                        if (volume > previousVolume):
                            priceTargets = getPriceTarget(ticker)
                            fromPriceTarget = round((price / priceTargets['priceTargetHigh']) * 100, 3) if (dataSanityCheck(priceTargets, 'priceTargetHigh')) else 0                            
                            avgPricetarget = priceTargets['priceTargetAverage'] if (dataSanityCheck(priceTargets, 'priceTargetAverage')) else None
                            highPriceTarget = priceTargets['priceTargetHigh'] if (dataSanityCheck(priceTargets, 'priceTargetHigh')) else None


                            # Save Trends to DB
                            Trend.objects.filter(stock=stock).update(                            
                                avgPricetarget=avgPricetarget,
                                highPriceTarget=highPriceTarget,
                                fromPriceTarget=fromPriceTarget,
                            )

                            keyStats = {}
                            for model, data in data_for_db.items():
                                keyStats.update(data)
                        
                            keyStats.update({
                                'highPriceTarget': highPriceTarget,
                                'fromPriceTarget': fromPriceTarget,
                            })
                            
                            stockData = {
                                'ticker': ticker,
                                'name': stock.name,
                                'lastPrice': price
                            }
                            stockData.update(keyStats)

                            # Save to Watchlist
                            Watchlist.objects.update_or_create(
                                stock=stock,
                                defaults=stockData
                            )

                            stockData['changeToday'] = changeToday                        
                            print('{} saved to Watchlist'.format(ticker))
                            results.append(stockData)

if results:
    today = date.today().strftime('%m-%d')
    writeCSV(results, 'lab/trend/output/chase/trend_chasing_{}.csv'.format(today))

    printFullTable(results, struct='dictlist')

    # Tweet
    tweet = ""
    for i, data in enumerate(results):
        ticker = '${}'.format(data['ticker'])
        changeToday = data['changeToday']
        tweet_data = "{} +{}% \n".format(ticker, changeToday)
        tweet = tweet + tweet_data

    send_tweet(tweet, True)