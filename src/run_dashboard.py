import dash_core_components as dcc
import dash_html_components as html
import json
import plotly.graph_objs as go
import urllib
from dashboard import oa_level
from dashboard import individual_level
from app import app
from utils import *
from dash.dependencies import Input, Output, State, ClientsideFunction
import settings
import os

# Set up app

settings.load()

# Get folders
ROOT_FOLDER = settings.get_root_dir()

# Get PostgreSQL database credentials
psql_credentials = settings.get_psql()
mapbox_access_token = settings.get_mapbox_token()

# Create SQLAlchemy engine from database credentials
engine = create_connection_from_dict(psql_credentials, 'postgresql')
print('Database connected')

app.layout = html.Div([
    html.H1('Public Transport Access Across the West Midlands'),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Output Area-Level Analysis', value='tab-1'),
        dcc.Tab(label='Individual-Level Analysis', value='tab-2'),
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return oa_level.return_layout(access_map_attr, population_map_attr, mapbox_access_token)
    elif tab == 'tab-2':
        return individual_level.return_layout(histogram_attr_ind, new_columns)


# Get data
mapbox_access_token = "pk.eyJ1IjoiamF0cmltYXIiLCJhIjoiY2p6ZmN2dnltMGFqbzNpbHQxcW82OHhvdyJ9.XWfWBetC6Et3MCClNzi7EQ"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

map_outlier_bound = 2.5


def get_oa_boundaries(path_to_geojson):
    with open(path_to_geojson) as f:
        return json.load(f)


def get_oa_level_data(engine):
    oa = get_oa_boundaries(
        os.path.join(ROOT_FOLDER, 'data/geo_simp.json'))  # TODO: this isn't really a query
    map = pd.read_sql_table('map_attributes', engine, schema='vis')
    pop = pd.read_sql_table('populations', engine, schema='results')
    poi = pd.read_sql_table('poi', engine, schema='semantic')
    return oa, map, pop, poi


def get_histogram_data(engine):
    histogram_attr_pop = pd.read_sql_table('histograms_oa_population', engine, schema='vis')
    histogram_attr_oa = pd.read_sql_table('histograms_oa_access', engine, schema='vis')
    histogram_attr_ind = pd.read_sql_table('histograms_individual_access', engine, schema='vis')
    return histogram_attr_pop, histogram_attr_oa, histogram_attr_ind


def get_scoreboard_data(engine):
    scoreboard = pd.read_sql_table('scoreboard', engine, schema='vis')
    return scoreboard


def set_metric(metric):
    # units = ''
    if metric in ['total_time', 'initial_wait_time']:
        units = 'Time in minutes'
    if metric in ['walk_dist']:
        units = 'Distance in meters'
    if metric in ['fare']:
        units = 'Cost in pounds'
    return units


oa_boundaries, access_map_attr, population_map_attr, poi_map_attr = get_oa_level_data(engine)
histogram_attr_pop, histogram_attr_oa, histogram_attr_ind = get_histogram_data(engine)


# Create layout for OA level analysis

def cutoff_counts_and_centers(bin_counts, bin_centers, outlier_cutoff):
    new_bin_counts = []
    new_bin_centers = []
    for i in range(len(bin_centers)):
        if bin_centers[i] <= outlier_cutoff:
            new_bin_counts.append(bin_counts[i])
            new_bin_centers.append(bin_centers[i])
    if len(new_bin_centers) > 1:
        return new_bin_counts, new_bin_centers
    else:
        return bin_counts, bin_centers


def get_scale_extremes(series, metric):
    if metric in ['fare', 'num_transfers']:
        zmin = series.min()
        zmax = series.max()
    else:
        zmin = 0
        zmax = float(series.mean() + (map_outlier_bound * series.std()))
    return zmin, zmax


def filter_histograms_access_dataframe(df, metric, strata, poi):
    dff = df[(df['metric'] == metric) & (
            (df['stratum'] == strata) & (df['poi_type'] == poi))]
    print(dff.outlier_cutoff.values[0])
    return cutoff_counts_and_centers(dff.bin_counts.values[0], dff.bin_centers.values[0], dff.outlier_cutoff.values[0])


def filter_histograms_population_dataframe(df, population):
    dff = df[df['population'] == population]
    print(dff.outlier_cutoff.values[0])
    return cutoff_counts_and_centers(dff.bin_counts.values[0], dff.bin_centers.values[0], dff.outlier_cutoff.values[0])


def filter_extreme_oa(df1, df2, access_slider, pop_slider):
    dff1 = df1[df1['value'] >= access_slider]
    dff2 = df2[df2['count'] >= pop_slider]
    return set(dff1['oa_id'].values.tolist()).intersection(set(dff2['oa_id'].values.tolist()))


# ACCESS_SLIDER
@app.callback(Output("access_slider", "max"), [
    Input("select-metric", "value"),
    Input("select-stratum", "value"),
    Input("select-poi", "value"),
])
def update_slider_max(metric, stratum, poi):
    counts, centers = filter_histograms_access_dataframe(histogram_attr_oa, metric, stratum, poi)
    # print("Slider max", max(centers))
    return max(centers)


# Slider -> count graph
@app.callback(Output("access_slider", "min"), [
    Input("select-metric", "value"),
    Input("select-stratum", "value"),
    Input("select-poi", "value"),
])
def update_slider_min(metric, stratum, poi):
    counts, centers = filter_histograms_access_dataframe(histogram_attr_oa, metric, stratum, poi)
    # print("Slider min", min(centers))
    return min(centers)


@app.callback(Output("access_slider", "value"), [
    Input("select-metric", "value"),
    Input("select-stratum", "value"),
    Input("select-poi", "value"),
])
def update_slider_value(metric, stratum, poi):
    counts, centers = filter_histograms_access_dataframe(histogram_attr_oa, metric, stratum, poi)
    # print(min(centers))
    return min(centers)


# POP_SLIDER
@app.callback(Output("population_slider", "max"), [
    Input("select-population", "value"),
])
def update_slider_max(pop):
    counts, centers = filter_histograms_population_dataframe(histogram_attr_pop, pop)
    # print(max(centers))
    return max(centers)


# Slider -> count graph
@app.callback(Output("population_slider", "min"), [
    Input("select-population", "value"),
])
def update_slider_min(pop):
    counts, centers = filter_histograms_population_dataframe(histogram_attr_pop, pop)
    # print(min(centers))
    return min(centers)


@app.callback(Output("population_slider", "value"), [
    Input("select-population", "value"),
])
def update_slider_value(pop):
    counts, centers = filter_histograms_population_dataframe(histogram_attr_pop, pop)
    # print(min(centers))
    return min(centers)


##### ACCESS MAP #####

@app.callback(
    Output("access-map", "figure"),
    [Input("select-poi", "value"),
     Input("select-metric", "value"),
     Input("select-stratum", "value"),
     Input("select-colorscale", "value")],
    [State("access-map", "figure")],
)
def create_access_map(poi_type, metric, stratum, colorscale, figure):
    """
    TODO : write docstring
    """
    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]  # TODO: This can probably be removed now
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = float(52.48)
        lon = float(-1.89)
        zoom = float(8.5)

    selected_data = access_map_attr.loc[(access_map_attr['poi_type'] == poi_type)
                                        & (access_map_attr['metric'] == metric)
                                        & (access_map_attr['stratum'] == stratum)]

    data = [go.Choroplethmapbox(geojson=oa_boundaries,
                                locations=selected_data['oa_id'],
                                z=selected_data['value'],
                                colorscale=colorscale,
                                reversescale=True,
                                zmin=get_scale_extremes(selected_data['value'], metric)[0],
                                zmax=get_scale_extremes(selected_data['value'], metric)[1],
                                marker_opacity=0.85,
                                marker_line_width=0,
                                colorbar=dict(title=dict(text=set_metric(metric),
                                                         side='right'),
                                              titlefont=dict(size=14),
                                              ),
                                ),
            ]

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),

        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        dragmode="lasso",
        uirevision="The User is always right",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
    )

    return go.Figure(data=data, layout=layout)


