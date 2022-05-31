import copy
import itertools
from typing import Tuple, Union, List, Any, Optional, Dict
from networkx import DiGraph, shortest_path, spring_layout
import pandas as pd
from networkx.drawing.nx_agraph import graphviz_layout
import plotly.graph_objects as go
import textwrap

from resources.table import preprocess_pathway
from backend.graph import filter_graph
from os import makedirs

# Color scheme
# --------------------
сolors_scheme = {'CGM': '#EF476F', 'KGM': '#E09D00', 'GDM': '#06D6A0', 'PFM': '#118AB2', 'SGM': '#031D25'}
# --------------------


# processing nodes with one in & one out edges (deprecated)
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


def pathway(g: DiGraph,
            source: str,
            target: str,
            weight: str,
            debug: bool = False) -> Tuple[Union[list, dict], List[Tuple[Any, Any]], pd.DataFrame]:
    """
    Find path between two nodes
    """
    source = source[0]
    target = target[0]
    nodes = shortest_path(g, source, target, weight=weight)
    edges = list(zip(nodes, nodes[1:]))

    data = []
    for el in nodes:
        d = g.nodes[el]
        data.append(d)
    res = preprocess_pathway(pd.DataFrame(data, index=list(range(len(data)))))
    res['Трудозатраты, чел*часов'] = res['Трудозатраты, чел*часов'].astype(float)

    if debug:
        makedirs('./results', exist_ok=True)
        res.to_csv(f'./results/{source}_{target}_{weight}.csv', index=False)
    return nodes, edges, res


def select_layout_graphviz(g: DiGraph, pos: str) -> DiGraph:
    """
    Append position data to graph in terms of selected graphviz layout from interface and return updated graph
    """
    pos = graphviz_layout(g, prog=pos, root=None)

    for node in g.nodes:
        g.nodes[node]['pos'] = tuple(pos[node])
    return g


# Append position data to graph in terms of selected layout from interface and return updated G (deprecated)
def select_layout(G, pos):
    if pos == 'spring':
        pos = spring_layout(G)
    elif pos == 'dot':
        pos = graphviz_layout(G, prog='dot', root=None)
    else:
        return 'Unknown layout'
    for node in G.nodes:
        G.nodes[node]['pos'] = tuple(pos[node])
    return G


def build_edge(g: DiGraph, edges: List[Tuple[Any, Any]]) -> Tuple[List[Optional[Any]], List[Optional[Any]]]:
    """
    Building edges (basement for annotations in 'arrow'-type style)
    """
    edge_x = []
    edge_y = []
    for edge in edges:
        x0, y0 = g.nodes[edge[0]]['pos']
        x1, y1 = g.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    return edge_x, edge_y


def edge_to_arrow(edge_x: List[Optional[Any]],
                  edge_y: List[Optional[Any]],
                  size: float,
                  width: float,
                  color: str,
                  opacity: float) -> List[Dict[str, Union[str, bool, int]]]:
    """
    Adding arrows to edges
    """
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


def custom_nodes(nodes: list,
                 colors_dict: Dict[str, str],
                 nodes_from_path: Union[list, dict],
                 alpha: float = 0.3,
                 border_color: str = '#f0ffff',  # azure
                 border_width: float = 1.5) -> pd.DataFrame:
    """
    Customizing nodes
    """
    node_x = []
    node_y = []
    colors = []
    sizes = []
    node_text = []
    borders = {'color': [], 'width': []}
    codes = []
    symbols = []
    opacities = []
    models = []

    for node in nodes:
        code = node[0]
        node = node[1]
        x, y = node['pos']
        text = ''
        text += f'<b>Код:</b> {code}<br>'
        try:
            model = node['MAIN MODEL']
        except KeyError:
            model = node['Код модели']

        models.append(model)
        color_default = colors_dict[model]

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
            sizes.append(14)
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
                symbols.append('star-triangle-down')  # Синий
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

    node_data = pd.DataFrame(
        zip(models, node_x, node_y, node_text, sizes, symbols, colors, borders['color'], borders['width'], opacities),
        columns = ['model', 'x', 'y', 'hover', 'size', 'symbol', 'color', 'border_color', 'border_width', 'opacity']
    )
    return node_data

# --------------------------------------------
symbols_dict = {
    'Блок выбора': 'diamond',
    'Ветвление': 'triangle-up',
    'Выходные': 'circle-dot',
    'Исходные': 'circle-x',
    'Промежуточные': 'star-triangle-down',
}
# --------------------------------------------
models = сolors_scheme.keys()
tags = symbols_dict.keys()
label_legend = {f'{r[0]} - {r[1]}':[сolors_scheme[r[0]], symbols_dict[r[1]]] for r in itertools.product(models, tags)}


def divide_node_data(nodes: pd.DataFrame, labels: Dict[str, str]) -> List[go.Scatter]:
    """
    Division of node data by type of data according to labels bio
    """
    node_trace = []
    hyper_edges = nodes[nodes['color'] == '#f0ffff'].copy() # фильтрация на гиперрёбра, добавляем в конце вне цикла
    nodes = nodes[nodes['color'] != '#f0ffff'].copy()

    for label, val in labels.items():
        df = nodes[(nodes['color'] == val[0]) & (nodes['symbol'] == val[1])]

        node_model = go.Scatter(
            x=df['x'],
            y=df['y'],
            name=label,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                color=val[0],
                size=df['size'],
                opacity=df['opacity'],
                line=dict(
                    width=df['border_width'],
                    color=df['border_color']
                ),
                symbol=val[1]
            ),
            text=df['hover'],
            showlegend=True
        )
        node_trace.append(node_model)

    hyper_trace = go.Scatter(
        x=hyper_edges['x'],
        y=hyper_edges['y'],
        name='Гиперребро',
        mode='markers',
        hoverinfo='text',
        marker=dict(
            color=hyper_edges['color'],
            size=hyper_edges['size'],
            opacity=hyper_edges['opacity'],
            line=dict(
                width=hyper_edges['border_width'],
                color=hyper_edges['border_color']
            ),
            symbol=hyper_edges['symbol']
        ),
        text=hyper_edges['hover'],
        showlegend=True
        )
    node_trace.append(hyper_trace)
    return node_trace


