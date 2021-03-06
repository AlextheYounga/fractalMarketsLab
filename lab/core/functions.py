import sys
import statistics
import math
import pandas as pd
import numpy as np
# from translate import Translator


def extract_data_pd(data, key):
    """ This appears to be significantly slower than the loop """
    df = pd.DataFrame(data, columns=data[0].keys())
    return df[key].tolist()


def burrow(data, key):
    values = []
    if len(key) == 2:
        for i, row in data.items():
            value = row[key[0]][key[1]]
            values.append(value)
    if len(key) == 3:
        for i, row in data.items():
            value = row[key[0]][key[1]][key[2]]
            values.append(value)
    if len(key) == 4:
        for i, row in data.items():
            value = row[key[0]][key[1]][key[2]][key[3]]
            values.append(value)
    if len(key) == 5:
        for i, row in data.items():
            value = row[key[0]][key[1]][key[2]][key[3]][key[4]]
            values.append(value)
    if len(key) > 5:
        return 'Nest level too deep to retrieve via function.'


def extract_data(data, key):
    values = []
    if (type(data) == dict):
        if (type(key) == list):
            burrow(data, key)
        else:
            for row in data.items():
                value = row[key]
                values.append(value)
    if (type(data) == list):
        if (type(key) == list):
            burrow(data[0], key)
        else:
            for row in data:
                value = row[key]
                values.append(value)
    if (values):
        return values

    return None


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def removeZeroes(lst):
    while 0 in lst:
        lst.remove(0)
    while 0.0 in lst:
        lst.remove(0.0)
    return lst


def logReturns(prices):
    series = pd.Series(prices)
    log_returns = (np.log(series) - np.log(series.shift(1))).dropna()

    return list(log_returns)


def calculateVol(prices):
    stdevTrade = statistics.stdev(prices[:16])
    stdevMonth = statistics.stdev(prices[:22])
    stdevTrend = statistics.stdev(prices[:64])
    volTrade = prices[-1] * (stdevTrade / prices[-1]) * (math.sqrt(1/16)) if (prices[-1] != 0) else 0
    volMonth = prices[-1] * (stdevMonth / prices[-1]) * (math.sqrt(1/22)) if (prices[-1] != 0) else 0
    volTrend = prices[-1] * (stdevTrend / prices[-1]) * (math.sqrt(1/64)) if (prices[-1] != 0) else 0
    volMean = round(statistics.mean([volTrade, volMonth, volTrend]), 3)

    return volMean


def prompt_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def dataSanityCheck(array, key):
    if(array):
        if (key in array and array[key]):
            return array[key]
    return 0


def wordVariator(lst):
    variations = []
    for word in lst:
        variations.append(word.lower())
        variations.append(word.upper())
        variations.append(word.title())
    lst.extend(variations)
    lstset = set(lst)

    return list(lstset)

# TODO: Figure out word translations
# def translateWords(lst):
    # langs = ["zh", "vi", "ja", "de", "ru", "es", "ar"]
    # translations = []

    # for lang in langs:
    #     for phrase in lst:
    #         translator = Translator(to_lang=lang)
    #         translation = translator.translate(phrase)
    #         translations.append(translation)
    
    # return translations