# ACCESS MAP DESCRIPTION

@app.callback(
    Output("access-map-description", "children"),
    [Input("select-poi", "value"),
     Input("select-metric", "value"),
     Input("select-stratum", "value")],
)
def populate_access_description(poi_type, metric, stratum):
    return dcc.Markdown(
        f'''
        This map shows the cost of travel to the nearest **{poi_type.lower()}** \
        in terms of **{metric.replace("_", " ")}** during **{stratum.lower()}**.
        ''')


# ACCESS MAP CSV DOWNLOAD

@app.callback(
    Output('download-access-map-link', 'href'),
    [Input("select-poi", "value"),
     Input("select-metric", "value"),
     Input("select-stratum", "value")],
)
def update_download_link(poi_type, metric, stratum):
    selected_data = access_map_attr.loc[(access_map_attr['poi_type'] == poi_type)
                                        & (access_map_attr['metric'] == metric)
                                        & (access_map_attr['stratum'] == stratum)]
    csv_string = selected_data.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


##### POPULATION MAP #####

@app.callback(
    Output("population-map", "figure"),
    [Input("select-population", "value"),
     Input("select-colorscale", "value")],
    [State("population-map", "figure")],
)
def create_population_map(pop_type, colorscale, figure):
    """
    TODO : write docstring
    """
    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = float(52.48)
        lon = float(-1.89)
        zoom = float(8.5)

    selected_data = population_map_attr.loc[(population_map_attr['population'] == pop_type)]

    zmax = float(selected_data['count'].mean() + (map_outlier_bound * selected_data['count'].std()))

    data = [
        go.Choroplethmapbox(geojson=oa_boundaries,
                            locations=selected_data['oa_id'],
                            z=selected_data['count'],
                            colorscale=colorscale,
                            reversescale=False,
                            zmin=0,
                            zmax=zmax,
                            marker_opacity=0.85,
                            marker_line_width=0,
                            colorbar=dict(title=dict(text='Population',
                                                     side='right'),
                                          titlefont=dict(size=14),
                                          ),
                            ),

    ]

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        dragmode="lasso",
        uirevision="The User is always right",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
    )

    return go.Figure(data=data, layout=layout)


