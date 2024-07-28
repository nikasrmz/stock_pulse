from flask import Flask, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pymongo import MongoClient

app = Flask(__name__)

# PostgreSQL setup
POSTGRES_DB = os.environ['POSTGRES_DB']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_PORT = os.environ['POSTGRES_PORT']

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class StockPrice(Base):
    __tablename__ = 'stock_prices'
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    timestamp = Column(DateTime)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


Base.metadata.create_all(engine)

# MongoDB setup
MONGO_HOST = os.environ['MONGO_HOST']
MONGO_PORT = int(os.environ['MONGO_PORT'])

client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client.financial_data
news_collection = db.news


@app.route('/')
def hello_world():
    return 'Hello, StockPulse!'


@app.route('/stock_prices/<symbol>', methods=['GET'])
def get_stock_prices(symbol):
    stock_prices = session.query(StockPrice).filter_by(symbol=symbol).all()
    result = [{'timestamp': sp.timestamp, 'open': sp.open, 'high': sp.high, 'low': sp.low, 'close': sp.close, 'volume': sp.volume} for sp in stock_prices]
    return jsonify(result)


@app.route('/news/<symbol>', methods=['GET'])
def get_news(symbol):
    news_articles = news_collection.find({'symbol': symbol})
    result = [{'title': article['title'], 'content': article['content'], 'published_at': article['published_at']} for article in news_articles]
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
