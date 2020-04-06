import requests
import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
from matplotlib.backends.backend_pdf import PdfPages

input_file = 'tickers.csv'
output_file = 'tickers_output-2.csv'

# numbers of columns in response table from iss.moex.com
tradedata_id = 1
close_price_id = 9     # field: legal close price
ticker_id = 3

# inner names of columns for output_file
fn_shortticker = 'short_ticker'
fn_tradedate = 'trade_date'
fn_closeprice = 'close_price'
fn_last_available_price = 'last_price'
fn_movavrg = 'moving average'

today = datetime.datetime.today().strftime("%Y-%m-%d")

# write headers to output file
fout = open(output_file, 'w', newline='')
fieldnames = [fn_shortticker, fn_tradedate, fn_closeprice, fn_movavrg, fn_last_available_price]
writer = csv.DictWriter(fout, fieldnames=fieldnames)
writer.writeheader()


# moving average
period = 14 # days

# volatility
volatility_file = 'volatility.csv'
vol_file = open(volatility_file, 'w', newline='')
fieldnames_vol = ['ticker', 'vol', 'start_date', 'end_date', 'days_count']
writer_vol = csv.DictWriter(vol_file, fieldnames=fieldnames_vol)
writer_vol.writeheader()
volatility = dict()
vol_np = dict()


def company_info(ticker, start_date, end_date):
    url = "http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqbr/securities/" + ticker + \
          ".json?iss.meta=off&from=" + start_date + "&till=" + end_date + "&start=0"
    response_data = []

    # initialize parameters for moving average
    mov_avrg = None
    days_count = 0
    price_sum = 0

    # initialize parameters for historical volatility
    prices_list = list()
    price_proc_list = list()
    dates_list = list() # date format

    try:
        response_data = requests.get(url).json()['history']['data']
        if len(response_data) == 0:
            print(ticker + ": No data for choosed period")
        else:
            print(ticker + ": OK!")
            start_vol_date = response_data[0][tradedata_id]
            prev_price = response_data[0][close_price_id]

    except Exception as err:
        print("Error: " + str(err))

    start = 100
    while len(response_data) > 0:
        for i in range(len(response_data)):
            date = response_data[i][tradedata_id]
            price = response_data[i][close_price_id]

            # calculate simple moving average
            if price is not None:
                days_count += 1
                price_sum += price
                prices_list.append(price)
                dates_list.append(datetime.datetime.strptime(date, '%Y-%m-%d').date())
                price_proc_list.append(price/prev_price)

                if days_count == period:
                    mov_avrg = price_sum / period
                if days_count > period:
                    prev_price = prices_list[len(prices_list) - period - 1]
                    mov_avrg = mov_avrg + (price - prev_price) / period

            if mov_avrg is not None:
                 res_mov_avrg = round(mov_avrg, 2)
                 #print(res_mov_avrg)
            else:
                res_mov_avrg = None

            writer.writerow({fn_shortticker: ticker, fn_tradedate: date, fn_closeprice: price, fn_movavrg: res_mov_avrg})

        # make another request for next 100 rows
        url = "http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqbr/securities/" + ticker + \
              ".json?iss.meta=off&from=" + start_date + "&till=" + end_date + "&start=" + str(start)
        try:
            response_data = requests.get(url).json()['history']['data']
        except Exception as err:
            print("Error: " + str(err))
        # --------------------------------------
        start += 100


    # get last availabe price
    url_lp = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/" + ticker + \
             ".json?iss.meta=off&marketdata.columns=LAST"
    try:
        last_available_price = requests.get(url_lp).json()["marketdata"]["data"][0][0]
        print(type(last_available_price))
        if last_available_price is not None:
            writer.writerow({fn_shortticker: ticker, fn_tradedate: today, fn_closeprice: last_available_price, fn_movavrg: None})
    except IndexError:
        print(ticker + ": Cannot find last price")
    except ConnectionError as err:
        print(str(err))
    last_available_price = None

    # calculate volatility
    if days_count != 0:
        vol_np[ticker] = round(np.std(price_proc_list)*100, 2)
        writer_vol.writerow({'ticker':ticker,
                             'vol':round(vol_np[ticker], 2),
                             'start_date': start_vol_date,
                             'end_date': date,
                             'days_count': days_count})
    #print(dates_list)
    #lineplot_with_date(dates_list, prices_list, "Dates", "Prices", ticker + " prices chart")


# add tickers from tickers.csv to list
tickers_list = list()
with open(input_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for csv_line in reader:
        tickers_list.append(csv_line["ticker_short"])

st = '2017-03-02'   # start date

# fill in tickers list
# for ticker in tickers_list:
#    company_info(ticker, st, today)

company_info('yndx', st, today)
# company_info('zill', st, today)
company_info('aflt', st, today)

fout.close()
vol_file.close()


#-----------------------------------------------------------------------
# Find tickers and make plots for them
vol_np = {k: v for k, v in sorted(vol_np.items(), key=lambda item: item[1], reverse=True)}
tickers_for_plots = [list(vol_np.keys())[0], list(vol_np.keys())[1]]
print(tickers_for_plots)
# first_ticker = list(vol_np.keys())[0]
# second_ticker = list(vol_np.keys())[1]


def lineplot_with_date(x_data, y_data, x_label="", y_label="", title=""):
    # Create the plot object
    _, ax = plt.subplots()
    x_data_float = matplotlib.dates.date2num(x_data)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%Y-%m"))

    #ax = plt.subplot(2,1,idx+1)
    ax.plot(x_data_float, y_data, lw=2, color='#539caf', alpha=1)

    # Label the axes and provide a title
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.grid()
    pdf.savefig()
    plt.close()


ticker_prices_dict = {tickers_for_plots[0]: list(), tickers_for_plots[1]: list()}
ticker_dates_dict = {tickers_for_plots[0]: list(), tickers_for_plots[1]: list()}


def prepare_data_for_plots():
    with open(output_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for csv_line in reader:
            if csv_line[fn_shortticker] in tickers_for_plots:
                tick = str(csv_line[fn_shortticker])
                ticker_dates_dict[tick].append( datetime.datetime.strptime(csv_line[fn_tradedate], '%Y-%m-%d').date() )
                ticker_prices_dict[tick].append( float(csv_line[fn_closeprice]) )


prepare_data_for_plots()
#print(ticker_prices_dict['yndx'])


with PdfPages('plot.pdf') as pdf:
    lineplot_with_date(ticker_dates_dict[ tickers_for_plots[0] ],
                   ticker_prices_dict[ tickers_for_plots[0] ],
                   "Dates",
                   "Prices",
                   tickers_for_plots[0] + " prices chart")

    lineplot_with_date(ticker_dates_dict[ tickers_for_plots[1] ],
                   ticker_prices_dict[ tickers_for_plots[1] ],
                   "Dates",
                   "Prices",
                   tickers_for_plots[1] + " prices chart")

#pdf.savefig()