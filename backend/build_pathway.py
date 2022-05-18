import numpy as np
from dash import Dash, dcc, html, callback_context, callback
from dash.dependencies import Input, Output, State
from dash_extensions import Download
import dash_bootstrap_components as dbc
import argparse
import sys
from os import path

from dash.exceptions import PreventUpdate

rpath = '../'
sys.path.insert(0, rpath)
from backend.NXGraph import NXGraph
from resources.utils import *
from resources.gantt import *

PATH = './../results'

# Model name if needed
# -----------------------------
model = None
# -----------------------------

data_folder = 'data_new'
actions_file_name = path.join(rpath, f"{data_folder}/actions_reestr_graph.xlsx")
data_file_name = path.join(rpath, f"{data_folder}/data_model_graph.xlsx")
branching_name = path.join(rpath, f"{data_folder}/vetvleniq_graph.xlsx")
method_selection_block_name = path.join(rpath, f"{data_folder}/method_selection_blocks.xlsx")

metric_types = ["intensive"]
n_metrics = len(metric_types)

actions_df = pd.read_excel(actions_file_name)
actions_df.rename(columns={"код действия": "name",
                           "код вх источников\nсписок через зяпятую": "ins",
                           "код выхода": "outs"
                           }, inplace=True)

# filtering one-in one-output actions
cols = ['name', 'ins', 'outs']
for col in cols:
    actions_df[col] = actions_df[col].str.replace(' ', '')

cond1 = (actions_df.ins.str.split(',').str.len() == 1)
cond2 = (actions_df.outs.str.split(',').str.len() == 1)
one_action = actions_df[cond1 & cond2].copy()
# actions_df.drop( one_action.index, inplace=True )
arrows = list(zip(one_action.ins, one_action.name)) + list(zip(one_action.name, one_action.outs))
actions = list(zip(zip(one_action.ins, one_action.name), zip(one_action.name, one_action.outs)))

data_df = pd.read_excel(data_file_name)
data_df.rename(columns={"Код": "name"}, inplace=True)
branchings_df = pd.read_excel(branching_name)
branchings_df.rename(columns={"код\nветвления": "name"}, inplace=True)
method_selection_blocks_df = pd.read_excel(method_selection_block_name)
method_selection_blocks_df.rename(columns={"код блока": "name"}, inplace=True)

# building graph
my_graph = NXGraph(name="BigGraph", info="For inspection")
my_graph.build_structure(
    initial_structure=(
        data_df,
        actions_df,
        {
            'branchings': branchings_df,
            'method_selection_blocks': method_selection_blocks_df
        }
    ),
    inspect=True, model=model
)

node_feature_weight = ['Времязатраты (1-10)', 'Сложность задачи (1-10)', 'Трудозатраты, чел*часов']
weight_feature = ['time_exp', 'comp_exp', 'work_exp']
columns_feature = dict(zip(node_feature_weight, weight_feature))

# initializing & filtering from empty nodes
G = my_graph
filter_graph(G)
# add weight data to edges
add_edge_weight(G, columns_feature)
# rest of edges w/o any assigned weights
empty_edges = [e for e in G.edges() if len(G[e[0]][e[1]]) != 3]  # 3 weights
for e in empty_edges:
    for weight in weight_feature:
        G[e[0]][e[1]][weight] = 0

LAYOUT = 'graphviz_dot'
# selecting layout and source & target (put in interface)
G = select_layout(G, LAYOUT)

# time perfomance test
# import time
# t0 = time.time()
# source = 'S12'
# target = 'GDM|D04'
# weight = 'time_exp'
# path = nx.shortest_path(G, source, target, weight=weight)
# t1 = time.time()
# total = t1-t0
# print(total)

# parser = argparse.ArgumentParser(description='Plot graph knowledge & pathway depends on weights')
# group = parser.add_mutually_exclusive_group(required=True)
# group.add_argument('-g', '--graph', action='store_true', help='Launch and show the whole graph')
# group.add_argument(
#     '-p',
#     '--path',
#     nargs=3,
#     metavar=("source", "target", "weight"),
#     type=str,
#     help='Plot pathway between source and target nodes'
# )
# args = parser.parse_args()
# if args.graph:
#     SOURCE, TARGET, WEIGHT = None, None, None
# elif args.path:
#     SOURCE, TARGET, WEIGHT = args.path[0], args.path[1], args.path[2]
# else:
#     pass

# test nodes

# nodes = ["S03", 'CGM|D15', 'CGM|D16']
# description = [G.nodes[i]['Параметр'] for i in nodes]
# nodes_describe = zip(nodes, description)
# nodes_labels = [{'label': f"{k} - {v}", 'value': k} for k, v in nodes_describe]

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY]
        )
app.title = 'Graph knowledge'

SOURCE, TARGET, WEIGHT = None, None, None

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "30rem",
    "padding": "2rem 2rem 1rem 2rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
