from backend.graph import init_graph
from backend.app import launch_app
from resources.utils import select_layout_graphviz, get_single_ended_nodes
import os

PATH = os.path.dirname(os.path.realpath(__file__))
DATA = 'data_2505' # data folder
LAYOUT = 'dot' # assign the basic layout (dot)
SOURCE, TARGET, WEIGHT = None, None, None # to launch the app

# initializing, filtering from empty nodes & add weight data to edges
G = init_graph(root=PATH, data_folder=DATA, filter_autonomous=True)

# select layout and source & target (put in interface)
G = select_layout_graphviz(G, LAYOUT)

# find only single nodes for setup tab (put in interface)
single_ended_nodes = get_single_ended_nodes(G)

app = launch_app(
    g=G,
    layout=LAYOUT,
    source=SOURCE,
    target=TARGET,
    weight=WEIGHT,
    single_ended=single_ended_nodes
)


if __name__ == '__main__':
    app.run_server(host="127.0.0.1", port=8050, debug=True, use_reloader=False)