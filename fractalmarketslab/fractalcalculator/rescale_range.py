import csv
import statistics
from .functions import *

with open('fractalmarketslab/imports/RescaleRangeSPX.csv', newline='', encoding='utf-8') as csvfile:
    rangeData = {}
    reader = csv.DictReader(csvfile)

    
    for i, row in enumerate(reader):
        # Using Risk Range Scales
        values = {
            'date': row['\ufeffDate'] if row['\ufeffDate'] else '',
            'close': row['Close'] if row['Close'] else 0,
            'returns': row['Returns'] if row['Returns'] else 0,

            'stats': {
                'month': {
                    'deviation': row['MonthDev'] if row['MonthDev'] else 0,
                    'runningTotal': row['MonthRT'] if row['MonthRT'] else 0,
                },
                'trade': {
                    'deviation': row['TradeDev'] if row['TradeDev'] else 0,
                    'runningTotal': row['TradeRT'] if row['TradeRT'] else 0,
                },
                'trend': {
                    'deviation': row['TrendDev'] if row['TrendDev'] else 0,
                    'runningTotal': row['TrendRT'] if row['TrendRT'] else 0,
                },
                'tail': {
                    'deviation': row['TailDev'] if row['TailDev'] else 0,
                    'runningTotal': row['TailRT'] if row['TailRT'] else 0,
                }
            }
        }

        # Append value dictionary to data
        rangeData[i] = values

scales = {
    'month': 22,
    'trade': 16,
    'trend': 64,
    'tail': 756,  # Max scale; Omega
}


returns = extractData(rangeData, 'returns')

rangeStats = {
    'month': {
        'means': chunkedAverages(returns, scales['month']),
        'stDev': chunkedDevs(returns, scales['month']),
    },
    'trade': {
        'means': chunkedAverages(returns, scales['trade']),
        'stDev': chunkedDevs(returns, scales['trade']),
    },
    'trend': {
        'means': chunkedAverages(returns, scales['trend']),
        'stDev': chunkedDevs(returns, scales['trend']),
    },
    'tail': {
        'means': chunkedAverages(returns, scales['tail']),
        'stDev': chunkedDevs(returns, scales['tail']),
    }
}
