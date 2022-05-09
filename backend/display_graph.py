import pandas as pd
from NXGraph import NXGraph
import numpy as np
import networkx as nx
import scipy

import dash
from dash import Dash, dcc, html, Input, Output
# from dash.dependencies import Input, Output
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import math
from typing import List, Dict, Tuple, Any
from itertools import chain
import sys
from networkx.drawing.nx_agraph import graphviz_layout
import textwrap
from statistics import mean
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import json
import collections

# Model name if needed
# -----------------------------
model = None
# -----------------------------

actions_file_name = "data/actions_reestr_graph.xlsx"
data_file_name = "data/data_model_graph.xlsx"
branching_name = "data/vetvleniq_graph.xlsx"
method_selection_block_name = "data/method_selection_blocks.xlsx"

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


def one_action_processed(x: tuple, actions: list = actions, returned: str = 'edge') -> tuple:
    elem = [i for i in actions if i[0] == x or i[1] == x][0]
    if returned == 'edge':
        return elem[0][0], elem[1][1]
    elif returned == 'node':
        assert elem[0][1] == elem[1][0], 'Non-transitional action'
        return elem[0][1]
    else:
        pass


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

G = my_graph

# filtering from autonomous nodes
in_ = dict(G.in_degree)
out = dict(G.out_degree)
degrees = [in_, out]
counter = collections.Counter()
for i in degrees:
    counter.update(i)
empty = dict((k, v) for k, v in counter.items() if v == 0)
for i in empty.keys():
    G.remove_node(i)
    print(f'Empty node {i}: no in & out degrees')

# Get nodes coordinates

# pos = nx.spring_layout(G)


# pos = graphviz_layout(G,
#                       prog="dot",  # sfdp, neato, fdp - sparse, dot-normal,
# gvcolor, osage, unflatten, dot, neato, acyclic, gvpr, ccomps, sfdp, gc, circo, patchwork, twopi, sccmap, fdp, nop, tred.
#                       root=None,
# args='-Gnodesep="0.2" -Gsplines=true'
# args='-Gsplines=true -Gnodesep=0.6 -Goverlap=scalexy'
# )

# test (edges highlight)
a = nx.shortest_path(G, 'S03', 'CGM|D15')
pathway = list(zip(a, a[1:]))


