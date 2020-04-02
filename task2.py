import json
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
fn_movavrg = 'moving average'

today = datetime.datetime.today().strftime("%Y-%m-%d")
print(today)


def company_info(ticker):
    url = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/" + ticker + ".json?iss.meta=off&marketdata.columns=LAST"
    response_json = requests.get(url).json()
    try:
        print(ticker + ": " + str(response_json["marketdata"]["data"][0][0]))
    except Exception:
        print(ticker + ": " + "Not found")


# add tickers from tickers.csv to list
tickers_list = list()
with open(input_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for csv_line in reader:
        tickers_list.append(csv_line["ticker_short"])

#print(tickers_list)


# output ticker
# for ticker in tickers_list:
#     company_info(ticker)




url = "http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqbr/securities/AFLT.json?iss.meta=off&from=2017-03-31&start=0"
response_data = []
try:
    response_data = requests.get(url).json()['history']['data']
except Exception as err:
    print("Error: " + str(err))

#print(response_json['history']['data'][0][1])

with open(output_file, 'w', newline='') as csvfile:
    fieldnames = [fn_shortticker, fn_tradedate, fn_closeprice]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()

    f = False
    start = 100
    while len(response_data) > 0:
        for i in range(len(response_data)):
            ticker = response_data[i][ticker_id]
            date = response_data[i][tradedata_id]
            price = float(response_data[i][close_price_id])
            writer.writerow({fn_shortticker: ticker, fn_tradedate: date, fn_closeprice: price})
            print(date)

        url = "http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/tqbr/securities/AFLT.json?iss.meta=off&from=2017-03-31&start=" + str(start)
        try:
            response_data = requests.get(url).json()['history']['data']
        except Exception as err:
            print("Error: " + str(err))

        start += 100

