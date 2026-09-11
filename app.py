import sqlite3
from flask import Flask, render_template, request
from finance import show_analysis

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == "POST":

        symbol = request.form["symbol"].upper()
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        with sqlite3.connect("finance.db") as conn:
            cursor = conn.cursor()

            result = None
            message = None
            rows = []
            symbol_rows = []
            graph = []

            if symbol == "":
                message = "銘柄コードが入力されていません"

            elif start_date == "" or end_date == "":
                message = "日付が入力されていません"

            elif start_date > end_date:
                message = "「開始日は終了日より前の日付を指定してください」"

            else:
                cursor.execute("""
                    SELECT symbol
                    FROM stock_prices
                    WHERE symbol = ?
                """,(symbol,))

                symbol_rows = cursor.fetchall()

                cursor.execute("""
                    SELECT symbol, date, open, high, low, close, volume
                    FROM stock_prices
                    WHERE symbol = ?
                    AND date BETWEEN ? AND ?
                """,(symbol, start_date, end_date))

                rows = cursor.fetchall()

                cursor.execute("""
                    SELECT date, close
                    FROM stock_prices
                    WHERE symbol = ?
                    AND date BETWEEN ? AND ?
                    ORDER BY date ASC
                    """,(symbol, start_date, end_date))

                graph = cursor.fetchall()
                print(graph)

                if not symbol_rows:
                    message = "該当する銘柄が見つかりません"

                elif not rows:
                    message = "指定期間のデータが見つかりません"

                elif len(rows) <= 1:
                    message = "前日比を計算するため、2日以上の期間を指定してください"

                else:
                    result = show_analysis(cursor, symbol, start_date, end_date)

        return render_template("index.html", symbol=symbol, rows=rows, graph=graph, result=result, message=message)

    return render_template("index.html", graph=[])

if __name__ == "__main__":
    app.run()