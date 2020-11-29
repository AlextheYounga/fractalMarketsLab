import json
from ..core.functions import *
from django.apps import apps
from ..core.api import *
from tabulate import tabulate
from ..core.output import printTable
import texttable
import requests
import json
import csv
import os
import sys
from dotenv import load_dotenv
load_dotenv()


def lookupFinancials(ticker):

    cash_flow_json = getCashFlow(ticker)
    financials_json = getFinancials(ticker)
    stats = getStats(ticker, filterResults=['sharesOutstanding', 'peRatio'])    
    advanced_stats = getAdvancedStats(ticker, filterResults=['priceToSales', 'EBITDA', 'debtToEquity'])
    price = getCurrentPrice(ticker)

    financials = financials_json['financials'][0]
    cash_flow = cash_flow_json['cashflow'][0]

    capitalExpenditures = checkArray(cash_flow, 'capitalExpenditures')
    sharesOutstanding = checkArray(stats, 'sharesOutstanding')
    shareholderEquity = checkArray(stats, 'shareholderEquity')
    cashFlow = checkArray(stats, 'cashFlow')
    longTermDebt = checkArray(stats, 'longTermDebt')
    totalAssets = checkArray(stats, 'totalAssets')
    totalLiabilities = checkArray(stats, 'totalLiabilities')

    freeCashFlow = capitalExpenditures - cashFlow if (capitalExpenditures and cashFlow) else 0
    freeCashFlowPerShare = freeCashFlow / sharesOutstanding if (freeCashFlow and sharesOutstanding) else 0
    freeCashFlowYield = freeCashFlowPerShare / price if (freeCashFlowPerShare and price) else 0
    longTermDebtToEquity = longTermDebt / shareholderEquity if (longTermDebt and shareholderEquity) else 0
    netWorth = totalAssets - totalLiabilities if (totalAssets and totalLiabilities) else 0

    financialData = {
        'ticker': ticker,
        'reportDate': financials['reportDate'],
        'netIncome': financials['netIncome'],
        'netWorth': netWorth,        
        'shortTermDebt': financials['shortTermDebt'],
        'longTermDebt': financials['longTermDebt'],
        'totalCash': financials['totalCash'],
        'totalDebt': financials['totalDebt'],
        'debtToEquity': advanced_stats['debtToEquity'],
        'priceToSales': advanced_stats['priceToSales'],
        'EBITDA': advanced_stats['EBITDA'],
        'freeCashFlow': freeCashFlow,
        'freeCashFlowPerShare': freeCashFlowPerShare,
        'freeCashFlowYield': freeCashFlowYield,
        'longTermDebtToEquity': longTermDebtToEquity,
    }
    printTable(financialData)

    del financialData['ticker']
    Financials = apps.get_model('database', 'Financials')
    Financials.objects.update_or_create(
        stock=ticker,
        defaults=financialData,
    )

    

