import collections
from typing import Dict, Tuple, List, Any, Union, Optional
import pandas as pd
from networkx import DiGraph
from backend.NXGraph import NXGraph

# Weights features
# ----------------------------------------------------------------------------------------------------
node_feature_weight = ['Времязатраты (1-10)', 'Сложность задачи (1-10)', 'Трудозатраты, чел*часов']
weight_feature = ['time_exp', 'comp_exp', 'work_exp']
columns_feature = dict(zip(node_feature_weight, weight_feature))
# ----------------------------------------------------------------------------------------------------


def init_graph(data_folder: str,
               model: str = None,
               filter_autonomous: bool = True,
               weights: Dict[str, str] = columns_feature,
               filter_one_to_one_action: bool = False) -> Union[Tuple[DiGraph, Optional[Any], Optional[Any]], DiGraph]:
    """
    Initialization of graph structure via existing data (actions, model,
    branching and method selection blocks)
    """
    # paths to files
    actions_fname = f"./{data_folder}/actions_reestr_graph.xlsx"
    data_fname = f"./{data_folder}/data_model_graph.xlsx"
    branching_fname = f"./{data_folder}/vetvleniq_graph.xlsx"
    method_fname = f"./{data_folder}/method_selection_blocks.xlsx"

    # ----- actions -----
    actions_df = pd.read_excel(actions_fname)
    actions_df.rename(
        columns={
            "код действия": "name",
            "код вх источников\nсписок через зяпятую": "ins",
            "код выхода": "outs"
        }, inplace=True)
    # ----- data -----
    data_df = pd.read_excel(data_fname)
    data_df.rename(
        columns={
            "Код": "name",
            'Тип даных': 'Тип данных'
        }, inplace=True)
    # ----- branching -----
    branchings_df = pd.read_excel(branching_fname)
    branchings_df.rename(
        columns={
            "код\nветвления": "name"
        }, inplace=True)
    # ----- method selection -----
    method_df = pd.read_excel(method_fname)
    method_df.rename(
        columns={
            "код блока": "name"
        }, inplace=True)

    # filtering one-in one-output actions (deprecated)
    if filter_one_to_one_action:
        actions_df, arrows, actions = filter_one_to_one_action(actions_df)
    else:
        arrows, actions = None, None
        pass

    # building graph
    my_graph = NXGraph(name="BigGraph", info="For inspection")
    my_graph.build_structure(
        initial_structure=(
            data_df,
            actions_df,
            {
                'branchings': branchings_df,
                'method_selection_blocks': method_df
            }
        ),
        inspect=True,
        model=model
    )

    if filter_autonomous:
        my_graph = filter_graph(my_graph)

    # add weight data to edges
    my_graph = add_edge_weight(my_graph, weights)

    if arrows or actions:
        return my_graph, arrows, actions
    else:
        return my_graph


def filter_one_to_one_action(actions_df: pd.DataFrame) -> Tuple[pd.DataFrame, list, List[Tuple[Any, Any]]]:
    """
    Filtering one-in & one-output actions to merge two arrows into one with action
    in the center of resulted arrow (deprecated)
    """
    cols = ['name', 'ins', 'outs']
    for col in cols:
        actions_df[col] = actions_df[col].str.replace(' ', '')

    cond1 = (actions_df.ins.str.split(',').str.len() == 1)
    cond2 = (actions_df.outs.str.split(',').str.len() == 1)
    one_action = actions_df[cond1 & cond2].copy()

    actions_df.drop(one_action.index, inplace=True)  # <--- тут может быть ошибка
    arrows = list(zip(one_action.ins, one_action.name)) + list(zip(one_action.name, one_action.outs))
    actions = list(zip(zip(one_action.ins, one_action.name), zip(one_action.name, one_action.outs)))
    return actions_df, arrows, actions


def filter_graph(g: DiGraph) -> DiGraph:
    """
    # Filtering graph from autonomous nodes
    """
    in_ = dict(g.in_degree)
    out = dict(g.out_degree)
    degrees = [in_, out]
    counter = collections.Counter()
    for i in degrees:
        counter.update(i)
    empty = dict((k, v) for k, v in counter.items() if v == 0)
    for i in empty.keys():
        g.remove_node(i)
        print(f'Empty node {i}: no in & out degrees')  # filtering from autonomous nodes

    return g


def check_io_action(g: DiGraph, node: str, col: str) -> Optional[List[str]]:
    """
    Check whether ins and outs instance for action node is str value
    """
    val = g.nodes[node][col]
    if isinstance(val, str):
        lst = val.split(',')  # list
        return lst
    else:
        print(f'Non-str instance in node for {col} in {node}: {val}')
        return None


def add_edge_weight(g: DiGraph,
                    columns: dict,
                    col_in: str = 'ins',
                    col_out: str = 'outs',
                    weight_filler: int = 0) -> DiGraph:
    """
    Assign additional data to allow find path by node weight
    """
    for node in g.nodes:
        for old, new in columns.items():
            try:
                end_keys = check_io_action(g, node, col_out)
                start_keys = check_io_action(g, node, col_in)
                val = g.nodes[node][old]
            except KeyError:
                continue
            if end_keys:
                for i in end_keys:
                    try:
                        g[node][i][new] = round(val / len(end_keys), 1)
                    except Exception as e:
                        print(f'{e}: Node {i} not found (as end)')
            if start_keys:
                for j in start_keys:
                    try:
                        g[j][node][new] = weight_filler
                    except Exception as e:
                        print(f'{e}: Node {j} not found (as start)')

    # rest of edges w/o any assigned weights
    empty_edges = [e for e in g.edges() if len(g[e[0]][e[1]]) != len(columns)]  # 3 weights
    for e in empty_edges:
        for weight in columns.values():
            g[e[0]][e[1]][weight] = weight_filler

    return g