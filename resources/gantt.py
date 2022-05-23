import pandas as pd
import numpy as np
import mpxj
import jpype
import datetime

import plotly.express as px
import plotly.graph_objects as go

PATH = './../results'

import os
import sys

def get_weight_col(filename, col_dict): # найти необходимую колонку
    weight = '_'.join(filename.split('.')[0].split('_')[2:4])
    return col_dict[weight]

def color(row):
    "Функция для раскраски графа"
    c_dict = {
        'Промежуточные':'Red',
        'Действие':'Blue',
        'Исходные': 'Green',
        'Ветвление': 'Grey',
        'Выходные': 'Violet'
    }
    return c_dict[row['Тип данных']]

def convert(number,
            year=datetime.datetime.today().strftime("%m/%d/%Y").split('/')[2],
            month=datetime.datetime.today().strftime("%m/%d/%Y").split('/')[0],
            day=datetime.datetime.today().strftime("%m/%d/%Y").split('/')[1],
            hour=datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S").split(' ')[1].split(':')[0],
            minute=datetime.datetime.today().strftime("%m/%d/%Y %H:%M:%S").split(' ')[1].split(':')[1]
            ):

    '''
    Конвертирует number (float) – ЧИСЛО ЧАСОВ,  в полную дату с точностью до минут
    Пользователь может указать год, месяц, день, иначе назначается сегодняшняя дата

    TODO: добавить учет конца месяца
    '''
    day_ini = day
    to_day_hour = number/24  #  выводит float, где день - число перед запятой
    if len(str(to_day_hour).split('.')[0] + day_ini) > 1:  #  учет если кол-во дней больше 10
        day = str(int(to_day_hour)+int(day_ini))
    else:
        day = '0'+str(int(to_day_hour)+int(day_ini))

    hour_ini = hour
    hour = str(int(round(float('.'+str(number/24).split('.')[1])*24, 2)) + int(hour_ini))

    if int(hour) >= 24:
        day = str(int(day) + int(str(float(hour)/24).split('.')[0]))
        hour = str(int(round(float('.'+str(float(hour)/24).split('.')[1])*24,0)))
        if int(day) > 31:
            print('more than 31 days!')

    if len(hour) > 2:
        hour = '0'+ hour

    minute_ini = minute
    hour_to_min = str(round(float('.'+str(number/24).split('.')[1])*24, 5))
    minute = str(int(round(float('.'+hour_to_min.split('.')[1])*60, 2))+int(minute_ini))

    return pd.to_datetime(month+'/'+day+'/'+year+' '+hour+':'+minute, format='%m/%d/%Y %H:%M')


def get_gantt(df, weight_label):
    # df = pd.read_csv(os.path.join(path, filename))
    node_feature_weight = ['Времязатраты (1-10)', 'Сложность задачи (1-10)', 'Трудозатраты, чел*часов']
    weight_feature = ['time_exp', 'comp_exp', 'work_exp']
    columns_feature = dict(zip(weight_feature, node_feature_weight))
    # weight_col = get_weight_col(filename, columns_feature)
    weight_col = columns_feature[weight_label]

    df = df[['Тип данных', 'Идентификатор', 'Описание', weight_col, 'Модуль ПО']].copy()
    df[weight_col].fillna(0, inplace=True)
    df['Color'] = df.apply(color, axis=1)
    df['Start'] = df[weight_col].cumsum().shift(1).fillna(0)
    df['Finish'] = df[weight_col].cumsum()
    df['Start-Finish'] = df['Finish'] - df['Start']
    df['Start Date'] = df['Start'].to_frame().applymap(convert)
    df['Finish Date'] = df['Finish'].to_frame().applymap(convert)

    dia = df[df['Тип данных'] != 'Действие'].copy()
    dia = px.scatter(dia, x="Start Date", y="Идентификатор", symbol_sequence=['diamond'])
    dia = dia.update_traces(marker=dict(size=15, color='orange', line=dict(width=2)))
    dia.update_yaxes(autorange='reversed')

    fig = px.timeline(
        df,
        x_start="Start Date",
        x_end="Finish Date",
        y="Идентификатор",
        hover_data=[
            'Модуль ПО'
        ]
    )
    fig.update_yaxes(autorange="reversed")

    new_fig = go.Figure(data=fig.data + dia.data, layout=fig.layout)
    new_fig.update_layout(showlegend=True)

    return new_fig, df


def create_xml(df, weight_label, name):
    node_feature_weight = ['Времязатраты (1-10)', 'Сложность задачи (1-10)', 'Трудозатраты, чел*часов']
    weight_feature = ['time_exp', 'comp_exp', 'work_exp']
    columns_feature = dict(zip(weight_feature, node_feature_weight))
    weight_col = columns_feature[weight_label]

    if jpype.isJVMStarted():
        pass
    else:
        jpype.startJVM()

    from java.lang import Double
    from java.text import SimpleDateFormat
    from net.sf.mpxj import ProjectFile, TaskField, Duration, TimeUnit, RelationType
    from net.sf.mpxj.writer import ProjectWriter,   ProjectWriterUtility
    from java.io import OutputStream, ByteArrayOutputStream, IOException

    df_java = SimpleDateFormat("dd/MM/yyyy HH:mm:ss")

    # Create a ProjectFile instance
    file = ProjectFile()

    # Add a default calendar called "Standard"
    calendar = file.addDefaultBaseCalendar()

    properties = file.getProjectProperties()
    properties.setStartDate(df_java.parse(datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")))

    # Set a couple more properties just for fun
    properties.setProjectTitle("Created by GRAPH KNOWLEDGE")

    # Let's create an alias for TEXT1
    customFields = file.getCustomFields()
    field = customFields.getCustomField(TaskField.TEXT1)
    field.setAlias("My Custom Field")

    # Create a summary task
    task1 = file.addTask()
    start = df['Идентификатор'].iloc[0]
    end = df['Идентификатор'].iloc[df.shape[0] - 1]
    task1.setName(f"{start} -> {end}")  # A --> B

    tasks = {}
    for i in range(len(df)):
        tasks[i] = task1.addTask()
        tasks[i].setName(df['Идентификатор'].iloc[i])
        tasks[i].setDuration(Duration.getInstance(df[weight_col].iloc[i], TimeUnit.HOURS))
        tasks[i].setStart(df_java.parse(pd.to_datetime(df['Start Date']).dt.strftime("%d/%m/%Y %H:%M:%S").iloc[i]))

        description = df['Описание'].iloc[i]
        description = description.replace('\n', ', ')
        tasks[i].setText(1, description)  # название параметра

        software = df['Модуль ПО'].iloc[i]
        if isinstance(software, str):
            software = software.replace('\n', ', ')
            resource = file.addResource()
            resource.setName(software)
            assignment = tasks[i].addResourceAssignment(resource)
        else:
            pass

        if i != 0:
            tasks[i].addPredecessor(tasks[i - 1], RelationType.FINISH_START, None)
        else:
            continue

    writer = ProjectWriterUtility.getProjectWriter(f"{name}.xml")
    # output = OutputStream()
    # writer.write(file, f"{name}.xml")

    out = ByteArrayOutputStream()
    writer.write(file, out)
    string_out = str(out)
    bytes_file = string_out.encode(encoding='UTF-8')
    return bytes_file

    # return buffer.write(file)
    # jpype.shutdownJVM()