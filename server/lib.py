#!/usr/bin/python3

import re
import datetime
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

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

def main_magic(Facility_df, Russia_df):
    gbit_to_tb = 1 / 8192 # константа перевода Gbit в Tbyte

    list_date = []

    def date_file(delta_date, max_date):
        #list_date.append(delta_date)
        if delta_date != max_date:
            date_1 = datetime.datetime(delta_date.year, delta_date.month, delta_date.day, 9, 0, 0)
            delta_date = delta_date + datetime.timedelta(days=1)
            date_2 = datetime.datetime(delta_date.year, delta_date.month, delta_date.day, 9, 0, 0)
        else:
            date_1 = datetime.datetime(delta_date.year, delta_date.month, delta_date.day, 9, 0, 0)
            date_2 = datetime.datetime(delta_date.year, delta_date.month, delta_date.day, 23, 59, 59)
        facility_day = Facility_df.loc[np.logical_and(Facility_df['Start Time (UTCG)'] >= date_1,
                                                      Facility_df['Start Time (UTCG)'] < date_2)]
        russia_day = Russia_df.loc[np.logical_and(Russia_df['Start Time (UTCG)'] >= date_1,
                                                  Russia_df['Start Time (UTCG)'] < date_2)]
        return {"delta_date": delta_date, f"Facility_{date_1.date()}": facility_day, f"Russia_{date_1.date()}": russia_day}

    def intersection(date_on, date_off, start_date, stop_date):
        """
        Функция поиска пересечения временных периодов
        :param date_on: дата начала первого периода включения
        :param date_off: дата окончания первого периода включения
        :param start_date: дата начала второго периода включения
        :param stop_date: дата окончания второго периода включения
        :return:
        - дата начала и дата окончания общей части периодов
        """
        if date_off < date_on or stop_date < start_date:
            # вот тут надо вывести исключение
            print('Ошибка! Дата начала периода не может быть больше даты окончания')
        else:
            if start_date <= date_on:
                start_date_period = date_on
            else:
                start_date_period = start_date
            if stop_date <= date_off:
                stop_date_period = stop_date
            else:
                stop_date_period = date_off
            if start_date_period >= stop_date_period:
                return date_on, date_on
            else:
                return start_date_period, stop_date_period

    for col in ['Start Time (UTCG)', 'Stop Time (UTCG)']:
        Facility_df[col] = Facility_df[col].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S'))
        Russia_df[col] = Russia_df[col].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S'))

    min_date = min(Facility_df['Start Time (UTCG)']).date()
    max_date = max(Facility_df['Start Time (UTCG)']).date()

    result = dict()

    delta_date = min_date
    while max_date != delta_date:
        list_date.append(delta_date)
        temp_dict = date_file(delta_date, max_date)
        delta_date = temp_dict["delta_date"]
        result.update({k:v for k, v in temp_dict.items() if "delta_date" not in temp_dict.keys()})
    date_file(delta_date, max_date)

    dict_max_kinosat = {}
    dict_max_zorkii = {}

    name_facility = Facility_df['Station'].unique()
    satellit_name = Facility_df['Satellite'].unique()

    result_df = pd.DataFrame(columns = ['Интервал', 'Длительность интервала', 'Спутник', 'Приемник',
                                        'Заполненность спутника по завершении операции',
                                        'Суммарный объем записанной информации',
                                        'Суммарный объем сброшенной информации'])

    # Индикатор занятости приемника
    dict_block_dur = {}
    for s in name_facility:
        dict_block_dur[s] = pd.to_datetime('1900-01-01 00:00:00', format='%Y-%m-%d %H:%M:%S')
    # Индикатор "занятости" спутника
    dict_block_sat = {}
    dict_fullness_sat = {}
    for s in satellit_name:
        dict_block_sat[s] = pd.to_datetime('1900-01-01 00:00:00', format='%Y-%m-%d %H:%M:%S')
        dict_fullness_sat[s] = 0

    full_sum_foto = 0
    full_sum_save = 0
    list_kinosat = ['_1101', '_1102', '_1103', '_1104', '_1105']

    # Формирование таблиц интервалов видимости по станциям
    for dates in list_date:
        df = result[f"Facility_{dates}"]
        res_df = pd.DataFrame(index=satellit_name, columns=name_facility)
        for station in name_facility:
            for sat in satellit_name:
                df_cut = df.loc[df['Station'] == station]
                df_cut = df_cut.loc[df_cut['Satellite'] == sat]
                list_interval = []
                for iter, rows in df_cut.iterrows():
                    list_interval.append([rows['Start Time (UTCG)'], rows['Stop Time (UTCG)']])
                res_df[station].loc[sat] = list_interval
        result[f"Full_date_{dates}"] = res_df
    print('Завершено формирование таблиц с интервалами видимости')

    # Блок расчета возможного времени записи
    for dates in list_date:
        df = result[f"Russia_{dates}"]
        res_df_1 = pd.DataFrame(index=satellit_name, columns=['for_foto'])
        for sat in satellit_name:
            df_cut = df.loc[df['Satellite'] == sat]
            list_time_interval = []
            list_duration = []
            for iter, row in df_cut.iterrows():
                list_time_interval.append([row['Start Time (UTCG)'],
                                           row['Stop Time (UTCG)']])
                list_duration.append(row['Duration (sec)'])
            if len(list_time_interval) != 0:
                for i in range(len(list_time_interval)):
                    list_time_interval[i] = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(list_time_interval[i]))
                res_df_1['for_foto'].loc[sat] = list_time_interval
            else:
                res_df_1['for_foto'].loc[sat] = 0
        result[f"For_foto_{dates}"] = res_df_1

        print('Завершено формирование таблиц с интервалами съемки')
        # Может пригодиться для "обрезания" списка съемки при заполнении нужного объема ЗУ
        # На тестовых данных дало потерю 0,5 Тб
        """
        new_list_duration = []
        if satellit[-7:-2] not in list_kinosat:
            summa = 0
            for dur in list_duration:
                if summa < 0.21:
                    new_list_duration.append(dur)
                    summa  = summa + dur * 4 * 0.00012207
                print(summa)
            list_duration = new_list_duration
        list_time_interval = list_time_interval[:len(list_duration)]
        """
        # Объединение съемки и зон видимости
        sum_1 = result[f"Full_date_{dates}"]
        sum_2 = result[f"For_foto_{dates}"]
        full_data = pd.concat([sum_1, sum_2], axis=1)
        result[f"Full_{dates}"] = full_data
        print('Завершено формирование общей таблицы')

        # Вычитание из зон видимости тех интервалов, которые пересекаются с интервалами записи
        interval = result[f"Full_{dates}"]
        for iter, row in interval.iterrows():
            foto = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(row['for_foto']))
            foto_1 = foto[::2]
            foto_2 = foto[1::2]
            foto = []
            for i in range(len(foto_1)):
                foto.append([pd.to_datetime(foto_1[i], format='%Y-%m-%d %H:%M:%S'),
                             pd.to_datetime(foto_2[i], format='%Y-%m-%d %H:%M:%S')])
            for name in name_facility:
                period = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(row[name]))
                period_1 = period[::2]
                period_2 = period[1::2]
                period = []
                for i in range(len(period_1)):
                    period.append([pd.to_datetime(period_1[i], format='%Y-%m-%d %H:%M:%S'),
                                   pd.to_datetime(period_2[i], format='%Y-%m-%d %H:%M:%S')])
                del_period = []
                for j in period:
                    for k in foto:
                        date_on, date_off = intersection(j[0], j[1], k[0], k[1])
                        if date_on != date_off:
                            del_period.append(j)
                new_period = [x for x in period if x not in del_period]

                if len(new_period) != 0:
                    for i in range(len(new_period)):
                        new_period[i] = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(new_period[i]))
                row[name] = new_period
        result[f"Full_without_foto_{dates}"] = interval
        print('Закончен расчет исключения интервалов съемки из интервалов видимости')

        # Расчет длительности каждого периода
        def string_to_date(x):
            x = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(x))
            x_1 = x[::2]
            x_2 = x[1::2]
            x = []
            unique_date = []
            for i in range(len(x_1)):
                x.append([pd.to_datetime(x_1[i], format='%Y-%m-%d %H:%M:%S'),
                          pd.to_datetime(x_2[i], format='%Y-%m-%d %H:%M:%S')])
                date = x[i][0].date()
                date_1 = x[i][1].date()
                if date not in unique_date:
                    unique_date.append(date)
                if date_1 not in unique_date:
                    unique_date.append(date_1)
            return x, unique_date


        timing = result[f"Full_without_foto_{dates}"]
        print(timing.columns)
        for iter, row in timing.iterrows():
            for i in timing.columns:
                time, unique_date = string_to_date(str(row[i]))
                sum_time = 0
                for k in time:
                    sec = (k[1] - k[0]).total_seconds()
                    sum_time = sum_time + sec
                row[i] = sum_time
        result[f"Duration_{dates}"] = timing
        print('Закончен расчет длительностей каждого интервала')

        # Дополнительные столбцы для классификации спутников
        duration = result[f"Duration_{dates}"]

        duration['Суммарная видимость (минус интервалы записи)'] = 0
        duration['Суммарная видимость (минус интервалы записи)'] = duration[name_facility].sum(axis=1)
        # duration['Гигабайты, возможные для записи за интервал'] = duration['for_foto'] * 0.5

        duration['Террабайты, возможные для записи за интервал'] = duration['for_foto'] * 4 * 0.00012207
        duration['Террабайты, возможные для записи в сутки (среднее)'] = duration[
                                                                             'Террабайты, возможные для записи за интервал']

        duration = duration.sort_values(by='for_foto')
        duration['index_asc'] = 0
        ind = 1
        duration['satellit'] = 0
        for iter, row in duration.iterrows():
            if iter[-7:-2] in list_kinosat:
                duration['satellit'].loc[iter] = 'Киносат'
            else:
                duration['satellit'].loc[iter] = 'Зоркий'
            # duration['index_asc'].loc[duration.index == iter.map(str)] = ind
            # ind = ind + 1

        # duration['satellit'] = np.where(duration['index_asc'] <= 150, 'Зоркий', 'Киносат')
        duration['volume'] = np.where(duration['satellit'] == 'Зоркий', 0.5, 1)
        duration['Переполняемость за сутки'] = np.where(
            duration['volume'] <= duration['Террабайты, возможные для записи за интервал'], 0, 1)
        sum_kinosat = sum(duration['Террабайты, возможные для записи за интервал'].loc[duration['satellit'] == 'Киносат'])
        time_kinosat_for_save = sum_kinosat * 8192
        print(sum_kinosat, time_kinosat_for_save)
        sum_zorkii = (24 * 60 * 60 * 14 - time_kinosat_for_save) * 0.25 * 0.00012207
        time_zorkii = sum_zorkii * 8192
        print(sum_zorkii, time_zorkii)
        sum_zorkii_for_one = sum_zorkii / 150
        time_zorkii_for_one = time_zorkii / 150
        print(sum_zorkii_for_one, time_zorkii_for_one)

        reserve = 5
        max_sum_kinosat = sum_kinosat + 2 * reserve
        max_sum_zorkii = sum_zorkii + reserve

        dict_max_kinosat[dates] = max_sum_kinosat
        dict_max_zorkii[dates] = max_sum_zorkii
        result[f"Duration_added_{dates}"] = duration

    print('Закончен расчет дополнительных столбцов длительности')
    print(dict_max_kinosat)
    print(dict_max_zorkii)
    print('И вот теперь начинаем формировать расписание')
    dict_mass = {}
    count = 0
    for dates in list_date:
        df = result[f"Full_without_foto_{dates}"]
        for iter, row in df.iterrows():
            sat = iter
            for col in df.columns:
                if iter[-7:-2] in list_kinosat:
                    type_sat = 1
                else:
                    type_sat = 0.5
                receiving = col
                save = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(row[col]))
                save_1 = save[::2]
                save_2 = save[1::2]
                for s in range(len(save_1)):
                    time_interval = save_1[s] + '-' + save_2[s]
                    #print(time_interval)
                    dict_mass[count] = [sat, receiving, time_interval, (pd.to_datetime(save_2[s], format='%Y-%m-%d %H:%M:%S') -
                                                                                 pd.to_datetime(save_1[s],
                                                                                                format='%Y-%m-%d %H:%M:%S')).total_seconds(),
                                        type_sat, [save_1[s], save_2[s]], dict_max_kinosat[dates], dict_max_zorkii[dates]]
                    count = count + 1

    dict_queue = {}
    dict_block = {}
    for x in dict_mass.keys():
        interval_queue = pd.to_datetime(dict_mass[x][-3][0], format='%Y-%m-%d %H:%M:%S')
        interval_block = pd.to_datetime(dict_mass[x][-3][1], format='%Y-%m-%d %H:%M:%S')
        dict_queue[x] = interval_queue
        dict_block[x] = interval_block

    sorted_dict_queue = {}
    sorted_keys = sorted(dict_queue, key=dict_queue.get)

    for w in sorted_keys:
        sorted_dict_queue[w] = dict_queue[w]
    #print(sorted_dict_queue)
    full_sum_zorkii = 0
    full_sum_kinosat = 0
    for zu in sorted_dict_queue.keys():
        if dict_mass[zu][1] == 'for_foto':
            if dict_block_sat[dict_mass[zu][0]] <= dict_queue[zu]:
                # Проверяем, хватит ли у спутника места, чтобы фотографировать весь период
                if dict_fullness_sat[dict_mass[zu][0]] + (dict_mass[zu][3] * 4 * gbit_to_tb) <= dict_mass[zu][4]:
                    #print('Заполненность спутника до: ', dict_fullness_sat[dict_mass[zu][0]])
                    if dict_mass[zu][4] == 1:
                        if full_sum_zorkii + dict_mass[zu][3] * 4 * gbit_to_tb <= dict_mass[zu][-2]:
                            dict_fullness_sat[dict_mass[zu][0]] = dict_fullness_sat[dict_mass[zu][0]] + dict_mass[zu][3] * 4 * gbit_to_tb
                            dict_block_sat[dict_mass[zu][0]] = dict_block[zu]
                            full_sum_foto = full_sum_foto + dict_mass[zu][3] * 4 * gbit_to_tb
                            full_sum_zorkii = full_sum_zorkii + dict_mass[zu][3] * 4 * gbit_to_tb
                    else:
                        #if full_sum_kinosat + dict_mass[zu][3] * 4 * gbit_to_tb <= dict_mass[zu][-1]:
                            dict_fullness_sat[dict_mass[zu][0]] = dict_fullness_sat[dict_mass[zu][0]] + dict_mass[zu][3] * 4 * gbit_to_tb
                            dict_block_sat[dict_mass[zu][0]] = dict_block[zu]
                            full_sum_foto = full_sum_foto + dict_mass[zu][3] * 4 * gbit_to_tb
                            full_sum_kinosat = full_sum_kinosat + dict_mass[zu][3] * 4 * gbit_to_tb
                    #print('Заполненность спутника после: ', dict_fullness_sat[dict_mass[zu][0]])
                    new_row = pd.DataFrame([[dict_mass[zu][2],
                                            dict_mass[zu][3],
                                            dict_mass[zu][0],
                                            dict_mass[zu][1],
                                            dict_fullness_sat[dict_mass[zu][0]],
                                            full_sum_foto,
                                            full_sum_save]],
                                           columns=['Интервал', 'Длительность интервала', 'Спутник',
                                                    'Приемник', 'Заполненность спутника по завершении операции',
                                                    'Суммарный объем записанной информации',
                                                    'Суммарный объем сброшенной информации'])
                    result_df = pd.concat([result_df, new_row], ignore_index=True)
        else:
            #print(dict_block_dur[dict_mass[zu][1]], dict_queue[zu])
            if dict_block_dur[dict_mass[zu][1]] <= dict_queue[zu]:
                #print(dict_block_sat[dict_mass[zu][0]], dict_queue[zu])
                if dict_block_sat[dict_mass[zu][0]] <= dict_queue[zu]:
                    if dict_mass[zu][4] == 1:
                        vol_save = dict_mass[zu][3] * gbit_to_tb
                    else:
                        vol_save = dict_mass[zu][3] * 0.25 * gbit_to_tb
                    #print('Объем сброса: ', vol_save)
                    if dict_fullness_sat[dict_mass[zu][0]] <= dict_mass[zu][4] and dict_fullness_sat[dict_mass[zu][0]] > vol_save:
                        full_sum_save = full_sum_save + vol_save
                        #print('Заполненность спутника до: ', dict_fullness_sat[dict_mass[zu][0]])
                        dict_fullness_sat[dict_mass[zu][0]] = dict_fullness_sat[dict_mass[zu][0]] - vol_save
                        if dict_mass[zu][4] == 1:
                            full_sum_kinosat = full_sum_kinosat - vol_save
                        else:
                            full_sum_zorkii = full_sum_zorkii - vol_save
                        #print('Заполненность спутника после: ', dict_fullness_sat[dict_mass[zu][0]])
                        dict_block_sat[dict_mass[zu][0]] = dict_block[zu]
                        dict_block_dur[dict_mass[zu][1]] = dict_block[zu]
                        new_row = pd.DataFrame([[dict_mass[zu][2],
                                                 dict_mass[zu][3],
                                                 dict_mass[zu][0],
                                                 dict_mass[zu][1],
                                                 dict_fullness_sat[dict_mass[zu][0]],
                                                 full_sum_foto,
                                                 full_sum_save]],
                                               columns=['Интервал', 'Длительность интервала', 'Спутник',
                                                        'Приемник', 'Заполненность спутника по завершении операции',
                                                        'Суммарный объем записанной информации',
                                                        'Суммарный объем сброшенной информации'])
                        result_df = pd.concat([result_df, new_row], ignore_index=True)
    result["final_schdule"] = result_df
    result = {k:v.to_dict('list') for k,v in result.items()}
    return result
