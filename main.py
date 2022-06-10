import investpy
from models import session, Currency, CurrencyPair
import pandas
from datetime import datetime
import threading
from sqlalchemy import func

def read_iso4217():
    excel_data_df = pandas.read_excel('iso4217.xls', sheet_name='Active', skiprows=3)
    alphabetic_code = excel_data_df['Alphabetic Code'].tolist()
    country = excel_data_df['ENTITY'].tolist()
    numeric_code = excel_data_df['Numeric Code'].tolist()
    name = excel_data_df['Currency'].tolist()
    return alphabetic_code, country, numeric_code, name

def write_all_currencies_in_db(session):
    """Используется один раз для добавления в БД данных по кодам валют"""
    alphabetic_code, country, numeric_code, name = read_iso4217()
    for i in range(len(alphabetic_code)):
        currency = Currency(
                    id=i,
                    alphabetic_code=alphabetic_code[i],
                    country=country[i],
                    numeric_code=numeric_code[i],
                    name=name[i]
                    )
        session.add(currency)
    session.commit()

def write_currency_pair_in_db(session, df, n_results):
    for i in range(n_results):
        currency_pair = CurrencyPair(
            first_curr=df.at[i, 'symbol'][:3],
            second_curr=df.at[i, 'symbol'][4:],
            bid=df.at[i, 'bid'],
            ask=df.at[i, 'ask'],
            datetime=datetime.now()
        )
        session.add(currency_pair)
    session.commit()

def get_currency_pair(alphabetic_code, n_results):
    """Возрващает n_results записей по валютным парам с участием code_currency;
       ask и bid имеют значения на момент вызова"""
    return investpy.currency_crosses.get_currency_crosses_overview(alphabetic_code, n_results=n_results)

def get_and_write_currency_pair(session, alphabetic_code, n_results):
    """Пример вызова: get_and_write_currency_pair(session(), 'RUB', 1)"""
    df = get_currency_pair(alphabetic_code, n_results)
    write_currency_pair_in_db(session, df, n_results)

def repeated_timer():
    """Запись данных по выбранной валюте в БД по таймеру"""
    threading.Timer(1.0, repeated_timer).start()
    get_and_write_currency_pair(session(), 'USD', 1)

def list_input():
    a, b, c, d = input().split()
    return a, datetime.strptime(b, "%d.%m.%Y"), datetime.strptime(c, "%d.%m.%Y"), int(d)

def list_currency_print(session):
    print('Введите код валюты, диапазон дат и количество записей; \n'
          'например, "RUB 01.06.2022 20.06.2022 5"; \n'
          'вывести все записи: "RUB 01.06.2022 20.06.2022 -1";')
    alphabetic_code, date_from, date_before, limit = list_input()
    result = session.query(CurrencyPair).filter(
        CurrencyPair.datetime.between(date_from, date_before),
        CurrencyPair.second_curr == alphabetic_code).limit(limit).all()
    if not result:
        print('По данной валюте в выбранном диапозоне времени нет данных')
    if limit >= 0:
        print('Count = '+str(len(result)))
    for i in range(len(result)):
        print(result[i].first_curr+'/'+result[i].second_curr,
              result[i].ask, result[i].bid, result[i].datetime)

def min_max_input():
    a, b, c = input().split()
    return a, datetime.strptime(b, "%d.%m.%Y"), datetime.strptime(c, "%d.%m.%Y")

def min_max_currency_print(session):
    print('Введите код валюты, диапазон дат; \n'
          'например, "RUB 01.06.2022 20.06.2022";')
    alphabetic_code, date_from, date_before = min_max_input()
    max = session.query(CurrencyPair).filter(
        CurrencyPair.datetime.between(date_from, date_before),
        CurrencyPair.second_curr == alphabetic_code).group_by(CurrencyPair.first_curr).having(func.max(CurrencyPair.ask)).all()
    min = session.query(CurrencyPair).filter(
        CurrencyPair.datetime.between(date_from, date_before),
        CurrencyPair.second_curr == alphabetic_code).group_by(CurrencyPair.first_curr).having(func.min(CurrencyPair.ask)).all()
    if not max or not min:
        print('По данной валюте в выбранном диапозоне времени нет данных')
    for i in range(len(max)):
        print('max:', max[i].first_curr + '/' + max[i].second_curr,
              max[i].ask, max[i].bid, max[i].datetime)
        print('min:', min[i].first_curr + '/' + min[i].second_curr,
              min[i].ask, min[i].bid, min[i].datetime)

#repeated_timer()
list_currency_print(session())
#min_max_currency_print(session())
