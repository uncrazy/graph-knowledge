import collections
import networkx as nx
import pandas as pd
from networkx.drawing.nx_agraph import graphviz_layout
import plotly.graph_objects as go
import textwrap
from .table import preprocess_pathway


# Color scheme
# --------------------
сolors_dict = {'CGM': '#EF476F', 'KGM': '#E09D00', 'GDM': '#06D6A0', 'PFM': '#118AB2', 'SGM': '#031D25'}
# --------------------


def one_action_processed(x: tuple,
                         actions: list,
                         returned: str = 'edge') -> tuple:
    elem = [i for i in actions if i[0] == x or i[1] == x][0]
    if returned == 'edge':
        return elem[0][0], elem[1][1]
    elif returned == 'node':
        assert elem[0][1] == elem[1][0], 'Non-transitional action'
        return elem[0][1]
    else:
        pass


# Filtering from autonomous nodes
def filter_graph(G):
    in_ = dict(G.in_degree)
    out = dict(G.out_degree)
    degrees = [in_, out]
    counter = collections.Counter()
    for i in degrees:
        counter.update(i)
    empty = dict((k, v) for k, v in counter.items() if v == 0)
    for i in empty.keys():
        G.remove_node(i)
        print(f'Empty node {i}: no in & out degrees')  # filtering from autonomous nodes


# check if ins and outs instance for action is str value
def check_INOUT_action(G, node, col):
    val = G.nodes[node][col]
    if isinstance(val, str):
        lst = val.split(',')  # list
        return lst
    else:
        print(f'Non-str instance in node for {col} in {node}: {val}')
        return None


# Add additional data to allow find path by node weight
def add_edge_weight(G, columns, col_in='ins', col_out='outs', weight_filler=0):
    for node in G.nodes:
        for old, new in columns.items():
            try:
                end_keys = check_INOUT_action(G, node, col_out)
                start_keys = check_INOUT_action(G, node, col_in)
                val = G.nodes[node][old]
            except KeyError:
                continue
            if end_keys:
                for i in end_keys:
                    try:
                        G[node][i][new] = round(val / len(end_keys), 1)
                    except Exception as e:
                        print(f'{e}: Node {i} not found (as end)')
            if start_keys:
                for j in start_keys:
                    try:
                        G[j][node][new] = weight_filler
                    except Exception as e:
                        print(f'{e}: Node {j} not found (as start)')


# Find path between two nodes
def pathway(G, source, target, weight, save=True):
    nodes = nx.shortest_path(G, source, target, weight=weight)
    edges = list(zip(nodes, nodes[1:]))

    if save:
        data = []
        for el in nodes:
            d = G.nodes[el]
            data.append(d)
        res = preprocess_pathway(pd.DataFrame(data, index=list(range(len(data)))))
        # res.to_csv(f'./results/{source}_{target}_{weight}.csv', index=False)

    return nodes, edges


# Append position data to graph in terms of selected layout from interface and return updated G
def select_layout(G, pos):
    if pos == 'spring':
        pos = nx.spring_layout(G)
    elif pos == 'graphviz_dot':
        pos = graphviz_layout(G, prog='dot', root=None)
    else:
        return 'Unknown layout'
    for node in G.nodes:
        G.nodes[node]['pos'] = tuple(pos[node])
    return G


# Building edges  (на их основе - annotations в виде стрелок)
def build_edge(G, edges):
    edge_x = []
    edge_y = []
    for edge in edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    return edge_x, edge_y


# Adding arrows
def edge_to_arrow(edge_x, edge_y, size, width, color, opacity):
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
                arrowsize=size,
                arrowwidth=width,
                arrowcolor=color,
                opacity=opacity
            )
            arrow_list.append(arrow)
    return arrow_list


