import pandas as pd
import numpy as np
import networkx as nx
from collections import Counter
import dash
from dash import Dash, dcc, html
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import math
from typing import List
from itertools import chain
import sys
from networkx.drawing.nx_agraph import graphviz_layout
import textwrap
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import json


actions_file_name = "data/actions_reestr_graph.xlsx"
data_file_name = "data/data_model_graph.xlsx"
branching_name = "data/vetvleniq_graph.xlsx"
method_selection_block_name = "data/method_selection_blocks.xlsx"

metric_types = ["intensive"]
n_metrics = len(metric_types)


class NXGraph(nx.DiGraph):
    """
    Graph is a structure of data-vertices and process-edges. It has its own name, info and metric_types
    that can be intensive (quality, completeness) and extensive (labour expenses)
    initial_stucture is two dataframes, containing information about vertices and edges
    every hyperedge is transformed to a new vertice in the center connected with all incoming and outcoming data
    """
    
    def __init__(self, **args):
        super().__init__(self, **args)
        self.insp_counter("reset")
        
    def insp_counter(self, action="small_step"):
        if action == "reset":
            self.insp_count1 = 0
            self.insp_count2 = 0
            self.insp_count_tot = []
        elif action == "small_step":
            self.insp_count2 += 1
        elif action == "big_step":
            self.insp_count1 += 1
            self.insp_count_tot.append(self.insp_count2)
            self.insp_count2 = 0            
        return "{}.{}. ".format(self.insp_count1, self.insp_count2)        
            
    def build_structure(self, initial_structure, inspect=False, model=None):
        data_df, actions_df, other = initial_structure  # others may include branches and method selection blocks
        v_set, e_set = [], []
        
        # Add and check nodes
        self.insp_counter("big_step")
        for _,row in data_df.iterrows():  # verify repetitions
            if model is not None:
                if row['Код модели'] != model:
                    continue

            if "," in row['name']:
                for node_name in list(map(str.strip, str(row['name']).split(','))):
                    self.add_node(node_name, **dict(row))
                if inspect:
                    print(self.insp_counter() + "Вершины {} надо задавать отдельными строками".format(row["name"]))
            else:
                self.add_node(row['name'], **dict(row))

            if inspect:
                v_set.append(row['name'])
        if 'branchings' in other:
            for _,row in other['branchings'].iterrows():
                if model is not None:
                    if row['MAIN MODEL'] != model:
                        continue
                self.add_node(row['name'], **dict(row))
        if 'method_selection_blocks' in other:
            for _,row in other['method_selection_blocks'].iterrows():
                if model is not None:
                    if row['MAIN MODEL'] != model:
                        continue
                self.add_node(row['name'], **dict(row))
        if inspect:
            v_set_cnt = Counter(v_set)
            for k, v in v_set_cnt.most_common():
                if v > 1:
                    print(self.insp_counter() + "Код вершины {} повторяется {} раз".format(k, v))
            
        # Add and check actions
        self.insp_counter("big_step")
        for _,row in actions_df.iterrows():
            if model is not None:
                if row['MAIN MODEL'] != model:
                    continue

            ins = [] if type(row['ins']) != str else list(map(str.strip, str(row['ins']).split(',')))
            if "код выхода ветвления" in row and type(row["код выхода ветвления"]) == str:
                insn = list(map(str.strip, str(row["код выхода ветвления"]).split(',')))
                for inn in insn:
                    ins += [inn[:-2]] # отсекаются |1 |0           
            outs = [] if type(row['outs']) != str else list(map(str.strip, str(row['outs']).split(',')))
            self.add_node(row['name'], **dict(row))
            if inspect:
                e_set.append(row['name'])
                if row['name'] in v_set_cnt:
                    print(self.insp_counter() + "{} одновременно ребро и вершина".format(row['name']))
            if len(ins) > 0:
                for in_node in ins:
                    if in_node in self:
                        self.add_edge(in_node, row['name'])
                    elif inspect:
                        print(self.insp_counter() + "Входящая вершина {} ребра {} не определена".format(in_node, row['name']))
            else:
                print(self.insp_counter() + "У ребра {} нет входящих вершин".format(row['name']))
                
            if len(outs) > 0:
                for out_node in outs:
                    if out_node in self:
                        self.add_edge(row['name'], out_node)
                    elif inspect:
                        print(self.insp_counter() + "Выход {} ребра {} не определен".format(out_node, row['name']))
            else:
                print(self.insp_counter() + "У ребра {} нет выходов".format(row['name']))
                
        self.insp_counter("big_step")
        if inspect:
            e_set_cnt = Counter(e_set)
            for k, v in e_set_cnt.most_common():
                if v > 1:
                    print(self.insp_counter() + "Код ребра {} повторяется {} раз".format(k, v))
                    
        if inspect:
            print('Graph has {} nodes and {} edges'.format(len(self.nodes), len(self.edges)))
            print('{} simple errors found at the graph building'.format(np.sum(self.insp_count_tot)))
            comps = list(nx.weakly_connected_components(self))
            print('Found {} connected components'.format(len(comps)))
            for i, cc in enumerate(comps):
                print('{}: len={}'.format(i + 1, len(cc)))
                print(*cc)
                