# POPULATION MAP DESCRIPTION

@app.callback(
    Output("population-map-description", "children"),
    [Input("select-population", "value")],
)
def populate_population_description(population_type):
    units = "people"
    if population_type[-2:].lower() == 'hh':
        units = "households"
        population_type = population_type[:-2]
    elif population_type.lower() == 'total':
        population_type = "all"
    return dcc.Markdown(
        f'''
        This map shows the number of **{population_type.lower().replace("_", " ")} {units}** \
        living in each output area.
        ''')


# POPULATION MAP CSV DOWNLOAD

@app.callback(
    Output('download-population-map-link', 'href'),
    [Input("select-population", "value")],
)
def update_pop_download_link(population_type):
    selected_data = population_map_attr.loc[(population_map_attr['population'] == population_type)]
    csv_string = selected_data.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


# SLIDERS

# HISTOGRAMS OA LEVEL
@app.callback(
    Output("access_histogram", "figure"),
    [
        Input("select-poi", "value"),
        Input("select-metric", "value"),
        Input("select-stratum", "value"),
        # Input("population_slider", "value"),
        Input("access_slider", "value"),
    ],
)
def make_access_figure(poi_type, metric, stratum, access_slider):
    counts, center = filter_histograms_access_dataframe(histogram_attr_oa, metric, stratum, poi_type)
    colors = []
    for i in range(0, len(center)):
        if center[i] >= float(access_slider):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")

    data = [
        dict(
            type="bar",
            x=center,
            y=counts,
            name="All Wells",
            marker=dict(color=colors),
        ),
    ]

    layout = dict(
        autosize=True,
        automargin=False,
        showlegend=False,
        margin=dict(l=20, r=20, b=40, t=0),
        hovermode="closest",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        xaxis=dict(title=set_metric(metric)),
        yaxis=dict(title=f"Count of output areas",
                   ticks="",
                   showticklabels=False),
    )

    figure = dict(data=data, layout=layout)
    return figure


@app.callback(
    Output("population_histogram", "figure"),
    [
        Input("select-population", "value"),
        Input("population_slider", "value"),
    ],
)
def make_pop_figure(pop_type, population_slider):
    counts, center = filter_histograms_population_dataframe(histogram_attr_pop, pop_type)
    colors = []
    for i in range(0, len(center)):
        if center[i] >= float(population_slider):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")

    data = [
        dict(
            type="bar",
            x=center,
            y=counts,
            name="All Wells",
            marker=dict(color=colors),
        ),
    ]

    layout = dict(
        autosize=True,
        automargin=False,
        showlegend=False,
        margin=dict(l=20, r=20, b=40, t=0),
        hovermode="closest",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        xaxis=dict(title=f"Number of {pop_type}"),
        yaxis=dict(title=f"Count of output areas",
                   ticks="",
                   showticklabels=False),
    )

    figure = dict(data=data, layout=layout)
    return figure