def network_graph(pos, pathway=pathway):
    # if pos == 'spring':
    #     pos = nx.spring_layout(G)
    # elif pos == 'graphviz_dot':
    #     pos = graphviz_layout(G, prog='dot', root=None)
    # else:
    #     return 'Unknown layout'

    # Node coordinates to graph (in 'pos' argument of a node)
    for node in G.nodes:
        G.nodes[node]['pos'] = tuple(pos[node])

    # Building edges    на их основе - annotations в виде стрелок
    edge_x = []
    edge_y = []
    edge_text = []
    one_action_node = {}  # transitional node to move at the center of merged arrow
    count = 0
    for edge in G.edges():
        # if edge in arrows:
        #     count += 1
        #     # print(count, edge)
        #     pair = one_action_processed(edge) # Генератор правильных рёбер из one-type action (действия с одним входом и выходом)
        #     try:
        #         x0, y0 = G.nodes[pair[0]]['pos']
        #         x1, y1 = G.nodes[pair[1]]['pos']
        #         x_avg, y_avg = mean([x0, x1]), mean([y0, y1])
        #         one_action_node[one_action_processed(edge, returned='node')] = (x_avg, y_avg)
        #     except KeyError:
        #         continue
        # else:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='text',
        mode='lines')


    edge_x_path = []
    edge_y_path = []
    for edge in pathway:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x_path.append(x0)
        edge_x_path.append(x1)
        edge_x_path.append(None)
        edge_y_path.append(y0)
        edge_y_path.append(y1)
        edge_y_path.append(None)

    edge_trace_scatter = go.Scatter(
        x=edge_x_path, y=edge_y_path,
        line=dict(width=10, color='#000000'),
        hoverinfo='text',
        mode='lines')


    edge_trace.text = edge_text

    # Customizing nodes
    node_x = []
    node_y = []
    colors = []
    sizes = []
    node_text = []
    borders = {}
    borders['color'] = []
    borders['width'] = []
    codes = []
    symbols = []

    symbols_dict = {'CGM': 'circle', 'KGM': 'square', 'GDM': 'hexagon', 'PFM': 'star', 'SGM': 'hexagram'}

    for node in G.nodes(data=True):
        code = node[0]
        node = node[1]
        x, y = node['pos']
        text = ''
        text += f'<b>Код:</b> {code}<br>'
        border_color = 'rgba(217,191,219,0)'
        border_width = 1
        try:
            model = node['MAIN MODEL']
        except KeyError:
            model = node['Код модели']
        symbols.append(symbols_dict[model])
        if 'Текст ветвления' in node:  # ------ Ветвление
            colors.append('#bb00c7')  # Фиолетовый
            sizes.append(15)
            text += node['Текст ветвления']
        elif 'текст выбора метода' in node:  # ------ Блок выбора действий
            colors.append('#00d554')  # Зелёный
            sizes.append(30)
            text += node['текст выбора метода']
        elif 'ins' in node:  # ------ Гиперребро (действие)

            if code in one_action_node.keys():
                x, y = one_action_node[code]
            else:
                pass

            colors.append('rgba(217,191,219,0)')  # Прозрачный
            sizes.append(5)
            border_color = 'plum'
            border_width = 2
            text += f"<b>{node['текст действия']}</b>"
            if not pd.isna(node[
                               'Уровень автоматизации и развитости технологий автоматизации (автоматическое, автоматизированное, ручное)']):
                text += f"<br>Действие: <i>{node['Уровень автоматизации и развитости технологий автоматизации (автоматическое, автоматизированное, ручное)']}</i>"
            if not pd.isna(
                    node['проекты компании направленные на развитие автоматизации методологии (в свободной форме)']):
                text += f"<br>Проекты: <i>{node['проекты компании направленные на развитие автоматизации методологии (в свободной форме)']}</i>"
        else:  # ------ Данные либо ветвление
            if node['Тип данных'] == 'Исходные':
                colors.append('#ffec00')  # Жёлтый
            elif node['Тип данных'] == 'Промежуточные':
                colors.append('#0013ff')  # Синий
            elif node['Тип данных'] == 'Ветвление':
                colors.append('#bb00c7')  # Фиолетовый
            elif node['Тип данных'] == 'Выходные':
                colors.append('#ff0000')  # Красный
            else:
                raise AttributeError("Неизвестный тип данных ноды " + code)
            sizes.append(10)
            parameter = node['Параметр']
            descriprion = node['Описание ']
            text += f"Параметр: <b>{parameter}</b>"
            if parameter != descriprion and not pd.isna(descriprion):
                text += f"<br>Описание: <i>{descriprion}</i>"
            if not pd.isna(node['Формат данных (например, .SEG-Y, .png)']):
                text += f"<br>Формат: <i>{node['Формат данных (например, .SEG-Y, .png)']}</i>"
            if not pd.isna(node['Возможные аномалии (в свободном формате)']):
                text += f"<br>Возможные аномалии: <i>{node['Возможные аномалии (в свободном формате)']}</i>"

        node_x.append(x)
        node_y.append(y)
        node_text.append('<br>'.join(textwrap.wrap(text)))
        borders['color'].append(border_color)
        borders['width'].append(border_width)
        codes.append(code)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        #     marker=dict(
        #                 line=dict(
        #                    color='plum',
        #                     width=2
        #                 )
        #     )
        # showscale=True,
        # colorscale options
        # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        # colorscale='YlGnBu',
        # reversescale=True,
        # color=[],
        # size=10,
        # colorbar=dict(
        #     thickness=15,
        #     title='Node Connections',
        #     xanchor='left',
        #     titleside='right'
        # ),
        # line_width=2)
    )

    node_trace.marker.symbol = symbols
    node_trace.marker.color = colors
    node_trace.marker.line = borders
    node_trace.text = node_text
    node_trace.marker.size = sizes

    # Adding arrows
    i = -1
    arrow_list = []
    xs = []
    ys = []
    for x, y in zip(edge_x, edge_y):
        i += 1
        if i == 2:
            i = -1
            xs = []
            ys = []
            continue
        xs.append(x)
        ys.append(y)
        if i == 1:
            arrow = dict(
                x=xs[1],  # arrows' head      Почему-то координаты наоборот
                y=ys[1],  # arrows' head
                ax=xs[0],  # arrows' tail
                ay=ys[0],  # arrows' tail
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                text='',  # if you want only the arrow
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=0.5,
                arrowcolor='grey'
            )
            arrow_list.append(arrow)

    i = -1
    arrow_list_path = []
    xs_path = []
    ys_path = []
    for x, y in zip(edge_x_path, edge_y_path):
        i += 1
        if i == 2:
            i = -1
            xs_path = []
            ys_path = []
            continue
        xs_path.append(x)
        ys_path.append(y)
        if i == 1:
            arrow = dict(
                x=xs_path[1],  # arrows' head      Почему-то координаты наоборот
                y=ys_path[1],  # arrows' head
                ax=xs_path[0],  # arrows' tail
                ay=ys_path[0],  # arrows' tail
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                text='',  # if you want only the arrow
                showarrow=True,
                arrowhead=3,
                arrowsize=3,
                arrowwidth=2,
                arrowcolor='black'
            )
            arrow_list_path.append(arrow)

    fig = go.Figure(
        data=[node_trace],
        layout=go.Layout(
            title=None,
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
    )

    # for x, y, code in zip(node_x, node_y, codes):
    #     fig.add_annotation(x=x, y=y, text=code)

    fig.update_layout(annotations=arrow_list)
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1
    )
    return fig


app = dash.Dash()
app.title = 'Graph knowledge'

app.layout = html.Div([

    dcc.Dropdown(id='dropdown', options=[
        {'label': 'spring', 'value': 'spring'},
        {'label': 'graphviz_dot', 'value': 'graphviz_dot'}],
                 value='spring'),

    dcc.Graph(id='graph-network',
              style={'height': '100vh'}
              )

])


@app.callback(
    Output('graph-network', 'figure'),
    [Input('dropdown', 'value')],
)
def update_output(pos):
    if pos == 'spring':
        pos = nx.spring_layout(G)
    elif pos == 'graphviz_dot':
        pos = graphviz_layout(G, prog='dot', root=None)
    else:
        return 'Unknown layout'
    return network_graph(pos)

app.run_server(debug=True, use_reloader=False)

#
# graph = dcc.Graph(id='GDM',
#                   figure=fig,
#                   responsive=True,
#                   style={'height': '100vh'})
# # graph.figure = {"data": graph.figure.data, 'layout': {'height': '100vh'}}
# app.layout = html.Div(
#     children=[graph],
#     style={'height': '100vh'}
# )