def test_graph():   
    test_actions_df = pd.DataFrame.from_dict({
        'name': ['a1','a2','a3'],
        'info': ['first_action', 'second_action', 'third_action'],
        'ins': ['A, G', 'B', 'E'],
        'outs': ['B', 'C', 'D, C']})
    test_data_df = pd.DataFrame.from_dict({
        'name': ['A','B','C','E','F','G'],
        'info': ['first', 'second', 'third', 'fifth', 'sixth', 'seventh'],
        'init_metrics': [[None],[None],[8.],[None],[None],[None]]})

    my_graph = NXGraph(name="TestGraph", info="For tests")
    my_graph.build_structure(initial_structure = (test_data_df, test_actions_df, {}), inspect=True)
    
actions_df = pd.read_excel(actions_file_name)
actions_df.rename(columns={"код действия":"name",
                           "код вх источников\nсписок через зяпятую":"ins",
                           "код выхода":"outs"}, inplace=True)
data_df = pd.read_excel(data_file_name)
data_df.rename(columns={"Код":"name"}, inplace=True)
branchings_df = pd.read_excel(branching_name)
branchings_df.rename(columns={"код\nветвления":"name"}, inplace=True)
method_selection_blocks_df = pd.read_excel(method_selection_block_name)
method_selection_blocks_df.rename(columns={"код блока":"name"}, inplace=True)

my_graph = NXGraph(name="BigGraph", info="For inspection")
my_graph.build_structure(initial_structure = (data_df, actions_df,
    {'branchings':branchings_df, 'method_selection_blocks':method_selection_blocks_df}), inspect=True, model='GDM')
# my_graph.build_structure(initial_structure = (data_df, actions_df,
#     {'branchings':branchings_df, 'method_selection_blocks':method_selection_blocks_df}), inspect=True)#, model='GDM')
G = my_graph

plt.figure(figsize=(50, 50))
pos = graphviz_layout(G,
                      prog="dot",  # sfdp, neato, fdp - sparse, dot-normal,
# gvcolor, osage, unflatten, dot, neato, acyclic, gvpr, ccomps, sfdp, gc, circo, patchwork, twopi, sccmap, fdp, nop, tred.
                      root=None,
                      # args='-Gsplines=true -Gnodesep=0.6 -Goverlap=scalexy'
                      )
for node in G.nodes:
    G.nodes[node]['pos'] = tuple(pos[node])

# nx.draw(G, pos=pos, node_size=1000, node_color='lightblue', linewidths=0.25,
#         font_size=10, font_weight='bold', with_labels=True)
# # plt.show()
# plt.savefig("imagenet_layout.png")

edge_x = []
edge_y = []
edge_text = []
for edge in G.edges():
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
edge_trace.text = edge_text

