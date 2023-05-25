#!/usr/bin/python3

import re
import datetime

def pars_txt_file(data:str):
    data = data.split('\n')[4:]
    data = [i for i in data if i != '']
    data = [i for i in data if '-----' not in i]
    data = [i for i in data if 'Duration' not in i]
    data = [i for i in data if 'Global' not in i]
    result = dict()
    satellite_name = ''
    for row in data:
        if row[0] != ' ':
            satellite_name = row.replace("Russia-To-", "")
            result[satellite_name] = {"Access":[], "Start Time (UTCG)":[], "Stop Time (UTCG)":[], "Duration (sec)":[]}
        else:
            temp_string = re.sub(r"(\s{5,})", "    ", row)
            temp_string = temp_string.split("    ")[1:]
            result[satellite_name]["Access"].append(int(temp_string[0]))
            #result[satellite_name]["Start Time (UTCG)"].append(temp_string[1]) 
            #result[satellite_name]["Stop Time (UTCG)"].append(temp_string[2])
            result[satellite_name]["Start Time (UTCG)"].append(datetime.datetime.strptime(temp_string[1], "%d %b %Y %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")) 
            result[satellite_name]["Stop Time (UTCG)"].append(datetime.datetime.strptime(temp_string[2], "%d %b %Y %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S"))
            result[satellite_name]["Duration (sec)"].append(int(float(temp_string[3])))
    return result