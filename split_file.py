#!/usr/bin/python3

import os
import pandas as pd

work_folder = "/home/slawa/HDD/hak_2023/DATA_Files/Facility2Constellation"
work_files = [i for i in os.listdir(work_folder) if ".csv" in i]
date_list = ["2027-05-31",
             "2027-06-01",
             "2027-06-02",
             "2027-06-03",
             "2027-06-04",
             "2027-06-05",
             "2027-06-06",
             "2027-06-07",
             "2027-06-08",
             "2027-06-09",
             "2027-06-10",
             "2027-06-11",
             "2027-06-12",
             "2027-06-13",
            ]

for work_file in work_files:
    df = pd.read_csv(os.path.join(work_folder, work_file), delimiter=';', names=["name", "name_2", "date_1", "date_2", "sec"])
    df["date_1"] = pd.to_datetime(df["date_1"], format="%d %b %Y %H:%M:%S.%f")
    df["date_2"] = pd.to_datetime(df["date_2"], format="%d %b %Y %H:%M:%S.%f")
    for i in range(len(date_list)-1):
        target_folder = os.path.join(work_folder, '_'.join(date_list[i+1].split("-")[::-1]))
        if not os.path.isdir(target_folder): os.system(f'mkdir {target_folder}')
        df_2 = df[(df["date_1"] > f"{date_list[i]} 8:59:59.999") & (df["date_2"] <= f"{date_list[i+1]} 8:59:59.999")]
        df_2.to_csv(os.path.join(target_folder, work_file), index=False, sep=';', header=False, date_format="%d %b %Y %H:%M:%S.%f")