##### AT RISK MAP #####

@app.callback(
    Output("at-risk-map", "figure"),
    [Input("select-poi", "value"),
     Input("select-metric", "value"),
     Input("select-stratum", "value"),
     Input("select-population", "value"),
     Input("button", "n_clicks")],
    [State("access_slider", "value"), State("population_slider", "value")],
)
def create_at_risk_map(poi_type, metric, stratum, pop_type, click, access_slider, population_slider):
    """
    TODO : write docstring
    """

    selected_access_data = access_map_attr.loc[(access_map_attr['poi_type'] == poi_type)
                                               & (access_map_attr['metric'] == metric)
                                               & (access_map_attr['stratum'] == stratum)]

    selected_pop_data = population_map_attr.loc[(population_map_attr['population'] == pop_type)]

    lat = float(52.48)
    lon = float(-1.89)
    zoom = float(8.5)

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        dragmode="lasso",
        uirevision="The User is always right",
    )

    at_risk_map_attr = access_map_attr.copy(deep=True)
    at_risk_oa_list = list(filter_extreme_oa(selected_access_data, selected_pop_data, access_slider, population_slider))
    at_risk_map_attr['value'] = at_risk_map_attr['oa_id'].isin(at_risk_oa_list).astype(int)

    data = [
        go.Choroplethmapbox(geojson=oa_boundaries,
                            locations=at_risk_map_attr['oa_id'],
                            z=at_risk_map_attr['value'],
                            colorscale='oranges',
                            reversescale=False,
                            zmin=False,
                            zmax=True,
                            marker_opacity=at_risk_map_attr['value'],
                            marker_line_width=0,
                            showscale=False)
    ]

    return go.Figure(data=data, layout=layout)


# AT RISK MAP DESCRIPTION

@app.callback(
    Output("at-risk-description-text", "children"),
    [Input("select-poi", "value"),
     Input("select-metric", "value"),
     Input("select-stratum", "value"),
     Input("select-population", "value"),
     Input("access_slider", "value"),
     Input("population_slider", "value")],
)
def populate_at_risk_map_description(poi_type, metric, stratum, population_type, access_slider, pop_slider):
    units = "people"
    if population_type[-2:].lower() == 'hh':
        units = "households"
        population_type = population_type[:-2]
    elif population_type.lower() == 'total':
        population_type = "all"
    return dcc.Markdown(
        f'''
        This map shows the output areas where the number of **{population_type.lower().replace("_", " ")} {units}** \
        is more than **{round(pop_slider)}**, AND it takes longer than **{round(access_slider)}** minutes to get to the nearest \
        **{poi_type}** during **{stratum}**.
        ''')


# AT-RISK MAP CSV DOWNLOAD

# TODO: We're getting a network error here; this is an important feature
# @app.callback(
#     Output('download-at-risk-map-link', 'href'),
#     [Input("select-poi", "value"),
#      Input("select-metric", "value"),
#      Input("select-stratum", "value"),
#      Input("select-population", "value")],
#     [State("access_slider", "value"),
#      State("population_slider", "value")],
# )
# def update_download_link(poi_type, metric, stratum, pop_type, access_slider, population_slider):
#     selected_access_data = access_map_attr.loc[(access_map_attr['poi_type'] == poi_type)
#                                                & (access_map_attr['metric'] == metric)
#                                                & (access_map_attr['stratum'] == stratum)]
#
#     # TODO: This code is repeated from above; need to find a more elegant approach
#     selected_pop_data = population_map_attr.loc[(population_map_attr['population'] == pop_type)]
#
#     at_risk_map_attr = access_map_attr.copy(deep=True)
#     at_risk_oa_list = list(filter_extreme_oa(selected_access_data, selected_pop_data, access_slider, population_slider))
#     at_risk_map_attr['value'] = at_risk_map_attr['oa_id'].isin(at_risk_oa_list).astype(int)
#
#     csv_string = at_risk_map_attr.to_csv(index=False, encoding='utf-8')
#     csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
#     return csv_string


# INDIVIDUAL LEVEL FUNCTIONS START HERE

def filter_individual_histograms(df, population, metric, strata, poi):
    dff = df[((df['population'] == population) & (df['metric'] == metric)) & (
            (df['stratum'] == strata) & (df['poi_type'] == poi))]
    return dff.bin_counts.values[0], dff.bin_centers.values[0]


# Individual level callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)


