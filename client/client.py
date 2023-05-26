#!/usr/bin/python3

import requests
import pandas as pd


URL = 'http://62.109.6.118:8008/upload'
ARHIVE_name = 'DATA_Files (1).zip'

files = [
    ('file', (ARHIVE_name, open(ARHIVE_name, 'rb'))),
]
response = requests.post(URL, files=files)


if __name__ == "__main__":
    def base_logic(data:dict):
        Facility_df = pd.DataFrame(data=data["Facility"], columns=["Station", "Satellite", "Access", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)"])
        Russia_df = pd.DataFrame(data=data["Russia"], columns=["Station", "Satellite", "Access", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)"])
        return (Facility_df, Russia_df)
    
    # Facility_df - это видимость станциями
    # Russia_df - это спутники пролетают над РФ
    Facility_df, Russia_df = base_logic(eval(response.text))
    print(Facility_df.head())
    print(Russia_df.head())
