import os
import re

files_folder = 'DATA_Files/Russia2Constellation'
file_name = [i for i in os.listdir(os.path.join(os.getcwd(), files_folder)) if ("readme" not in i) and ("py" not in i) and (".csv" not in i)]

for fn in file_name:
    print(fn)
    with open(os.path.join(os.getcwd(), os.path.join(files_folder, fn)), 'r') as f:
        data = [i.replace('\n', '') for i in f.readlines()[4:]]
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
                temp_string = temp_string.replace("Russia-To-", "")
                data_temp.append(temp_string.replace("    ", ";"))
    
    with open(os.path.join(os.getcwd(), os.path.join(files_folder, fn.replace(".txt", ".csv"))), 'w', encoding='utf-8') as f:
        f.write('\n'.join(data_temp))