TABS_STYLE = {
    "margin-left": "31rem",
    "margin-right": "2rem",
    "margin-bottom": "1rem",
    "padding": "1rem 1rem",
}

CONTENT_STYLE = {
    'margin-top': '10px',
    'width': "150vh",
    "height": "90vh"
}

sidebar = html.Div(
    [
        html.H1("Graph knowledge", className="display-6"),
        html.Hr(),
        html.P(
            "Find the optimum path from source to target node", className="text"
        ),
        dcc.Dropdown(
            id='source-node',
            placeholder='Select the source ...',
            searchable=True,
            optionHeight=90,
            options=get_nodes_labels(G, G.nodes()),
            style={
                'font-size': '16px',
                 'width': '27rem',
                 'display': 'inline-block',
                 'margin-bottom': '5px'
            },
        ),
        dcc.Dropdown(
            id='target-node',
            placeholder='Select the target ...',
            searchable=True,
            optionHeight=90,
            options=get_nodes_labels(G, G.nodes()),
            disabled=True,
            style={
                'font-size': '16px',
                 'width': '27rem',
                 'display': 'inline-block',
                 'margin-bottom': '8px'
            },
        ),
        html.P(
            "Select weight feature for edges:", className="text"
        ),
        html.Div([
            dbc.RadioItems(
                id="weight",
                value='time_exp',
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-primary",
                labelCheckedClassName="active",
                options=[
                    {'label': k, 'value': v} for k, v in columns_feature.items()
                ],
                style={
                        'width': '27rem',
                },
            ),
        ],
            className="radio-group"
        ),
        html.Hr(),
        html.Div(
            [
                dbc.Button(
                    id='submit-button-state',
                    outline=True,
                    color="success",
                    className="me-1",
                    n_clicks=0,
                    children='Submit',
                    style={
                        'margin-right': '5px',
                    },
                ),
                dbc.Button(
                    id='reset-button-state',
                    outline=True,
                    color="danger",
                    className="me-1",
                    n_clicks=0,
                    children='Reset',
                    disabled=True,
                    style={
                        'margin-right': '5px',
                    },
                ),

            ],
            className='d-grid gap-2 col-9 mx-auto'
        ),
        html.Hr(),
        html.Div(
            [
            html.P(
                        "Save as:", className="text"
                    ),
                html.Div([
                    dbc.Button(
                        id='xml-button',
                        color='info',
                        children='*.XML',
                        disabled=True,
                        style={
                            'margin-right': '16px',
                        }
                    ),
                    Download(id="download-xml")
                ],
                style={
                    'margin-bottom': '5px',
                    'textAlign': 'center'
                }
                ),
                html.Div([
                    dbc.Button(
                        id='xlsx-button',
                        color='info',
                        children='*.XLSX',
                        disabled=True,
                    ),
                    Download(id="download-xlsx")
                ],
                style={
                    'margin-right': '15px',
                    'textAlign': 'center'
                }
                )
            ],
            style={'textAlign': 'center', 'margin': 'auto'}
        ),
    ],
    style=SIDEBAR_STYLE,
)

graph = dcc.Graph(
    id='GDM',
    figure=plot(G, SOURCE, TARGET, WEIGHT)[0],
    responsive=True,
    style=CONTENT_STYLE
)

table_object = html.Div(
    [
    html.Div(id='gantt-table', children='test_text'),
    ],
    style=CONTENT_STYLE
)

gantt_object = html.Div(
    [
    dcc.Graph(
        id='gantt-figure',
        responsive=True,
        style={
            'margin-top': '10px',
            'width': "150vh",
            "height": "50vh"
        }
    ),
    html.Div(
        id='software-block',
        children='text',
        # className='fst-normal',
        # style={
        #     'margin-left": "50px'
        # }
    )
    ]
)
tabs = {
    'Graph': [False, graph],
    'Table': [True, table_object],
    'Gantt chart': [True, gantt_object]
}
content = dbc.Container(
    dbc.Tabs(
        [
            dbc.Tab(
                id=k,
                children=v[1],
                label=f"{k}",
                tabClassName="flex-grow-2 text-center",
                disabled=v[0]
            )
            for k, v in tabs.items()
        ]
    ),
    className="p-4",
    style=TABS_STYLE
)

app.layout = html.Div([sidebar, content])

