import requests
import sqlite3

api_key = "JC6KMVZYZ4OGFS6G."

url = "https://www.alphavantage.co/query"

conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        UNIQUE (symbol, date)
        )
    """)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        company_name TEXT,
        UNIQUE (symbol)
        )
    """)

# APIから株価データを取得
def get_stock_data(symbol):

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": "あなたのAPIキー"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "Information" in data:
        print("APIの利用制限に達しました")
        exit()

    if "Time Series (Daily)" not in data:
        print("株価データを取得できませんでした")
        exit() 

    daily_data = data["Time Series (Daily)"]

    stock_data = []

    for date in daily_data:
        open_price = float(daily_data[date]["1. open"])
        high_price = float(daily_data[date]["2. high"])
        low_price = float(daily_data[date]["3. low"])
        close_price = float(daily_data[date]["4. close"])
        volume = int(daily_data[date]["5. volume"])

        record = {
            "date": date,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume
        }
        stock_data.append(record)

    return stock_data
# SQLiteへ保存
def save_stock_data(symbol, stock_data):
    for record in stock_data:
        cursor.execute("""
            INSERT OR IGNORE INTO stock_prices
            (symbol, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                record['date'],
                record['open'],
                record['high'],
                record['low'],
                record['close'],
                record['volume']
            ))
    conn.commit()

# 最高値・最低値・平均・前日比を表示
def show_analysis(cursor, symbol, start_date, end_date):
    
# 始値データを取り出す処理
    cursor.execute("""
        SELECT open
        FROM stock_prices
        WHERE symbol = ?
        AND date BETWEEN ? AND ?
        ORDER BY date ASC
        LIMIT 1
    """, (symbol, start_date, end_date))

    open_price = cursor.fetchone()

    if  not open_price:
        print("該当するデータがありません")
        return
    
# 高値データを取り出す処理
    cursor.execute("""
        SELECT MAX(high) 
        FROM stock_prices
        WHERE symbol = ?
        AND date BETWEEN ? AND ?
    """, (symbol, start_date, end_date))

    high_price = cursor.fetchone()

    if  high_price[0] is None:
        print("該当するデータがありません")
        return

# 低値データを取り出す処理
    cursor.execute("""
        SELECT MIN(low)
        FROM stock_prices
        WHERE symbol = ?
        AND date BETWEEN ? AND ?
    """, (symbol, start_date, end_date))

    low_price = cursor.fetchone()

    if  low_price[0] is None:
        print("該当するデータがありません")
        return

# 終値データを取り出す処理
    cursor.execute("""
        SELECT close
        FROM stock_prices
        WHERE symbol = ?
        AND date BETWEEN ? AND ?
        ORDER BY date DESC
        LIMIT 1
    """, (symbol, start_date, end_date))

    close_price = cursor.fetchone()

    if  not close_price:
            print("該当するデータがありません")
            return

# 平均終値データを取り出す処理
    cursor.execute("""
        SELECT AVG(close)
        FROM stock_prices
        WHERE symbol = ?
        AND date BETWEEN ? AND ?
    """, (symbol, start_date, end_date))

    avg_price = cursor.fetchone()

    if avg_price[0] is None:
        print("該当するデータがありません")
        return

# 期間中の価格差
    change = close_price[0] - open_price[0]

# 期間中の変動率
    change_rate = change / open_price[0] * 100

# 前日比データの処理
    cursor.execute("""
        SELECT date, close
        FROM stock_prices
        WHERE symbol = ?
        AND date BETWEEN ? AND ?
        ORDER BY date DESC
        LIMIT 1
    """, (symbol, start_date, end_date))

    latest_data = cursor.fetchone()

    if not latest_data:
        print("該当するデータがありません")
        return

    cursor.execute("""
        SELECT date, close
        FROM stock_prices
        WHERE symbol = ?
        AND date BETWEEN ? AND ?
        ORDER BY date DESC
        LIMIT 1 OFFSET 1
    """, (symbol, start_date, end_date))

    close_price2 = cursor.fetchone()

    if not close_price2:
        print("該当するデータがありません")
        return

    daily_change = latest_data[1] - close_price2[1]

    compare = daily_change / close_price2[1] * 100

    result = {
        "open": open_price[0],
        "high": high_price[0],
        "low": low_price[0],
        "close": close_price[0],
        "avg": avg_price[0],
        "change": change,
        "change_rate": change_rate,
        "latest_data": latest_data[0],
        "previous_date": close_price2[0],
        "compare": compare
    }

    return result

# 検索処理
def search_stock(symbol):
    search_date = input("検索する日付を入力してください: ")

    if not search_date:
        print("日付が入力されていません")
        return

    cursor.execute("""
        SELECT * FROM stock_prices WHERE symbol = ? AND date = ?""", (symbol, search_date))

    row = cursor.fetchone()

    if not row:
        print("該当するデータが見つかりません")
        return
    
    print(f"日付: {row[2]}")
    print(f"始値: {row[3]}")
    print(f"高値: {row[4]}")
    print(f"低値: {row[5]}")
    print(f"終値: {row[6]}")
    print(f"出来高: {row[7]}")
# 銘柄コード入力
def input_stock():

    code = input("銘柄コードを入力してください: ")

    if not code:
        print("銘柄コードが入力されていません")
        return
    
    return code
# 二つ目の銘柄コードを入力
def input_stocks():

    codes = input("もう1つの銘柄コードを入力してください: ")

    if not codes:
        print("銘柄コードが入力されていません")
        return
    
    return codes

if __name__ == "__main__":
    symbol = input_stock()
    symbol2 = input_stocks()

    symbols = [symbol, symbol2]

    results = []

    start_date = input("分析開始日を入力してください: ")
    if not start_date:
        print("分析開始日が入力されていません")

    end_date = input("分析終了日を入力してください: ")
    if not end_date:
        print("分析終了日が入力されていません")

    print("\n========== 株価分析結果 ==========")
    for i, symbol in enumerate(symbols):

        stock_data = get_stock_data(symbol)

        save_stock_data(symbol, stock_data)

        result = show_analysis(cursor, symbol, start_date, end_date)
        
        results.append(result)

        print(f"{symbol} : {result:.2f}%")

    max_index = results.index(max(results))
    print(f"最も上昇した銘柄: {symbols[max_index]}")

    search_stock(symbol)
    print("================================")
    conn.close()