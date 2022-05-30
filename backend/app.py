from typing import Any, Dict, Union, Optional
from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State
from dash_extensions import Download
import dash_bootstrap_components as dbc
from dash_extensions.snippets import send_bytes
from dash.exceptions import PreventUpdate

import pandas as pd
from networkx import DiGraph, descendants
from backend.graph import columns_feature
from resources.utils import plot, get_nodes_labels
from resources.gantt import get_gantt, create_xml

# the style arguments for the sidebar (also try: "position": "fixed")
SIDEBAR_STYLE = {
    "position": "absolute",
    # "overflow-y": "scroll",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "30rem",
    "padding": "2rem 2rem 1rem 2rem",
    "background-color": "#f8f9fa",
}

# the style arguments for the main content position it to the right of the sidebar
TABS_STYLE = {
    "margin-left": "31rem",
    "margin-right": "2rem",
    "margin-bottom": "1rem",
    "padding": "1rem 1rem",
}

# the style arguments for content of each tab
CONTENT_STYLE = {
    'margin-top': '10px',
    'width': "150vh",
    "height": "90vh"
}

def launch_app(g: DiGraph,
               layout: str,
               source: Optional[Any],
               target: Optional[Any],
               weight: Optional[Any],
               single_ended: list,
               sidebar_style: Dict[str, Union[str, int]] = SIDEBAR_STYLE,
               tabs_style: Dict[str, str] = TABS_STYLE,
               content_style: Dict[str, str] = CONTENT_STYLE) -> Dash:
    """
    Launch sidebar web-app with tabs inside of page
    """
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.FLATLY],
        assets_folder='./assets'
    )
    app.title = 'Graph knowledge'

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
                options=get_nodes_labels(g, g.nodes(), filter_hyperedge=True),
                multi=True,
                style={
                    'font-size': '16px',
                    'width': '27rem',
                    # 'display': 'inline-block',
                    'margin-bottom': '5px'
                },
            ),
            dcc.Dropdown(
                id='target-node',
                placeholder='Select the target ...',
                searchable=True,
                optionHeight=90,
                options=get_nodes_labels(g, g.nodes(), filter_hyperedge=True),
                disabled=True,
                multi=True,
                style={
                    'font-size': '16px',
                    'width': '27rem',
                    # 'display': 'inline-block',
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
                style={'textAlign': 'center', 'margin': 'auto', "margin-bottom": "100px"}
            ),
            html.Hr(),
            html.P(
                "Select suitable layout style for representation", className="text"
            ),
            dcc.Dropdown(
                id='prog-layout',
                placeholder='Select layout style ...',
                searchable=False,
                options=['dot', 'twopi', 'sfdp'],
                value=layout,
                style={
                    'font-size': '16px',
                    'width': '27rem',
                    # 'display': 'inline-block',
                    'margin-bottom': '5px'
                },
            ),
            html.Div(
                [
                    dbc.Button(
                        id='update-layout',
                        outline=True,
                        color="info",
                        className="me-1",
                        n_clicks=0,
                        children='Update layout',
                        style={
                            'margin-top': '15px',
                            'margin-right': '5px',
                        },
                    ),
                ],
                className='d-grid gap-2 col-9 mx-auto'
            ),

        ],
        style=sidebar_style,
    )

    graph = dcc.Graph(
        id='GDM',
        figure=plot(g, source, target, weight)[0],
        responsive=True,
        style=content_style
    )

    table_object = html.Div(
        [
            html.Div(id='gantt-table', children='test_text'),
        ],
        style=content_style
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

    setup_object = html.Div(
        [
            dbc.Button(
                id='update-graph',
                color='success',
                children='Update visible',
                n_clicks=0
            ),
            dcc.Checklist(
                id="all-or-none",
                options=[{"label": "Select All", "value": "All"}],
                value=["All"],
                labelStyle={"display": "inline-block"},
                inputStyle={"margin-right": "10px"}
            ),
            dcc.Checklist(
                id='features-select',
                options=get_nodes_labels(g, single_ended),
                value=single_ended,
                labelStyle=dict(display='block'),
                inputStyle={"margin-right": "10px"},
                style={
                    'width': "100vh",
                    "height": "80vh",
                    "overflow": "auto"
                }
            ),
        ],
        style={
            'margin-top': '10px',
            'width': "100vh",
            "height": "90vh"
        }
    )

    tabs = {
        'Graph': [False, graph, '🧠'],
        'Table': [True, table_object, '🗄️'],
        'Gantt chart': [True, gantt_object, '📈'],
        'Setup': [False, setup_object, '⚙️']
    }

    content = dbc.Container(
        dbc.Tabs(
            [
                dbc.Tab(
                    id=k,
                    children=v[1],
                    label=f"{v[2]} {k}",
                    tabClassName="flex-grow-2 text-center",
                    disabled=v[0]
                )
                for k, v in tabs.items()
            ]
        ),
        className="p-4",
        style=tabs_style
    )

    app.layout = html.Div([sidebar, content])

    @app.callback(
        Output('target-node', 'options'),
        Output('target-node', 'disabled'),
        Input('source-node', 'value')
    )
    def update_target(source):
        if source in [0, None]:
            raise PreventUpdate
        else:
            target_options = []
            for s in source:  # for 1-item list
                target_options = descendants(g, s)
            return get_nodes_labels(g, target_options, filter_hyperedge=True), False

    @app.callback(
        [
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
            Output('prog-layout', 'value')
        ],
        [
            Input('submit-button-state', 'n_clicks'),
            State('source-node', 'value'),
            State('target-node', 'value'),
            State('weight', 'value'),
            Input('reset-button-state', 'n_clicks'),
            Input('update-graph', 'n_clicks'),
            State('features-select', 'value'),
            State('prog-layout', 'value'),
            Input('update-layout', 'n_clicks')

        ]
    )
    def update_output(submit, source, target, w, reset, update, features_selected, layout, update_layout):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'submit-button-state':
                fig, nodes_path, df_path = plot(g, source, target, w, layout=layout)
                table = dbc.Table.from_dataframe(df_path, striped=True, bordered=True, hover=True)
                software = df_path['Модуль ПО'].unique().tolist()
                software = [i for i in software if i == i]
                software = list(set(map(lambda x: x.strip(), ','.join(software).split((',')))))
                software_str = [
                    html.Strong('Используемое ПО: '),
                    html.Span(", ".join(software))
                ]
                gantt = get_gantt(df_path, w)[0]
                return [fig, False, False, False, True, False, False, table, gantt, software_str, layout]
            elif button_id == 'reset-button-state':
                fig = plot(g, None, None, None)[0]
                return [fig, True, True, True, False, True, True, None, {}, None, 'dot']
            elif button_id == 'update-graph':
                exceptions = list(set(single_ended) - set(features_selected))
                fig = plot(g, None, None, None, nodes_except=exceptions, layout=layout)[0]
                return [fig, False, True, True, False, True, True, None, {}, None, layout]
            elif button_id == 'update-layout':
                # G = select_layout_graphviz(G, layout)
                fig = plot(g, None, None, None, layout=layout)[0]
                return [fig, False, True, True, False, True, True, None, {}, None, layout]

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
            df = plot(g, source, target, w)[2]
            name = f'{source}_{target}_{w}'

            def to_xlsx(bytes_io):
                xlsx_writer = pd.ExcelWriter(bytes_io, engine="xlsxwriter")
                df.to_excel(xlsx_writer, index=False, sheet_name="pathway")
                xlsx_writer.save()

            return send_bytes(to_xlsx, f"{name}.xlsx")

    @app.callback(
        Output("download-xml", "data"),
        Input("xml-button", "n_clicks"),
        State('source-node', 'value'),
        State('target-node', 'value'),
        State('weight', 'value')
    )
    def generate_xml(n_clicks, source, target, w):
        if n_clicks in [0, None]:
            raise PreventUpdate
        else:
            df_path = plot(g, source, target, w)[2]  # csv
            gantt = get_gantt(df_path, w)[1]
            name = f'{source}_{target}_{w}'

            def to_xml(bytes_io):
                stream = create_xml(gantt, w, name)
                bytes_io.write(stream)

            return send_bytes(to_xml, f"{name}.xml")

    @app.callback(
        Output("features-select", "value"),
        Output("all-or-none", "value"),
        Input("features-select", "value"),
        Input("all-or-none", "value"),
    )
    def sync_checklists(options_selected, all_selected):
        ctx = callback_context
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if input_id == "features-select":
            all_selected = ["All"] if set(options_selected) == set(single_ended) else []
        else:
            options_selected = single_ended if all_selected else []
        return options_selected, all_selected

    # @app.callback(
    #     Output("features-select", "value"),
    #     [Input("all-or-none", "value")],
    #     [State("features-select", "options")],
    # )
    # def select_all_none(all_selected, options):
    #     all_or_none = []
    #     all_or_none = [option["value"] for option in options if all_selected]
    #     return all_or_none

    return app
