import dash_core_components as dcc
import dash_html_components as html
from . import dash_utils
import dash_table

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
)


def return_layout(histogram_attributes, score_board_columns):
    return html.Div(
        [
            dcc.Store(id="aggregate_data"),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div(
                [

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3(
                                        "Individual Level Access Across West Midlands",
                                        style={"margin-bottom": "0px"},
                                    ),
                                ]
                            )
                        ],
                        className="one-half column",
                        id="title",
                    ),
                ],
                id="header",
                className="row flex-display",
                style={"margin-bottom": "25px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P(
                                "Select threshold (or select range in histogram):",
                                className="control_label",
                            ),
                            dcc.Slider(
                                id="slider",
                                min=0,
                                max=100,
                                value=0,
                                className="dcc_control",
                            ),
                            html.P("Filter by demographic group:", className="control_label"),
                            dcc.Dropdown(
                                id="population",
                                options=dash_utils.build_options('population', histogram_attributes),
                                value=dash_utils.build_options('population', histogram_attributes)[0]['value'],
                                className="dcc_control",
                            ),
                            html.P("Filter by metric:", className="control_label"),
                            dcc.Dropdown(
                                id="metric",
                                options=dash_utils.build_options('metric', histogram_attributes),
                                value=dash_utils.build_options('metric', histogram_attributes)[3]['value'],
                                className="dcc_control",
                            ),
                            html.P("Filter by strata:", className="control_label"),
                            dcc.Dropdown(
                                id="strata",
                                options=dash_utils.build_options('stratum', histogram_attributes),
                                value=dash_utils.build_options('stratum', histogram_attributes)[0]['value'],
                                className="dcc_control",
                            ),
                            html.P("Filter by point of interest:", className="control_label"),
                            dcc.Dropdown(
                                id="poi",
                                options=dash_utils.build_options('poi_type', histogram_attributes),
                                value=dash_utils.build_options('poi_type', histogram_attributes)[0]['value'],
                                className="dcc_control",
                            ),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [html.H6(id="well_text"), html.P("")],
                                        id="wells",
                                        className="mini_container",
                                    ),
                                ],
                                id="info-container",
                                className="row container-display",
                            ),
                            html.Div(
                                [dcc.Graph(id="count_graph")],
                                id="countGraphContainer",
                                className="pretty_container",
                            ),
                        ],
                        id="right-column",
                        className="eight columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Hr(),
            html.Div(
                [
                    html.Div(
                        [
                            html.P("Filter by point of interest:", className="control_label"),
                            dcc.Dropdown(
                                id="poi_scoreboard",
                                options=dash_utils.build_options('poi_type', histogram_attributes),
                                value=dash_utils.build_options('poi_type', histogram_attributes)[0]['value'],
                                className="dcc_control",
                            ),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),
                    html.Div(
                        [

                            html.Div(
                                [dash_table.DataTable(
                                    id='table-paging-and-sorting',
                                    columns=[
                                        {'name': i, 'id': i, 'deletable': True} for i in score_board_columns
                                    ],
                                    page_current=0,
                                    page_size=10,
                                    page_action='custom',
                                    sort_action='custom',
                                    sort_mode='single',
                                    sort_by=[]
                                )],
                                id="countGraphContainer",
                                className="pretty_container",
                            ),
                        ],
                        id="right-column",
                        className="eight columns",
                    ),
                ],
                className="row flex-display",
            ),
        ]
    )

# layout = html.Div([
#     html.H1('Page 2'),
#     dcc.RadioItems(
#         id='page-2-radios',
#         options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
#         value='Orange'
#     ),
#     html.Div(id='page-2-content')
# ])
