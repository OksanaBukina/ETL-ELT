import pandas as pd 
import xml.etree.ElementTree as ET 
from datetime import datetime 
import glob 

log_file = "log_file.txt" 
target_file = "transformed_data.csv" 
# формат csv,json,xml
def extract_from_csv(file_to_process): 
    dataframe = pd.read_csv(file_to_process) 
    return dataframe 

def extract_from_json(file_to_process): 
    dataframe = pd.read_json(file_to_process, lines=True) 
    return dataframe


def extract_from_xml(file_to_process):
    dataframe = pd.DataFrame(columns=['model', 'year', 'price', 'fuel'])
    tree = ET.parse(file_to_process) 
    root = tree.getroot() 
    for person in root:
        car_model = person.findtext("car_model")
        year_of_manufacture = person.findtext("year_of_manufacture")
        price = person.findtext("price")
        fuel = person.findtext("fuel")
        dataframe = pd.concat([dataframe,
             pd.DataFrame([{"model":car_model, "year":int(year_of_manufacture) if year_of_manufacture else None,
                             "price":float(price) if price else None,
                             "fuel":fuel}])], ignore_index=True) 
    return dataframe 

# перебираем все файлы , вызываем функцию конвертации и собираем все в один DB , все что сконвертировали с разных форматов
def extract(): 
    df = pd.DataFrame(columns=['model', 'year', 'price', 'fuel'])
    for csv_ex in glob.glob("*.csv"):
        if csv_ex != target_file:
            df = pd.concat([df,pd.DataFrame(extract_from_csv(csv_ex))],ignore_index=True)

    for xml_ex in glob.glob("*.xml"):
        df = pd.concat([df,pd.DataFrame(extract_from_xml(xml_ex))],ignore_index=True)

    for json_ex in glob.glob("*.json"):
        df = pd.concat([df,pd.DataFrame(extract_from_json(json_ex))],ignore_index=True)
    return df
# трансформация, округлили цену 
def transform(data): 
    data['price'] = round(data.price,2) 
    return data 
# загрузка БД в формат csv
def load_data(target_file, transformed_data): 
    transformed_data.to_csv(target_file, index=False, encoding='utf-8') 

# функция для отображения прогресса выполнения кода
def log_progress(message):
    time_format = "%y-%m-%d-%H:%M:%S" # Year-Monthname-Day-Hour-Minute-Second 
    time_now = datetime.now()
    time_stamp = time_now.strftime("%y-%m-%d-%H:%M:%S")
    with open (log_file, 'a' ) as log_f:
        log_f.write(f'{time_stamp}: {message} \n')


log_progress("start")
print("start") 
result_extract = extract()
log_progress("extract is completed")
print(result_extract)

log_progress("transform started")
result_transform = transform(result_extract)
print("Transformed Data") 
print(result_transform)

log_progress ("Save to csv ")
print("Save to csv")
load_data(target_file, result_transform)

log_progress("ETL Job Ended") 





