import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from . import dash_utils

all_colorscales = ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
                   'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
                   'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
                   'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
                   'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
                   'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
                   'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
                   'orrd', 'oryel', 'peach', 'phase', 'picnic', 'pinkyl', 'piyg',
                   'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn', 'puor',
                   'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu', 'rdgy',
                   'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar', 'spectral',
                   'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn', 'tealrose',
                   'tempo', 'temps', 'thermal', 'tropic', 'turbid', 'twilight',
                   'viridis', 'ylgn', 'ylgnbu', 'ylorbr', 'ylorrd']


def return_layout(access_map_attr, population_map_attr, mapbox_access_token, colors=None):
    if colors is None:
        colors = all_colorscales
    return html.Div(
        id="root",
        children=[
            html.Div(
                id="header",
                children=[
                    html.H3(children=""),
                    html.P(
                        id="description",
                        children=("This tool is designed to help  analysis identify areas of the West Midlanands "
                                  "where investments in transit infrastructure could help improve the equity of the "
                                  "transit system. "),
                    ),
                ],
            ),
            html.Div(
                id="app-container",
                children=[
                    html.Div(
                        id="row-one",
                        children=[
                            html.Div(  # contains the controllers
                                id="row-one-controllers",
                                className="pretty_container two columns",
                                children=[
                                    html.H6(
                                        id="pop-dropdown-text",
                                        children="Select the population:",
                                    ),
                                    dcc.Dropdown(
                                        options=dash_utils.build_options('population', population_map_attr),
                                        value=dash_utils.build_options('population', population_map_attr)[0]['value'],
                                        id="select-population",
                                    ),
                                    html.A(
                                        'Download the data.',
                                        id='download-population-map-link',
                                        download="population-map-data.csv",
                                        href="",
                                        target="_blank"
                                    ),

                                ],
                            ),
                            html.Div(
                                id="population-map-and-title",
                                className="pretty_container six columns",
                                style={'vertical-align': 'bottom'},
                                children=[
                                    html.H4(
                                        "Heatmap of Selected Population",
                                        id="population-heatmap-title",
                                    ),
                                    html.P(id="population-map-description",
                                           children=""),
                                    dcc.Graph(
                                        id="population-map",
                                        figure=go.Figure(
                                            layout=go.Layout(
                                                mapbox=dict(
                                                    layers=[],
                                                    accesstoken=mapbox_access_token,
                                                    center=dict(lat=float(52.48),
                                                                lon=float(-1.89)),
                                                    zoom=float(8.5),
                                                ),
                                                autosize=True,
                                                hovermode="closest",
                                                margin=dict(r=0, l=0, t=0, b=0),
                                                dragmode="lasso",
                                            )
                                        ),
                                    ),
                                ],
                            ),  # end of the map

                            html.Div(
                                id="container2",
                                className="pretty_container four columns",
                                style={'vertical-align': 'bottom'},
                                children=[
                                    html.H4(
                                        "Histogram of Population",
                                        id="population-histogram-title",
                                    ),
                                    html.P(id="population-histogram-description",
                                           children="Use the slider to select a portion of the histogram's right tail."),
                                    dcc.Graph(id="population_histogram"),

                                    dcc.Slider(
                                        id="population_slider",
                                        min=0,
                                        max=600,
                                        value=100,
                                        className="dcc_control",
                                    ),
                                ],

                            ),
                        ],
                        className="row flex-display",
                    ),  # end of row one
                    html.Hr(),
                    html.Div(
                        id="row-two",
                        children=[
                            html.Div(  # contains the controllers
                                id="row-two-controllers",
                                className="pretty_container two columns",
                                children=[
                                    html.H6(
                                        id="poi-dropdown-text",
                                        children="Select the POI type:",
                                    ),
                                    dcc.Dropdown(
                                        options=dash_utils.build_options('poi_type', access_map_attr),
                                        value=dash_utils.build_options('poi_type', access_map_attr)[0]['value'],
                                        id="select-poi",
                                    ),
                                    html.H6(
                                        id="metric-dropdown-text",
                                        children="Select the metric:",
                                    ),
                                    dcc.Dropdown(
                                        options=dash_utils.build_options('metric', access_map_attr),
                                        value='total_time',
                                        id="select-metric",
                                    ),
                                    html.H6(
                                        id="stratum-dropdown-text",
                                        children="Select the part of week:",
                                    ),
                                    dcc.Dropdown(
                                        options=dash_utils.build_options('stratum', access_map_attr),
                                        value=dash_utils.build_options('stratum', access_map_attr)[0]['value'],
                                        id="select-stratum",
                                    ),
                                    html.A(
                                        'Download the data.',
                                        id='download-access-map-link',
                                        download="access-map-data.csv",
                                        href="",
                                        target="_blank"
                                    ),
                                ],
                            ),
                            html.Div(
                                id="access-map-and-title",
                                style={'vertical-align': 'bottom'},
                                className="pretty_container six columns",
                                children=[
                                    html.H4(
                                        "Heatmap of Transit Access",
                                        id="access-heatmap-title",
                                    ),
                                    html.P(id="access-map-description",
                                           children=""),
                                    dcc.Graph(
                                        id="access-map",
                                        figure=go.Figure(
                                            layout=go.Layout(
                                                mapbox=dict(
                                                    layers=[],
                                                    accesstoken=mapbox_access_token,
                                                    center=dict(lat=float(52.48),
                                                                lon=float(-1.89)),
                                                    zoom=float(8.5),
                                                ),
                                                autosize=True,
                                                hovermode="closest",
                                                margin=dict(r=0, l=0, t=0, b=5),
                                                dragmode="lasso",
                                            )
                                        ),
                                    ),
                                ],
                            ),  # end of the map
                            html.Div(
                                id="access-hist-and-title",
                                style={'vertical-align': 'bottom'},
                                className="pretty_container four columns",
                                children=[
                                    html.H4(
                                        "Histogram of Transit Access",
                                        id="access-histogram-title",
                                    ),
                                    html.P(id="access-histogram-description",
                                           children="Use the slider to select a portion of the histogram's right tail."),
                                    dcc.Graph(id="access_histogram"),

                                    dcc.Slider(
                                        id="access_slider",
                                        min=20,
                                        max=1000,
                                        value=100,
                                        className="dcc_control",

                                    ),
                                ],
                            ),
                        ],
                        className="row flex-display",
                    ),  # end of row two
                    html.Hr(),

                    html.Div(
                        id="row-three",
                        children=[
                            html.Div(  # contains the controllers
                                id="row-three-controllers",
                                className="pretty_container two columns",
                                children=[
                                    html.H6(
                                        id="at-risk-dropdown-text",
                                        children="Compute at-risk neighborhoods.",
                                    ),
                                    html.Button('Refresh', id='button'),
                                    # html.A(
                                    #     'Download the data.',
                                    #     id='download-at-risk-map-link',
                                    #     download="at-risk-map-data.csv",
                                    #     href="",
                                    #     target="_blank"
                                    # ),
                                ],
                            ),
                            html.Div(
                                id="at-risk-map-and-title",
                                className="pretty_container six columns",
                                children=[
                                    html.H4(
                                        "Map of At-Risk Neighborhoods",
                                        id="at-risk-map-title",
                                    ),
                                    html.P(
                                        id="at-risk-description-text",
                                        children="",
                                    ),
                                    dcc.Graph(
                                        id="at-risk-map",
                                        figure=go.Figure(
                                            layout=go.Layout(
                                                mapbox=dict(
                                                    layers=[],
                                                    accesstoken=mapbox_access_token,
                                                    center=dict(lat=float(52.48),
                                                                lon=float(-1.89)),
                                                    zoom=float(8.5),
                                                ),
                                                autosize=True,
                                                hovermode="closest",
                                                margin=dict(r=0, l=0, t=0, b=0),
                                                dragmode="lasso",
                                            )
                                        ),
                                    ),
                                ],
                            ),
                        ],
                        className="row flex-display",
                    ),
                    html.Div(
                        html.Div(
                            id="colorscale-selector",
                            className="pretty_container eight columns",
                            children=[
                                html.P(
                                    id="color-selector-text",
                                    children="Select a colorscale:",

                                ),
                                dcc.Dropdown(
                                    options=dash_utils.build_options_from_list(all_colorscales),
                                    value='cividis',
                                    id="select-colorscale",
                                ),
                            ]
                        ),
                        className="row flex-display",
                    ),
                    html.Hr(),
                    html.Div(
                        id="attribution",
                        className="pretty_container eight columns",
                        children=[
                            html.Small(
                                id="attribution-text",
                                children=("Created by Ece Calikus, James Trimarco, Tammy Tseng, Renzhe Yu for Data "
                                          "Science for Social Good at The Alan Turing institute and University of "
                                          "Warwick, in partnership with the DSSG Foundation."),
                                style={'align-items': 'left',
                                       'width': '200px'},
                            ),
                        ]
                    ),
                ],  # end of all rows
                # className="row flex-display",
            ),
        ],
    )
