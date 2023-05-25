import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import datetime

def intersection(date_on, date_off, start_date, stop_date):
    '''
    Функция поиска пересечения временных периодов
    :param date_on: дата начала первого периода включения
    :param date_off: дата окончания первого периода включения
    :param start_date: дата начала второго периода включения
    :param stop_date: дата окончания второго периода включения
    :return:
    - дата начала и дата окончания общей части периодов
    - если периоды не пересекаются, то [0, 0]
    '''
    if date_off < date_on or stop_date < start_date:
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

# Блок формирования исходной таблицы со списками периодов видимости и нахождения на территории России
import re
import os

for dates in ['02_06_2027', '03_06_2027', '04_06_2027', '05_06_2027', '06_06_2027', '07_06_2027',
              '08_06_2027', '09_06_2027', '10_06_2027', '11_06_2027', '12_06_2027', '13_06_2027']:
    count_days = 1
    path = f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Facility2Constellation\\{dates}'
    path_1 = f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Russia2Constellation\\{dates}'

    dir_list_facility = []
    dir_list_russia = []

    name_facility = []
    name_russia = []
    extension = os.path.splitext(path)[1]

    for x in os.listdir(path):
        if os.path.splitext(os.path.join(path, x))[1] == '.csv' in x:
            name = x.split('-')[1].split('.')[0]
            dir_list_facility.append(os.path.join(path, x))
            name_facility.append(x.split('-')[1].split('.')[0])
    print(dir_list_facility)
    print(name_facility)

    for x in os.listdir(path_1):
        if os.path.splitext(os.path.join(path_1, x))[1] == '.csv' in x:
            dir_list_russia.append(os.path.join(path_1, x))
            name_russia.append(x.split('-')[-1].split('_plane')[0])
    print(dir_list_russia)
    print(name_russia)

    satellit_name = []
    for i in dir_list_facility:
        df = pd.read_csv(i, sep=';', header=None)
        for j in df[0].unique():
            if j.split('-')[-1] not in satellit_name:
                satellit_name.append(j.split('-')[-1])
    print(len(satellit_name))
    '''
    df = pd.read_csv(os.path.join(path, 'Facility-' + name_facility[0] + '.csv'), sep=';', header=None)
    print(satellit_name[0])
    df = df.loc[df[0] == name_facility[0] + '-To-' + satellit_name[0]]

    df['date'] = df[2].apply(lambda x: x[:-17])
    count_days = 1 #len(df['date'].unique())
    print('Количество дней в периоде: ', 1) #, len(df['date'].unique()))

    res_df = pd.DataFrame(index=satellit_name, columns=name_facility)

    for i in range(len(name_facility)):
        path = dir_list_facility[i]
        receiver = name_facility[i]

        # Блок записи основного файла с датами по каждому спутнику
        for satellit in satellit_name:
            df = pd.read_csv(path, sep=';', header=None)
            list_date = []
            df = df.loc[df[0].str.contains(satellit)].reset_index(drop=True)
            list_time_interval = []
            list_duration = []
            for iter, row in df.iterrows():
                list_time_interval.append([pd.to_datetime(row[2][:-7], format='%d %b %Y %H:%M:%S'),
                                           pd.to_datetime(row[3][:-7], format='%d %b %Y %H:%M:%S')])
                list_duration.append(row[4])
            if len(list_time_interval) != 0:
                for r in range(len(list_time_interval)):
                    list_time_interval[r] = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(list_time_interval[r]))
            if len(list_time_interval) != 0:
                res_df.at[satellit, receiver] = list_time_interval
        print(name_facility[i])
    res_df.to_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Full_date_{dates}.xlsx')


    res_df_1 = pd.DataFrame(index=satellit_name, columns=['for_foto'])
    # Блок расчета возможного времени записи
    for satellit in satellit_name:
        for j in dir_list_russia:
            df = pd.read_csv(j, sep=';', header=None)
            if satellit in df[0].unique():
                df = df.loc[df[0] == satellit]
                list_time_interval = []
                list_duration = []
                for iter, row in df.iterrows():
                    list_time_interval.append([pd.to_datetime(row[2][:-7], format='%d %b %Y %H:%M:%S'),
                                               pd.to_datetime(row[3][:-7], format='%d %b %Y %H:%M:%S')])
                    list_duration.append(row[4])
                list_foto = []
                for i in list_time_interval:
                    date_on = i[0]
                    date_off = i[1]
                    date = i[0].date()
                    start_date = pd.to_datetime(f'{date} 09:00:00')
                    stop_date = pd.to_datetime(f'{date} 18:00:00')
                    start_int, stop_int = intersection(date_on, date_off, start_date, stop_date)
                    if start_int != stop_int:
                        list_foto.append([start_int, stop_int])
                if len(list_foto) != 0:
                    for i in range(len(list_foto)):
                        list_foto[i] = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(list_foto[i]))
                    res_df_1['for_foto'].loc[satellit] = list_foto
                else:
                    res_df_1['for_foto'].loc[satellit] = 0
    res_df_1.to_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\For_foto_{dates}.xlsx')
    '''
    '''
    # Объединение съемки и зон видимости
    sum_1 = pd.read_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Full_date_{dates}.xlsx',
                          index_col='Unnamed: 0')
    sum_2 = pd.read_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\For_foto_{dates}.xlsx',
                          index_col='Unnamed: 0')
    sum = pd.concat([sum_1, sum_2], axis=1)

    sum.to_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Full_{dates}.xlsx')
    '''
    '''
    # Вычитание из зон видимости тех интервалов, которые пересекаются с интервалами записи
    interval = pd.read_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Full_{dates}.xlsx',
                                index_col='Unnamed: 0')

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

    interval.to_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Full_without_foto_{dates}.xlsx')

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

    timing = pd.read_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Full_without_foto_{dates}.xlsx',
                           index_col='Unnamed: 0')
    print(timing.columns)
    for iter, row in timing.iterrows():
        for i in timing.columns:
            time, unique_date = string_to_date(str(row[i]))
            sum_time = 0
            for k in time:
                sec = (k[1] - k[0]).total_seconds()
                sum_time = sum_time + sec
            row[i] = sum_time

    timing.to_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Duration_{dates}.xlsx')
    '''
    # Дополнительные столбцы для классификации спутников
    duration = pd.read_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Duration_{dates}.xlsx',
                             index_col='Unnamed: 0')

    duration['Суммарная видимость (минус интервалы записи)'] = 0
    duration['Суммарная видимость (минус интервалы записи)'] = duration[name_facility].sum(axis=1)
    # duration['Гигабайты, возможные для записи за интервал'] = duration['for_foto'] * 0.5

    duration['Террабайты, возможные для записи за интервал'] = duration['for_foto'] * 4 * 0.00012207
    duration['Террабайты, возможные для записи в сутки (среднее)'] = duration['Террабайты, возможные для записи за интервал'] / count_days

    import numpy as np
    duration = duration.sort_values(by='for_foto')
    duration['index_asc'] = 0
    ind = 1
    list_kinosat = ['_1101', '_1102', '_1103', '_1104', '_1105']
    duration['satellit'] = 0
    for iter, row in duration.iterrows():
        if iter[-7:-2] in list_kinosat:
            duration['satellit'].loc[iter] = 'Киносат'
        else:
            duration['satellit'].loc[iter] = 'Зоркий'
        #duration['index_asc'].loc[duration.index == iter.map(str)] = ind
        #ind = ind + 1


    #duration['satellit'] = np.where(duration['index_asc'] <= 150, 'Зоркий', 'Киносат')
    duration['volume'] = np.where(duration['satellit'] == 'Зоркий', 0.5, 1)
    duration['Переполняемость за сутки'] = np.where(duration['volume'] <= duration['Террабайты, возможные для записи за интервал'], 0, 1)

    sum_kinosat = sum(duration['Террабайты, возможные для записи за интервал'].loc[duration['satellit'] == 'Киносат'])
    time_kinosat_for_save = sum_kinosat * 8192
    print(sum_kinosat, time_kinosat_for_save)
    sum_zorkii = (24 * 60 * 60 * 14 - time_kinosat_for_save) * 0.25 * 0.00012207
    time_zorkii = sum_zorkii * 8192
    print(sum_zorkii, time_zorkii)
    sum_zorkii_for_one = sum_zorkii / 150
    time_zorkii_for_one = time_zorkii / 150
    print(sum_zorkii_for_one, time_zorkii_for_one)

    duration.to_excel(f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Duration_added_{dates}.xlsx')

reserve = 5
max_sum_kinosat = sum_kinosat + reserve
max_sum_zorkii = sum_zorkii + reserve

print(max_sum_kinosat)
print(max_sum_zorkii)

dict_mass = {}
count = 0
for dates in ['02_06_2027', '03_06_2027', '04_06_2027', '05_06_2027', '06_06_2027', '07_06_2027',
              '08_06_2027', '09_06_2027', '10_06_2027', '11_06_2027', '12_06_2027', '13_06_2027']:
    path = f'C:\\Users\\КитКат\\Desktop\\ЛЦТ\\Новые данные\\Full_{dates}.xlsx'
    df = pd.read_excel(path, index_col='Unnamed: 0')
    for iter, row in df.iterrows():
        sat = iter
        for col in df.columns:
            if iter[-7:-2] in list_kinosat:
                duration['satellit'].loc[iter] = 1
            else:
                duration['satellit'].loc[iter] = 0.5
            receiving = col
            save = re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(row[col]))
            save_1 = save[::2]
            save_2 = save[1::2]
            for s in range(len(save_1)):
                dict_mass[count] = [sat, receiving, [save_1[s], save_2[s]], (pd.to_datetime(save_2[s], format='%Y-%m-%d %H:%M:%S') -
                                                                             pd.to_datetime(save_1[s],
                                                                                            format='%Y-%m-%d %H:%M:%S')).total_seconds()]
                count = count + 1

dict_queue = {}
dict_block = {}
for x in dict_mass.keys():
    interval_queue = pd.to_datetime(dict_mass[x][2][0], format='%Y-%m-%d %H:%M:%S')
    interval_block = pd.to_datetime(dict_mass[x][2][1], format='%Y-%m-%d %H:%M:%S')
    dict_queue[x] = interval_queue
    dict_block[x] = interval_block
print(dict_queue)
print(dict_queue[45])
print(dict_block[45])

sorted_dict_queue = {}
sorted_keys = sorted(dict_queue, key=dict_queue.get)

for w in sorted_keys:
    sorted_dict_queue[w] = dict_queue[w]
print(sorted_dict_queue)