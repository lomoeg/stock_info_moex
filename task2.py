import requests
import csv
import datetime

input_file = 'tickers.csv'
output_file = 'tickers_output.csv'

# numbers of columns in response table from moex
tradedata_id = 1
close_price_id = 11
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


def company_info(ticker, start_date, end_date):
    # get last availabe price
    url_lp = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/" + ticker + \
             ".json?iss.meta=off&marketdata.columns=OFFER"
    try:
        last_available_price = requests.get(url_lp).json()["marketdata"]["data"][0][0]
    except:
        print(ticker + ": Not Found")
        last_available_price = None

    url = "http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqbr/securities/" + ticker + \
          ".json?iss.meta=off&from=" + start_date + "&till=" + end_date + "&start=0"

    response_data = []
    mov_avrg = None
    days_count = 0
    price_sum = 0
    prev_price = 0

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
            #ticker = response_data[i][ticker_id]
            date = response_data[i][tradedata_id]
            price = response_data[i][close_price_id]

            if price is not None:
                if days_count < 14:
                    price_sum += price
                    prev_price = price
                    days_count += 1
                if days_count == 14:
                    mov_avrg = round(price_sum / period, 2)
                    days_count += 1
                if days_count > 14:
                    mov_avrg = round(mov_avrg + (price - prev_price) / period, 2)

            writer.writerow({fn_shortticker: ticker, fn_tradedate: date, fn_closeprice: price, fn_movavrg: mov_avrg,
                             fn_last_available_price: last_available_price})
            #print(ticker + ": " + date)

        url = "http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqbr/securities/" + ticker + \
              ".json?iss.meta=off&from=" + start_date + "&till=" + end_date + "&start=" + str(start)
        try:
            response_data = requests.get(url).json()['history']['data']
        except Exception as err:
            print("Error: " + str(err))

        start += 100


# add tickers from tickers.csv to list
tickers_list = list()
with open(input_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for csv_line in reader:
        tickers_list.append(csv_line["ticker_short"])

#print(tickers_list)

st = '2020-03-31'

# fill in tickers list
for ticker in tickers_list:
    company_info(ticker, st, today)

#company_info('aflt', st, today)

fout.close()