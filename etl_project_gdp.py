# Code for ETL operations on Country-GDP data

# Importing the required libraries
from bs4 import BeautifulSoup
import requests as rq
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime 

url ='https://web.archive.org/web/20230902185326/https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29'

table_attribs = ["Country", "GDP_USD_millions"]
db_name = 'World_Economies.db'
table_name = 'Countries_by_GDP'
csv_path = 'Countries_by_GDP.csv'
log_txt = 'etl_project_log.txt'


#tables = data.find_all('tbody') #нашла таблицу
#rows = tables[2].find_all('tr')    # выбираю нужную таблицу по индексу

def extract(url, table_attribs):

    df = pd.DataFrame(columns=table_attribs) #millions 
    html_page = rq.get(url).text
    data =BeautifulSoup(html_page, 'html.parser')
    tables = data.find('tbody')
    rows = tables.find_all('tr')  # Извлекаем все строки из 1 таблицы [0]
    for i in rows:
        col = i.find_all('td') #ячейки
        if len(col) !=0:
            country = col[0].get_text(strip=True)  #str(col[0].contents[0])
            gdp_text = col[2].contents[0].replace(",", "")
            if gdp_text =="—":
                gdp_text = 0
            else:
                gdp_text = float(gdp_text)        
                  
            data_country = {"Country":country, # Создаём словарь с данными из ячеек
                          "GDP_USD_millions":gdp_text}
             # Преобразование словаря в датафрейм и объединение его с существующим
            # данные продолжают добавляться в датафрейм с каждой итерацией цикла
            df1 = pd.DataFrame(data_country, index =[0]) 
            df = pd.concat([df,df1],ignore_index=True) #конкатенация двух БД
    return df

def transform(df):
    ''' This function converts the GDP information from Currency
    format to float value, transforms the information of GDP from
    USD (Millions) to USD (Billions) rounding to 2 decimal places.
    The function returns the transformed dataframe.'''

    df['GDP_USD_millions'] = round(df['GDP_USD_millions']/1000,2)
    df = df.rename(columns={'GDP_USD_millions': "GDP_USD_billions"})
    return df

def load_to_csv(df, csv_path):
    ''' This function saves the final dataframe as a `CSV` file 
    in the provided path. Function returns nothing.'''
    df.to_csv(csv_path)

def load_to_db(df, sql_con, table_name):
    ''' This function saves the final dataframe as a database table
    with the provided name. Function returns nothing.'''
    df.to_sql(table_name,sql_con,if_exists='replace', index =False)
    print('table is ready')


def run_query(query_statement, sql_con):
    ''' This function runs the stated query on the database table and
    prints the output on the terminal. Function returns nothing. '''
    print(query_statement)
    query_output = pd.read_sql(query_statement,  sql_con)
    print(query_output)
    sql_con.close()

def log_progress(message):
    time_now = datetime.now()
    time_stamp = time_now.strftime("%y-%m-%d-%H:%M:%S")
    with open (log_txt, 'a' ) as log_f:
        log_f.write(f'{time_stamp}: {message} \n')
    

log_progress("Start")
extract_data =  extract(url, table_attribs)
log_progress("transform")
transform_data = transform(extract_data)
log_progress("load csv")
load_to_csv(transform_data, csv_path)
log_progress('connect sql')
sql_con = sqlite3.connect(db_name)
log_progress('load bd')
load_to_db(transform_data,sql_con, table_name)
log_progress('sql')
query_statement = f"SELECT * FROM {table_name} where GDP_USD_billions>=100 "
run_query(query_statement, sql_con)
log_progress('Process Complete.')

