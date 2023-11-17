from flask import *
from flask_cors import CORS
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import date
import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np
import sklearn as sk
import seaborn as sns
import pandas as pd

app = Flask(__name__)
CORS(app)
# Required
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "stock_price"
mysql = MySQL(app)


@app.route("/getCompanies/", methods=['GET'])
def get_companies():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("select distinct(company_name),code from companies")
    company_list = cur.fetchall()
    return jsonify(company_list)


@app.route("/getCompanyInfo/", methods=['POST'])
def get_company():
    code = request.form['code']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute(
        "select * from stock_index where index_id in (select index_id from companies where code='" + code + "')")
    company_list = cur.fetchall()
    return jsonify(company_list)


@app.route("/predict/", methods=['POST'])
def predict_price():
    code = request.form['code']
    open_value = request.form['open']
    high_value = request.form['high']
    low_value = request.form['low']
    start_date = date.today()
    year = date.today().year
    y = int(year) - 10
    end_date = str(start_date.strftime(str(y) + '-%m-%d'))
    end = pd.to_datetime(end_date)
    data = yf.download(code + ".BO", start=end, end=start_date)
    dataset = pd.DataFrame(data)
    print(dataset.tail())
    x = dataset.drop(['Adj Close', 'Volume', 'Close'], axis=1).values
    y = dataset['Close'].values
    m = LinearRegression()
    m.fit(x, y)
    prediction = m.predict([np.array([open_value, high_value, low_value], dtype=np.float64)])
    print(prediction)
    return jsonify(predicted=round(prediction[0], 2))


@app.route("/getIndexes/", methods=['GET'])
def get_indexes():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("select * from stock_index")
    index_list = cur.fetchall()
    return jsonify(index_list)


@app.route("/randomIndexes/", methods=['GET'])
def get_random_indexes():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("select * from stock_index limit 4")
    index_list = cur.fetchall()
    return jsonify(index_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
