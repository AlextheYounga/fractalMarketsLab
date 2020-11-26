import statistics
from scipy import stats
import math
from ..core.functions import *
from ..core.api import *
from ..core.imports import *
from .functions import *
from .export import exportFractal
import sys
from tabulate import tabulate
# from .imports import *

# Fetch historical prices
# ticker = "SP500"
# asset_data = getHistoricalData(ticker)
# TODO: Go back and redo the calculations with what you know now. Errors are popping up.
asset_data = parseIndexDateClose("SPX.csv")

prices = extractData(asset_data, 'close')
count = len(prices)

# Arbitrary fractal scales
scales = exponentialScales(count, 3, 6)

print(json.dumps(scales, indent=1))

returns = returnsCalculator(prices)
deviations = deviationsCalculator(returns, scales)
running_totals = running_totalsCalculator(deviations, scales)

# Calculating statistics of returns and running totals
range_stats = {}
for scale, days in scales.items():
    range_stats[scale] = {}
    range_stats[scale]['means'] = chunkedAverages(returns, days)
    range_stats[scale]['stDevs'] = chunkedDevs(returns, days)
    range_stats[scale]['minimums'] = chunkedRange(running_totals[scale], days)['minimum']
    range_stats[scale]['maximums'] = chunkedRange(running_totals[scale], days)['maximum']
    range_stats[scale]['ranges'] = chunkedRange(running_totals[scale], days)['range']


# Calculating Rescale Range
for scale, values in range_stats.items():
    range_stats[scale]['rescaleRanges'] = {}
    for i, value in values['ranges'].items():
        rescaleRange = (value / values['stDevs'][i] if (values['stDevs'][i] != 0) else 0)

        range_stats[scale]['rescaleRanges'][i] = rescaleRange

# Key stats for fractal calculations
for scale, values in range_stats.items():
    range_stats[scale]['keyStats'] = {}
    rescaleRanges = list(values['rescaleRanges'].values())
    range_stats[scale]['keyStats']['rescaleRangeAvg'] = statistics.mean(rescaleRanges)
    range_stats[scale]['keyStats']['size'] = scales[scale]
    range_stats[scale]['keyStats']['logRR'] = math.log10(statistics.mean(rescaleRanges)) if (statistics.mean(rescaleRanges) > 0) else 0
    range_stats[scale]['keyStats']['logScale'] = math.log10(scales[scale])

# Hurst Exponent Calculations
fractal_results = {
    'rescaleRange': {}
}
# Adding rescale ranges to final data
for scale, days in scales.items():
    fractal_results['rescaleRange'][scale] = round(range_stats[scale]['keyStats']['rescaleRangeAvg'], 2)


# Calculating linear regression of rescale range logs
log_RRs = scaledDataCollector(scales, range_stats, ['keyStats', 'logRR'])
log_scales = scaledDataCollector(scales, range_stats, ['keyStats', 'logScale'])
slope, intercept, r_value, p_value, std_err = stats.linregress(log_scales, log_RRs)

# Calculator
def fractalCalculator(x, y):
    sections = tradingFractalSections(x, y)
    results = {}
    for i, section in sections.items():
        slope, intercept, r_value, p_value, std_err = stats.linregress(section['x'], section['y'])
        results[i] = {
            'hurstExponent': round(slope, 2),
            'fractalDimension': round((2 - slope), 2),
            'r-squared': round(r_value**2, 2),
            'p-value': round(p_value, 2),
            'standardError': round(std_err, 2)
        }
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    results['fullSeries'] = {
        'hurstExponent': round(slope, 2),
        'fractalDimension': round((2 - slope), 2),
        'r-squared': round(r_value**2, 2),
        'p-value': round(p_value, 2),
        'standardError': round(std_err, 2)
    }
    return results


# Results
fractal_results['regressionResults'] = fractalCalculator(log_scales, log_RRs)
# print(json.dumps(fractal_results, indent=1))
# print('The lists are:', *L, sep='\n')
print(tabulate([
    ['Count', trend_data['upDays']['count']],
    ['Consecutive', trend_data['upDays']['consecutive']],
    ['Average', trend_data['upDays']['average']]],
    headers=['Up Days', '']))

print(tabulate([
    ['Trade', trend_data['downDays']['count']],
    ['Month', trend_data['downDays']['consecutive']],
    ['Trend', trend_data['downDays']['average']],
    ['Tail', trend_data['downDays']['average']]],
    headers=['Scale', 'HurstExponent', 'FractalDimension', 'r-squared', 'p-value', 'StandardError']))

# Export to CSV
exportFractal(fractal_results, scales)
