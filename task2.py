import requests
import csv
import datetime
from math import sqrt

input_file = 'tickers.csv'
output_file = 'tickers_output.csv'

# numbers of columns in response table from moex
tradedata_id = 1
close_price_id = 11     # field: close
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
volatility = dict()


def company_info(ticker, start_date, end_date):
    # get last availabe price
    url_lp = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/" + ticker + \
             ".json?iss.meta=off&marketdata.columns=LAST"
    try:
        last_available_price = requests.get(url_lp).json()["marketdata"]["data"][0][0]
        writer.writerow({fn_shortticker: ticker, fn_tradedate: today, fn_closeprice: None, fn_movavrg: None,
                         fn_last_available_price: last_available_price})
    except:
        print(ticker + ": Last Price not Found")

    last_available_price = None

    url = "http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqbr/securities/" + ticker + \
          ".json?iss.meta=off&from=" + start_date + "&till=" + end_date + "&start=0"

    response_data = []

    # initialize parameters for moving average
    mov_avrg = None
    days_count = 0
    price_sum = 0

    # initialize parameters for historical volatility
    prices_list = list()
    f = True

    try:
        response_data = requests.get(url).json()['history']['data']
        if len(response_data) == 0:
            print(ticker + ": Info not found")
        else:
            print(ticker)
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

                if days_count == period:
                    mov_avrg = price_sum / period
                    #print("Mov avrg: " + str(mov_avrg))
                if days_count > period:
                    prev_price = prices_list[len(prices_list) - period - 1]
                    mov_avrg = mov_avrg + (price - prev_price) / period
                    #print(price, prev_price)
                    #print("Mov avrg: " + str(mov_avrg))

            if mov_avrg is not None:
                 res_mov_avrg = round(mov_avrg, 2)
                 #print(res_mov_avrg)
            else:
                res_mov_avrg = None

            writer.writerow({fn_shortticker: ticker, fn_tradedate: date, fn_closeprice: price, fn_movavrg: res_mov_avrg,
                             fn_last_available_price: last_available_price})

        # make another request for next 100 rows
        url = "http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqbr/securities/" + ticker + \
              ".json?iss.meta=off&from=" + start_date + "&till=" + end_date + "&start=" + str(start)
        try:
            response_data = requests.get(url).json()['history']['data']
        except Exception as err:
            print("Error: " + str(err))
        # --------------------------------------
        start += 100

    if days_count != 0:
        av_price = price_sum / days_count
        vol = 0
        for p in prices_list:
            vol += (av_price - p)**2
        volatility[ticker] = round(sqrt(vol/days_count), 2)
    # print(prices_list)
    # print(av_price)
    # print(days_count)


# add tickers from tickers.csv to list
tickers_list = list()
with open(input_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for csv_line in reader:
        tickers_list.append(csv_line["ticker_short"])

#print(tickers_list)

st = '2017-03-01'

# fill in tickers list
# for ticker in tickers_list:
#    company_info(ticker, st, today)

company_info('zhiv', st, today)
print(volatility)

fout.close()