# app.layout = html.Div([
#     html.Div([
#         html.Div([
#         dcc.Dropdown(id='source_node',
#                      placeholder='Select the source ...',
#                      options=[
#                          {'label': k, 'value': k} for k in nodes
#                      ],
#                      style={
#                          'font-size': '16px',
#                          'width': '280px',
#                          'display': 'inline-block',
#                          'margin-right': '15px'
#                      }
#                      ),
#         dcc.Dropdown(id='target_node',
#                      placeholder='Select the target ...',
#                      options=[
#                         {'label': k, 'value': k} for k in nodes
#                      ],
#                      style={
#                       'font-size': '16px',
#                       'width': '280px',
#                       'display': 'inline-block',
#                       'margin-right': '15px'
#                      }
#                      )
#             ], style={'width': '25%', 'display': 'inline-block', 'margin-top': '20px', 'margin-bottom': '0px'}),
#         html.Div([
#         dbc.RadioItems(
#             id="weight",
#             className="btn-group",
#             inputClassName="btn-check",
#             labelClassName="btn btn-outline-primary",
#             labelCheckedClassName="active",
#             options=[
#                 {'label': k, 'value': v} for k, v in columns_feature.items()
#             ],
#             # style={
#             #         'display': 'inline-block'
#             # },
#             value='time_exp',
#         ),
#         # dcc.RadioItems(id='weight-selector',
#         #                options=[{'label': k, 'value': v} for k, v in columns_feature.items()],
#         #                inline=True,
#         #                style={
#         #                 'font-size': '16px',
#         #                })
#             ],
#             className="radio-group",
#             style={'width': '30%', 'display': 'inline-block', 'verticalAlign': 'center'}
#         ),
#         html.Div([
#             html.Button(id='submit-button-state', n_clicks=0, children='Submit',
#                         style={
#                             'display': 'inline-block',
#                             'margin-right': '5px',
#                         }),
#             html.Button(id='reset-button-state', n_clicks=0, children='Reset',
#                         style={
#                             'display': 'inline-block',
#                             'margin-right': '5px'
#                         }),
#             ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'сenter'}),
#     ], style={'display': 'flex', 'verticalAlign': 'center'}),
#     dcc.Graph(id='GDM',
#               figure=plot(G, SOURCE, TARGET, WEIGHT),
#               responsive=True,
#               style={'height': '95vh'})
# ])


# triggered_id = callback_context.triggered[0]['prop_id']

# для демо
# @app.callback(
#     Output('GDM', 'figure'),
#     Output('reset-button-state', 'disabled'),
#     Output('xml-button', 'disabled'),
#     Output('gantt-chart-button', 'disabled'),
#     Input('submit-button-state', 'n_clicks'),
#     State('source_node', 'value'),
#     State('target_node', 'value'),
#     State('weight', 'value')
# )
# def update_output(n_clicks, source, target, w):
#     if n_clicks in [0, None]:
#         raise PreventUpdate
#     else:
#         # w = 'time_exp'
#         fig = plot(G, source, target, w)
#         return fig, False, False, False

@app.callback(
    Output('target-node', 'options'),
    Output('target-node', 'disabled'),
    Input('source-node', 'value')
)
def update_target(source):
    if source in [0, None]:
        raise PreventUpdate
    else:
        target_options = nx.descendants(G, source)
        return get_nodes_labels(G, target_options), False

@app.callback(
    Output('GDM', 'figure'),
    Output('reset-button-state', 'disabled'),
    Output('xml-button', 'disabled'),
    Output('xlsx-button', 'disabled'),
    Output('submit-button-state', 'disabled'),
    Output('Table', 'disabled'),
    Output('Gantt chart', 'disabled'),
    Output('gantt-table', 'children'),
    Output('gantt-figure', 'figure'),
    Output('software-block', 'children'),
    Input('submit-button-state', 'n_clicks'),
    State('source-node', 'value'),
    State('target-node', 'value'),
    State('weight', 'value'),
    Input('reset-button-state', 'n_clicks')
)
def update_output(n_clicks, source, target, w, reset):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'submit-button-state':
            fig, nodes_path, df_path = plot(G, source, target, w)
            table = dbc.Table.from_dataframe(df_path, striped=True, bordered=True, hover=True)
            software = df_path['Модуль ПО'].unique().tolist()
            software = [i for i in software if i == i]
            software_str = [
                html.Strong('Используемое ПО: '),
                html.Span(", ".join(software))
             ]
            gantt = get_gantt(df_path, w)
            return fig, False, False, False, True, False, False, table, gantt, software_str
        elif button_id == 'reset-button-state':
            fig = plot(G, None, None, None)[0]
            return fig, True, True, True, False, True, True, None, {}, None

@app.callback(
    Output("download-xlsx", "data"),
    Input("xlsx-button", "n_clicks"),
    State('source-node', 'value'),
    State('target-node', 'value'),
    State('weight', 'value')
)
def generate_xlsx(n_clicks, source, target, w, bytes_io=None):
    if n_clicks in [0, None]:
        raise PreventUpdate
    else:
        df = plot(G, source, target, w)[2]
        name = f'{source}_{target}_{w}'
        def to_xlsx(bytes_io):
            xlsx_writer = pd.ExcelWriter(bytes_io, engine="xlsxwriter")
            df.to_excel(xlsx_writer, index=False, sheet_name="pathway")
            xlsx_writer.save()

        return send_bytes(to_xlsx, f"{name}.xlsx")


if __name__ == '__main__':
    app.run_server(host="127.0.0.1", port="8050", debug=True, use_reloader=False)