# Customizing nodes
def custom_edges(nodes, сolors_dict, nodes_from_path=None, alpha=0.3):
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
    opacities = []

    for node in nodes:
        code = node[0]
        node = node[1]
        x, y = node['pos']
        text = ''
        text += f'<b>Код:</b> {code}<br>'
        border_color = '#f0ffff'  # azure
        border_width = 1.5
        try:
            model = node['MAIN MODEL']
        except KeyError:
            model = node['Код модели']

        # if nodes_from_path:
        #     if code in nodes_from_path:
        #         color_default = сolors_dict[model]
        #     else:
        #         color_default = 'grey'
        # else:
        #     color_default = сolors_dict[model]

        color_default = сolors_dict[model]

        if nodes_from_path:
            if code in nodes_from_path:
                opacity = 1.0
            else:
                opacity = alpha
        else:
            opacity = 1.0

        if 'Текст ветвления' in node:  # ------ Ветвление
            sizes.append(14)
            symbols.append('triangle-up')
            colors.append(color_default)
            text += node['Текст ветвления']
        elif 'текст выбора метода' in node:  # ------ Блок выбора действий
            sizes.append(25)
            symbols.append('diamond')
            colors.append(color_default)
            text += node['текст выбора метода']
        elif 'ins' in node:  # ------ Гиперребро (действие)
            # if code in one_action_node.keys():
            #     x, y = one_action_node[code]
            # else:
            #     pass
            sizes.append(5)
            symbols.append('circle')
            colors.append('#f0ffff')  # Прозрачный
            text += f"<b>{node['текст действия']}</b>"
            border_color = '#44355B'
            border_width = 2
            if not pd.isna(node[
                               'Уровень автоматизации и развитости технологий автоматизации (автоматическое, автоматизированное, ручное)']):
                text += f"<br>Действие: <i>{node['Уровень автоматизации и развитости технологий автоматизации (автоматическое, автоматизированное, ручное)']}</i>"
            if not pd.isna(
                    node[
                        'проекты компании направленные на развитие автоматизации методологии (в свободной форме)']):
                text += f"<br>Проекты: <i>{node['проекты компании направленные на развитие автоматизации методологии (в свободной форме)']}</i>"
        else:  # ------ Данные либо ветвление
            sizes.append(14)
            if node['Тип данных'] == 'Исходные':
                symbols.append('circle-x')  # Круг с крестиком
            elif node['Тип данных'] == 'Промежуточные':
                symbols.append('star-triangle-up')  # Синий
            elif node['Тип данных'] == 'Ветвление':
                symbols.append('triangle-up')  # Треугольник
            elif node['Тип данных'] == 'Выходные':
                symbols.append('circle-dot')  # Кружок с точкой
            else:
                raise AttributeError("Неизвестный тип данных ноды " + code)
            colors.append(color_default)
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
        opacities.append(opacity)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text'
    )

    node_trace.marker.opacity = opacities
    node_trace.marker.symbol = symbols
    node_trace.marker.color = colors
    node_trace.marker.line = borders
    node_trace.text = node_text
    node_trace.marker.size = sizes

    return node_trace


# Draw the figure with the graph
def draw_figure(node, arrow, pathway=None):
    fig = go.Figure(
        data=[node],
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

    if pathway:
        arrow = arrow + pathway
    fig.update_layout(annotations=arrow)
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1
    )

    return fig


# Final plot
def plot(g, source=None, target=None, weight=None, сolors=сolors_dict):
    if not (source and target and weight):
        edge_x, edge_y = build_edge(g, g.edges())
        arrow_list = edge_to_arrow(edge_x, edge_y, 2, 0.5, 'grey', 0.9)
        nodes_path, pathway_list = None, None
    else:
        nodes_path, edges_path = pathway(g, source, target, weight)
        # preparing edges
        g.remove_edges_from(edges_path)
        edge_x, edge_y = build_edge(g, g.edges())
        arrow_list = edge_to_arrow(edge_x, edge_y, 2, 0.5, 'grey', 0.3)
        edge_x_path, edge_y_path = build_edge(g, edges_path)
        pathway_list = edge_to_arrow(edge_x_path, edge_y_path, 1, 1.5, '#432E36', 1)

    # preparing nodes
    node_trace = custom_edges(g.nodes(data=True), сolors, nodes_from_path=nodes_path)
    fig = draw_figure(node_trace, arrow_list, pathway=pathway_list)

    return fig