@app.callback(
    Output("well_text", "children"),
    [
        Input("slider", "value"),
        Input("population", "value"),
        Input("metric", "value"),
        Input("strata", "value"),
        Input("poi", "value"),
    ],
)
def update_hist_text(slider, population, metric, strata, poi):
    # dff = filter_dataframe(df2, population, metric, strata, poi)
    print(metric)
    counts, centers = filter_individual_histograms(histogram_attr_ind, population, metric, strata, poi)
    total = 0.0
    for i in range(0, len(centers)):
        if slider > centers[i]:
            total += counts[i]
    percent = (total / sum(counts)) * 100
    if metric == 'walk_dist':
        unit = 'meters'
    elif metric == 'fare':
        unit = 'pounds'
    elif metric == 'num_transfers':
        unit = 'transfers'
    else:
        unit = "minutes"
        slider = float(slider / 60.0)

    slider_formatted = float("{0:.2f}".format(slider))
    percent_formatted = float("{0:.2f}".format(percent))
    return f"{percent_formatted}% of the selected population can access {poi} in less than {slider_formatted} {unit}."


# Slider -> count graph
@app.callback(Output("slider", "max"), [
    Input("population", "value"),
    Input("metric", "value"),
    Input("strata", "value"),
    Input("poi", "value"),
])
def update_slider(population, metric, strata, poi):
    counts, centers = filter_individual_histograms(histogram_attr_ind, population, metric, strata, poi)
    return max(centers)


# Slider -> count graph
@app.callback(Output("slider", "min"), [
    Input("population", "value"),
    Input("metric", "value"),
    Input("strata", "value"),
    Input("poi", "value"),
])
def update_slider(population, metric, strata, poi):
    counts, centers = filter_individual_histograms(histogram_attr_ind, population, metric, strata, poi)
    return min(centers)


@app.callback(Output("slider", "value"), [
    Input("population", "value"),
    Input("metric", "value"),
    Input("strata", "value"),
    Input("poi", "value"),
])
def update_slider(population, metric, strata, poi):
    counts, centers = filter_individual_histograms(histogram_attr_ind, population, metric, strata, poi)
    return min(centers)


@app.callback(
    Output("count_graph", "figure"),
    [
        Input("population", "value"),
        Input("metric", "value"),
        Input("strata", "value"),
        Input("poi", "value"),
        Input("slider", "value"),
    ],
)
def make_count_figure(population, metric, strata, poi, slider):
    counts, center = filter_individual_histograms(histogram_attr_ind, population, metric, strata, poi)
    colors = []
    for i in range(0, len(center)):
        if center[i] >= float(slider):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")

    data = [
        dict(
            type="bar",
            x=center,
            y=counts,
            name="All Wells",
            marker=dict(color=colors),
        ),
    ]

    layout = dict(
        autosize=True,
        automargin=True,
        margin=dict(l=30, r=30, b=20, t=40),
        hovermode="closest",
        dragmode="select",
        showlegend=False,
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10), orientation="h"),
        title="",
    )

    figure = dict(data=data, layout=layout)
    return figure


# SCOREBOARD FUNCTIONS START HERE


# Get data
scoreboard = get_scoreboard_data(engine)
columns = scoreboard.columns

# Correct column names
new_columns = []
for column in columns:
    if column not in 'poi_type':
        column = column.replace("_", " ").title()
    new_columns.append(column)
scoreboard.columns = new_columns
new_columns.remove('poi_type')
new_columns.remove('Index')
print(new_columns)


@app.callback(
    Output('table-paging-and-sorting', 'data'),
    [Input('table-paging-and-sorting', "page_current"),
     Input('table-paging-and-sorting', "page_size"),
     Input('table-paging-and-sorting', 'sort_by'),
     Input("poi_scoreboard", "value")])
def update_table(page_current, page_size, sort_by, poi):
    scoreboard_filtered = scoreboard[(scoreboard['poi_type'] == poi)]
    scoreboard_filtered = scoreboard_filtered[['Population', 'Fare', 'Total Time', 'Walk Dist']]
    scoreboard_filtered['Walk Dist'] = scoreboard_filtered['Walk Dist'].map('{:,.2f}'.format)
    if len(sort_by):
        dff = scoreboard_filtered.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )
    else:
        # No sort is applied
        dff = scoreboard_filtered

    return dff.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records')


def run():
    app.run_server(host="0.0.0.0", debug=False)


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=False)
