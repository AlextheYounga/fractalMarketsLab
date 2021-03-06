import os
import sys
from lab.core.output import printTabs
from dotenv import load_dotenv
load_dotenv()


def list_commands():
    headers = ['Command', 'Description']
    print("\n")
    print('Available Subcommands')
    print('No quotes required on [ticker] arguments, may be typed directly into the terminal.')
    print("\n\n")

    commands = [
        ['correlations:scan', 'Runs correlations on all ETFs on the market, with *every other ETF on the market. (Takes about half an hour)'],
        ['donchian [ticker]', 'Runs a donchian range calculation on a ticker'],
        ['financials [ticker]', 'Returns financials data for ticker, including some custom indicators not provided by IEX.'],
        ['macro:trends [timeperiod=1m] [gain=20]', 'Scans all ETFs and returns the ETFs with the performance above an int (gain) within a timerange (5d, 1m, 3m, 1y)'],
        ['macro:gainers', 'Scans all ETFs and returns ETFs with highest day change.'],
        ['news:scrape [query]', 'Searches a query and searches first 10 articles for stocks mentioned in article'],
        ['hurst [ticker] [output]', 'Runs a rescaled range analysis on a ticker. Output defaults to table.'],
        ['range [ticker] [tweet=False]', 'Runs a volatility range analysis on a ticker.'],
        ['fintwit:follow [handle, page_number]', 'Combs through a followers of a user and follows particular people. Each loop is a *page* of 20 people.'],
        ['fintwit:trim [page_number]', 'Combs through your followers and removes certain types of people.'],
        ['trend:chase', 'Scans all stocks and returns todays gainers with above certain thresholds (weeds out the penny stocks).'],
        ['trend:search [string]', 'Scans stocks with string in stock name and looks for gainers'],
        ['trend:earnings', 'Scans all stocks and returns todays gainers who have consistently good earnings.'],
        ['trend:volume', 'Scans all stocks and returns todays gainers with abnormally high volume.'],
        ['trend:gainers', 'Grabs todays gainers and checks their earnings.'],
        ['pricedingold [ticker][timespan=5y][test=False]', 'Graphs and assets price in gold.'],
        ['vix [ticker]', 'Runs the VIX volatility equation on a ticker'],
    ]
    printTabs(commands, headers, 'simple')
    print("\n\n")


def correlations_controller(subroutine, args=[]):
    # TODO Figure out the rest of correlations.
    if (subroutine == 'scan'):
        from lab.correlations.scanner import scanner
        print(scanner())


def donchian_controller(args):
    if (args):
        ticker = args.pop(0)
        tweet = True if (args and (args[0] == 'tweet')) else False
        from lab.donchian.range import calculate
        print(calculate(ticker, tweet))


def financials_controller(args):
    if (args):
        ticker = args[0]
        from lab.financials.lookup import lookupFinancials
        print(lookupFinancials(ticker))


def macro_controller(subroutine, args=[]):
    if (subroutine == 'trends'):
        from lab.macro.trends import calculate_trends
        if (args and len(args) > 1):

            try:
                timeperiod = args[0]
            except IndexError:
                timeperiod = '1m'

            try:
                gain = args[1]
            except IndexError:
                gain = False

            print(calculate_trends(timeperiod, float(gain)))

    if (subroutine == 'gainers'):
        import lab.macro.gainers


def news_controller(subroutine, args=[]):
    if (subroutine == 'scrape'):
        from lab.news.scrape_headlines import scrape_news
        if (args):
            query = args[0]            
        else:
            query="best+stocks+to+buy+this+week"
        
        print(scrape_news(query))


def pricedingold_controller(args):
    if (args):
        from lab.pricedingold.compare import price_in_gold
        ticker = args[0]

        try:
            timespan = args[1]
        except IndexError:
            timespan = '5y'

        try:
            test = args[2]
        except IndexError:
            test = False

        print(price_in_gold(ticker, timespan, test))


def hurst_controller(args):
    if (args):
        from lab.rescaledrange.fractal_calculator import fractal_calculator
        ticker = args[0]
        output = args[1] if (len(args) > 1) else 'table'

        print(fractal_calculator(ticker, output))



def range_controller(args):
    from lab.riskrange.lookup import rangeLookup
    if (args):
        ticker = args[0]
        tweet = args[1] if (len(args) > 1) else False

        print(rangeLookup(ticker, tweet))



def twitter_controller(subroutine, args):
    if (subroutine == 'follow'):
        from lab.fintwit.user import followFollowers
        if (args):
            handle = args[0]
            index = args[1] if (len(args) > 1) else 0
            if (index == 'restart'):
                print(followFollowers(handle, 0))
            else:
                print(followFollowers(handle, index))

    if (subroutine == 'trim'):
        from lab.fintwit.user import trimFollowers
        if (args and args[0] == 'restart'):
            print(trimFollowers(0))
        else:
            print(trimFollowers())


def trend_controller(subroutine, args):
    if (args):
        if (subroutine == 'pricetarget'):
            # TODO: Finish price targets
            from lab.trend.pricetarget import lookup
            print(lookup(args[0]))
        if (subroutine == 'search'):
            from lab.trend.search import search
            print(search(args[0]))

    if (subroutine == 'chase'):
        import lab.trend.chase

    if (subroutine == 'earnings'):
        import lab.trend.chase_earnings

    if (subroutine == 'volume'):
        import lab.trend.chase_volume

    if (subroutine == 'gainers'):
        import lab.trend.gainers


def vix_controller(args):
    if (args):
        ticker = args[0]
        from lab.vix.calculation import vix_calculation
        print(vix_calculation(ticker))


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lab.settings')
    sys.argv.pop(0)

    args = [arg.strip() for arg in sys.argv]

    if (args[0] == 'list'):
        list_commands()
        return

    if (':' in args[0]):
        command = args.pop(0)
        program = command.split(':')[0] + "_controller"
        subroutine = command.split(':')[1]

        globals()[program](subroutine, args)
        return
    else:
        program = args.pop(0) + "_controller"

        globals()[program](args)
        return

    print("Error: your command did not match any known programs. Closing...")
    return


if __name__ == '__main__':
    main()
