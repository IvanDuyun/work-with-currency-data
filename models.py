from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Integer, String, \
    Column, DateTime, ForeignKey, Float

engine = create_engine('sqlite:///currency.db', echo=False)
session = sessionmaker(bind=engine)
Base = declarative_base()

class Currency(Base):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True)
    alphabetic_code = Column(String)
    country = Column(String)
    numeric_code = Column(String)
    name = Column(String)


class CurrencyPair(Base):
    __tablename__ = 'currency_pair'

    id = Column(Integer, primary_key=True)
    first_curr = Column(Integer, ForeignKey('currency.id'))
    second_curr = Column(Integer, ForeignKey('currency.id'))
    bid = Column(Float)
    ask = Column(Float)
    datetime = Column(DateTime)

Base.metadata.create_all(engine)