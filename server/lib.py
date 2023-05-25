#!/usr/bin/python3

import re
import datetime

def pars_txt_file(data:str):
    columns = ["Station", "Satellite", "Access", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)"]
    data = data.split('\n')[4:]
    data = [i for i in data if i != '']
    data = [i for i in data if '-----' not in i]
    data = [i for i in data if 'Duration' not in i]
    data = [i for i in data if 'Global' not in i]
    data_temp = list()
    satellite_name = ''
    for row in data:
        if row[0] != ' ':
            satellite_name = row
        else:
            temp_string = satellite_name + row
            temp_string = re.sub(r"(\s{5,})", "    ", temp_string)
            temp_string = temp_string.replace("-To-", ";")
            temp_string = temp_string.replace("    ", ";")
            temp_dict = dict(zip(columns, temp_string.split(";")))
            temp_dict["Start Time (UTCG)"] = datetime.datetime.strptime(temp_dict["Start Time (UTCG)"], "%d %b %Y %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
            temp_dict["Stop Time (UTCG)"] = datetime.datetime.strptime(temp_dict["Stop Time (UTCG)"], "%d %b %Y %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
            temp_dict["Duration (sec)"] = int(float(temp_dict["Duration (sec)"]))
            data_temp.append(temp_dict)
    return data_temp
