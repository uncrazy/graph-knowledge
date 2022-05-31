from typing import Tuple, Dict
import pandas as pd
import mpxj
import jpype
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

from backend.graph import columns_feature


# Find the weight column in dict from filename (deprecated)
def get_weight_col(filename: str, col_dict: dict):
    weight = '_'.join(filename.split('.')[0].split('_')[2:4])
    return col_dict[weight]


def color(row: pd.Series) -> str:
    """
    Coloring of gantt chart (used but not work properly)
    """
    c_dict = {
        'Промежуточные': 'Red',
        'Действие': 'Blue',
        'Исходные': 'Green',
        'Ветвление': 'Grey',
        'Выходные': 'Violet'
    }
    return c_dict[row['Тип данных']]


def convert(number: float) -> str:
    """
    Converting number from weight_col to date correspondingly to the current (today) date
    """
    return (datetime.now() + timedelta(hours=number)).strftime('%Y-%m-%d %H:%M')


def get_gantt(df: pd.DataFrame,
              weight_label: str,
              columns: Dict[str, str] = columns_feature) -> Tuple[go.Figure, pd.DataFrame]:
    """
    Build gantt chart and table from pathway
    """
    columns_rev = {v: k for k, v in columns.items()}
    weight_col = columns_rev[weight_label]

    df = df[['Тип данных', 'Идентификатор', 'Описание', weight_col, 'Модуль ПО']].copy()
    df[weight_col].fillna(0, inplace=True)
    df['Color'] = df.apply(color, axis=1)
    df['Start'] = df[weight_col].cumsum().shift(1).fillna(0)
    df['Finish'] = df[weight_col].cumsum()
    df['Start-Finish'] = df['Finish'] - df['Start']

    df['Start Date'] = df['Start'].apply(convert)
    df['Finish Date'] = df['Finish'].apply(convert)

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


def create_xml(df: pd.DataFrame,
               weight_label: str,
               name: str,
               columns: Dict[str, str] = columns_feature) -> bytes:
    """
    Create XML bytes-file for MS Project, based on jpype engine
    """
    columns_rev = {v: k for k, v in columns.items()}
    weight_col = columns_rev[weight_label]

    if jpype.isJVMStarted():
        pass
    else:
        jpype.startJVM()

    from java.lang import Double
    from java.text import SimpleDateFormat
    from net.sf.mpxj import ProjectFile, TaskField, Duration, TimeUnit, RelationType
    from net.sf.mpxj.writer import ProjectWriter, ProjectWriterUtility
    from java.io import OutputStream, ByteArrayOutputStream, IOException

    date_pattern = "yyyy-MM-dd HH:mm"  # before: "dd/MM/yyyy HH:mm:ss"
    df_java = SimpleDateFormat(date_pattern)

    # Create a ProjectFile instance
    file = ProjectFile()

    # Add a default calendar called "Standard"
    calendar = file.addDefaultBaseCalendar()

    properties = file.getProjectProperties()
    properties.setStartDate(df_java.parse(datetime.today().strftime('%Y-%m-%d %H:%M')))

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
        id = df['Идентификатор'].iloc[i]
        description = df['Описание'].iloc[i]
        description = description.replace('\n', ', ')
        tasks[i].setName(f'{id} - {description}')
        tasks[i].setDuration(Duration.getInstance(df[weight_col].iloc[i], TimeUnit.HOURS))
        tasks[i].setStart(df_java.parse(pd.to_datetime(df['Start Date']).dt.strftime('%Y-%m-%d %H:%M').iloc[i]))

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
    out = ByteArrayOutputStream()
    writer.write(file, out)
    string_out = str(out)
    bytes_file = string_out.encode(encoding='UTF-8')
    return bytes_file
