import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
from resources.utils import plot
from dash.exceptions import PreventUpdate


def create_dash_app(G, requests_pathname_prefix: str = None) -> dash.Dash:
    """
    Sample Dash application from Plotly: https://github.com/plotly/dash-hello-world/blob/master/app.py
    """
    dash_app = dash.Dash(requests_pathname_prefix=requests_pathname_prefix)
    dash_app.title = 'Graph knowledge'

    graph = dcc.Graph(id='GDM',
                      figure=plot(G),
                      responsive=True,
                      style={'height': '100vh'})
    button = html.Button('Make api call', id='button')#, hidden=True)#, inIDs=[], outIds=[])
    input_inIds = dcc.Input(id='inIds')#, type='hidden')
    input_outIds = dcc.Input(id='outIds')#, type='hidden')
    input_metric = dcc.Input(id='metric')#, type='hidden')

    dash_app.layout = html.Div(
        children=[graph, button, input_inIds, input_outIds, input_metric],
        style={'height': '100vh'}
    )

    @dash_app.server.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response

    # @dash_app.clientside_callback(Output('GDM', 'figure'),
    #                             [Input("button", "n_clicks"),
    #                             # Input('inIds', 'value'),
    #                             # Input('outIds', 'value'),
    #                             # Input('metric', 'value'),
    #                             ],
    #                             prevent_initial_call=True
    #                             # state=[State('inIds', 'value'),
    #                             #        State('outIds', 'value'),
    #                             #        State('metric', 'value')]
    #                             )

    @dash_app.callback(Output('GDM', 'figure'),
                        Input("button", "n_clicks"),
                        State('inIds', 'value'),
                        State('outIds', 'value'),
                        State('metric', 'value'),
                       prevent_initial_call=True
                       )
    def update_data(nclicks, inIds, outIds, metric):
        """Retrieves data from api call

        Parameters
        ----------
        nclicks : int | None
            The number of times the button was pressed.
            Used to prevent initial update with empty state.

        """
        print(f'Entered callback, nclicks={nclicks}, inIds={inIds}')
        if nclicks in [0, None]:
            raise PreventUpdate
        else:
            inIds = inIds.split('%')
            outIds = outIds.split('%')
            metric = 'time_exp'
            data = plot(G, inIds[0], outIds[0], metric)
            return data

    return dash_app
