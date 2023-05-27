#!/usr/bin/python3

from fastapi import FastAPI, File, UploadFile
import uvicorn
import os
import pandas as pd
from lib import pars_txt_file
import json

TEMP_FOLDER = os.path.join(os.getcwd(), "temp")

app = FastAPI()

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    try:
        contents = file.file.read()
        fn =os.path.join(TEMP_FOLDER, file.filename)
        with open(fn, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
        os.system(f'unzip -uqo "{fn}" -d "{os.path.dirname(fn)}"')
        os.system(f'rm "{fn}"')
        source_folders = [i for i in os.listdir(TEMP_FOLDER) if "readme.txt" not in i]
        results = dict()
        for source in source_folders:
            work_folder = os.path.join(TEMP_FOLDER, source)
            data = []
            files_name = [i for i in os.listdir(work_folder) if "readme.txt" not in i]
            for source_file in files_name:
                with open(os.path.join(work_folder, source_file), 'r', encoding='utf-8') as f:
                    raw_data = pars_txt_file(f.read())
                data += raw_data
            results[source.split("2")[0]] = data
        
        # пересобираем результат парсинга в df
        Facility_df = pd.DataFrame(data=results["Facility"], columns=["Station", "Satellite", "Access", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)"])
        Russia_df = pd.DataFrame(data=results["Russia"], columns=["Station", "Satellite", "Access", "Start Time (UTCG)", "Stop Time (UTCG)", "Duration (sec)"])
        

        os.system(f'rm -fr {TEMP_FOLDER + "/*"}')

    return {"message": results}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8008)
