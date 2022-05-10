from backend.NXGraph import NXGraph
from resources.utils import *
import dash
from dash import Dash, dcc, html, Input, Output
import argparse

# Model name if needed
# -----------------------------
model = None
# -----------------------------

def get_graph():
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

    node_feature_weight = ['Времязатраты (1-10)', 'Сложность задачи (1-10)']
    weight_feature = ['time_exp', 'comp_exp']
    columns_feature = dict(zip(node_feature_weight, weight_feature))

    # initializing & filtering from empty nodes
    G = my_graph
    filter_graph(G)
    # add weight data to edges
    add_edge_weight(G, columns_feature)
    # rest of edges w/o any assigned weights
    empty_edges = [e for e in G.edges() if len(G[e[0]][e[1]]) != 2]  # 2 weights
    for e in empty_edges:
        for weight in weight_feature:
            G[e[0]][e[1]][weight] = 0

    LAYOUT = 'graphviz_dot'
    # selecting layout and source & target (put in interface)
    G = select_layout(G, LAYOUT)

    return G