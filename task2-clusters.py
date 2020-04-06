from sklearn import datasets
from sklearn.cluster import KMeans
import csv
import math

input_file = 'tickers.csv'
output_file = 'stock_info.csv'

# inner names of columns for output_file
fn_shortticker = 'short_ticker'
fn_tradedate = 'trade_date'
fn_closeprice = 'close_price'
fn_last_available_price = 'last_price'
fn_movavrg = 'moving average'

ticker_prices_dict = dict()
ticker_dates_dict = dict()

# add tickers from tickers.csv to list
tickers_list = list()
with open(input_file, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for csv_line in reader:
        tickers_list.append(csv_line["ticker_short"])
        ticker_prices_dict[csv_line["ticker_short"]] = list()
        ticker_dates_dict[csv_line["ticker_short"]] = list()


# ticker_prices_dict[ticker] - list with all prices
def prepare_data_for_clusters():
    with open(output_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for csv_line in reader:
            # print(csv_line)
            if csv_line[fn_shortticker] in tickers_list:
                tick = str(csv_line[fn_shortticker])
                if csv_line[fn_closeprice] != '':
                    ticker_prices_dict[tick].append(float(csv_line[fn_closeprice]))


prepare_data_for_clusters()
dataset = []
for ticker in ticker_prices_dict.keys():
    prices = ticker_prices_dict[ticker]
    if len(prices) == 781:
        prev = prices[0]
        l = []
        for p in prices:
            l.append(math.log(p) - math.log(prev))
            prev = p
        dataset.append(l)

for i in range(len(dataset)):
    print(dataset[i])

#print(dataset)
#iris_df = datasets.load_iris()
# print(iris_df.data)
model = KMeans(n_clusters=20, max_iter=1000000)

# Проводим моделирование
model.fit(dataset)

# Предсказание на единичном примере
#predicted_label = model.predict([[7.2, 3.5, 0.8, 1.6]])

# Предсказание на всем наборе данных
all_predictions = model.predict(dataset)

# Выводим предсказания
# print(predicted_label)
print(all_predictions)