node_x = []
node_y = []
colors = []
sizes = []
node_text = []
for node in G.nodes(data=True):
    code = node[0]
    node = node[1]
    x, y = node['pos']
    node_x.append(x)
    node_y.append(y)
    text = ''
    if 'Текст ветвления' in node:                   # ------ Ветвление
        colors.append('#bb00c7')  # Фиолетовый
        sizes.append(15)
        text += node['Текст ветвления']
    elif 'текст выбора метода' in node:             # ------ Блок выбора действий
        colors.append('#00d554')  # Зелёный
        sizes.append(30)
        text += node['текст выбора метода']
    elif 'ins' in node:                             # ------ Гиперребро
        colors.append('#c8c8c8')  # Серый
        sizes.append(5)
        text += f"<b>{node['текст действия']}</b>"
        if not pd.isna(node['Уровень автоматизации и развитости технологий автоматизации (автоматическое, автоматизированное, ручное)']):
            text += f"<br>Действие: <i>{node['Уровень автоматизации и развитости технологий автоматизации (автоматическое, автоматизированное, ручное)']}</i>"
        if not pd.isna(node['проекты компании направленные на развитие автоматизации методологии (в свободной форме)']):
            text += f"<br>Проекты: <i>{node['проекты компании направленные на развитие автоматизации методологии (в свободной форме)']}</i>"
    else:                                           # ------ Данные либо ветвление
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
    node_text.append('<br>'.join(textwrap.wrap(text)))


node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    # marker=dict(
        # showscale=True,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
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

node_trace.marker.color = colors
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
            x=xs[1],  # arrows' head
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
            arrowwidth=1,
            arrowcolor='black'
        )
        arrow_list.append(arrow)

fig = go.Figure(
    data=[node_trace],
    layout=go.Layout(
        title=None,
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
)
fig.update_layout(annotations=arrow_list)
fig.update_yaxes(
    scaleanchor="x",
    scaleratio=1
)

app = Dash()

# @app.callback(
#     Output('GDM', 'figure'),
#     Input('GDM', 'relayoutData'))
# def change_marker_size(relayout_data):
#     if relayout_data is None:
#         raise PreventUpdate
#     if 'dragmode' in relayout_data:
#         fig.update_layout(**relayout_data)
#         return fig
#     print(relayout_data)
#     try:
#
#         # keys_values = xaxis_config.items()
#         # xaxis = {str(key): value for key, value in keys_values}
#         if 'autosize' in relayout_data.keys() or 'xaxis.autorange' in relayout_data.keys():
#             fig.update_traces(marker_size=15)
#             fig.update_xaxes({"range": None})
#             fig.update_yaxes({"range": None})
#             return fig
#         x0 = x1 = y0 = y1 = 0
#         if 'xaxis.range[0]' in relayout_data.keys():
#             x0, x1 = relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']
#             fig.update_xaxes({"range": [x0, x1]})
#         if 'yaxis.range[0]' in relayout_data.keys():
#             y0, y1 = relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']
#             fig.update_yaxes({"range": [y0, y1]})
#         new_size = int(abs(x0-x1) / 60)
#         if new_size > 40:
#             new_size = 40
#         if new_size < 15:
#             new_size = 15
#         print(new_size)
#         fig.update_traces(marker_size=new_size)
#         return fig
#     except Exception as e:
#         print(str(e))
#         raise PreventUpdate

    # try:
    #     keys_values = xaxis_config.items()
    #     xaxis = {str(key): value for key, value in keys_values}
    #
    #     if 'autosize' in xaxis.keys():
    #         fig.update_xaxes(range=None)
    #         fig.update_yaxes(range=None)
    #     elif 'xaxis.autorange' in xaxis.keys():
    #         fig.update_xaxes(range=[x0, x1])
    #         fig.update_yaxes(range=[y0, y1])
    #     else:
    #         fig.update_xaxes(range=[xaxis['xaxis.range[0]'], xaxis['xaxis.range[1]']])
    #         fig.update_yaxes(range=[xaxis['yaxis.range[0]'], xaxis['yaxis.range[1]']])
    # except:
    #     pass



graph = dcc.Graph(id='GDM',
                  figure=fig,
                  responsive=True,
                  style={'height': '100vh'})
# graph.figure = {"data": graph.figure.data, 'layout': {'height': '100vh'}}
app.layout = html.Div(
    children=[graph],
    style={'height': '100vh'}
)
app.run_server(debug=True, use_reloader=False)
# fig.show()