def draw_figure(node: List[go.Scatter],
                arrow: List[Dict[str, Union[str, bool, int]]],
                path_way: List[Dict[str, Union[str, bool, int]]] = None) -> go.Figure:
    """
    Draw the figure with the graph
    """
    fig = go.Figure(
        data=node,
        layout=go.Layout(
            title=None,
            # titlefont_size=16,
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
    )

    if path_way:
        arrow = arrow + path_way
    fig.update_layout(annotations=arrow)
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1
    )

    fig.update_layout(
        legend_title_text='Обозначения:',
        # legend = dict(
        #     x=0.01,
        #     y=0.99,
        #     bordercolor="Grey",
        #     bgcolor="#f0ffff",
        #     borderwidth=0.5
        # )
    )
    return fig


def get_single_ended_nodes(g: DiGraph, subset: list = None) -> list:
    """
    Select single-ended nodes by subset (only input or output)
    """
    if subset:
        return [i for i in subset if g.in_degree()[i] == 0 or g.out_degree()[i] == 0]
    else:
        return [i for i in list(g.nodes()) if g.in_degree()[i] == 0 or g.out_degree()[i] == 0]


def remove_nodes_n_edges(g: DiGraph, nodes_except: list) -> Tuple[DiGraph, list]:
    """
    Graph filtration ('setup' tab): remove node and autonomous edges
    """
    edges_except = [(start, end) for start, end in g.edges if start in nodes_except or end in nodes_except]
    g.remove_nodes_from(nodes_except)
    g.remove_edges_from(edges_except)

    # поиск связанных нод
    linked_nodes = list(set(list(itertools.chain.from_iterable(edges_except))) - set(nodes_except))
    return g, linked_nodes


def plot(g: DiGraph,
         source: str = None,
         target: str = None,
         weight: str = None,
         сolors: Dict[str, str] = сolors_scheme,
         nodes_except: list = None,
         layout: str = 'dot') -> Tuple[go.Figure, Union[None, list, dict], Optional[pd.DataFrame]]:
    """
    Draw the whole plot -- main drawing functionality
    """
    g = select_layout_graphviz(g, layout)
    g = copy.deepcopy(g) # to avoid removing edges after second and following tries

    # remove nodes and edges from the exceptions list
    if not nodes_except:
        pass
    else:
        g, linked_nodes = remove_nodes_n_edges(g, nodes_except)
        autonomous = get_single_ended_nodes(g, linked_nodes)
        g, linked_nodes_2 = remove_nodes_n_edges(g, autonomous)
        g = filter_graph(g)

        # g.remove_nodes_from(nodes_except)
        # edges_except = [(start, end) for start, end in g.edges if start in nodes_except or end in nodes_except]
        # g.remove_edges_from(edges_except)

    # classic layout - full graph
    if not (source and target and weight):
        edge_x, edge_y = build_edge(g, g.edges())
        arrow_list = edge_to_arrow(edge_x, edge_y, 2.0, 0.5, 'grey', 0.9)
        nodes_path, pathway_list = None, None
        df_path = None # нет никакого пути

    # pathway layout
    else:
        nodes_path, edges_path, df_path = pathway(g, source, target, weight)
        # preparing edges
        g.remove_edges_from(edges_path)
        edge_x, edge_y = build_edge(g, g.edges())
        arrow_list = edge_to_arrow(edge_x, edge_y, 2.0, 0.5, 'grey', 0.3)
        edge_x_path, edge_y_path = build_edge(g, edges_path)
        pathway_list = edge_to_arrow(edge_x_path, edge_y_path, 1, 1.5, '#432E36', 1)

    # preparing nodes
    node_data = custom_nodes(g.nodes(data=True), colors_dict=сolors, nodes_from_path=nodes_path)
    node_trace = divide_node_data(node_data, labels=label_legend)
    fig = draw_figure(node_trace, arrow_list, path_way=pathway_list)

    return fig, nodes_path, df_path


def find_description(g: DiGraph, node: str, max_symbols: int = 150) -> str:
    """
    Get description of the node regardless of the type
    """
    try:
        description = g.nodes[node]['Параметр']
    except KeyError:
        try:
            description = g.nodes[node]['текст действия']
        except KeyError:
            try:
                description = g.nodes[node]['Текст ветвления']
            except KeyError:
                description = g.nodes[node]['текст выбора метода']

    if '\n' in str(description):
        description = description.replace('\n', ' ')
    else:
        pass
    return str(description)[:max_symbols]


def get_nodes_labels(g: DiGraph, nodes: list, filter_hyperedge: bool = False) -> List[Dict[str, str]]:
    """
    Find nodes labels for options in dropdown & checklist
    """
    nodes_l = list(nodes)

    # фильтрация только на вершины (без гиперрёбер)
    if filter_hyperedge:
        nodes_l = [i for i in nodes_l if 'текст действия' not in g.nodes()[i].keys()]
    else:
        pass

    description = [find_description(g, i) for i in nodes_l]
    nodes_describe = zip(nodes_l, description)
    nodes_labels = [{'label': f"{k} - {v}", 'value': k} for k, v in nodes_describe if isinstance(k, str) is True]
    nodes_sorted = sorted(nodes_labels, key=lambda d: d['value'])
    return nodes_sorted
