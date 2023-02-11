# Hi! This app was modified from another app
# Source: https://github.com/plotly/dash-world-cell-towers
# This app utilizes a similar layout to this app, with different plots / data
# I used this app to figure out how to add buttons that refresh figures
# To see the original app in production, visit: https://dash.gallery/dash-world-cell-towers/
# Originally, I used this app to host a visualization I made for a summer internship
# I repurposed this application for the Frontera Hacks inaugural hackathon
# Specifically for the Frontera Hacks A Dashboard workshop
# I've found this project to be a valuable showcase of my ability for future teams
# I hope you can gain some inspiration for it with your project / data / interests! <3

# Import libraries
import dash as dash
from dash import dcc
from dash import html
from dash import ctx
from textwrap import dedent
import plotly.graph_objects as go
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd
import plotly.express as px

# Figure Templates
bgcolor = "#f3f3f1"  # mapbox light map land color
row_heights = [150, 500, 300]
template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

# Required line to run the app
app = dash.Dash(__name__)

# this is a template modal that makes the info help text work
# edit at your own risk!
def build_modal_info_overlay(id, side, content):
    """
    Build div representing the info overlay for a plot panel
    """
    div = html.Div(
        [  # modal div
            html.Div(
                [  # content div
                    html.Div(
                        [
                            html.H4(
                                [
                                    "About this plot",
                                    html.Img(
                                        id=f"close-{id}-modal",
                                        src="assets/times-circle-solid.svg",
                                        n_clicks=0,
                                        className="info-icon",
                                        style={"margin": 0},
                                    ),
                                ],
                                className="container_title",
                                style={"color": "white"},
                            ),
                            dcc.Markdown(content),
                        ]
                    )
                ],
                className=f"modal-content {side}",
            ),
            html.Div(className="modal"),
        ],
        id=f"{id}-modal",
        style={"display": "none"},
    )

    return div


# import all data for figures below
# this is from the starting dataset
musicdf = pd.read_csv("assets/mxmh_survey_results.csv")
# this is from the datasets that'll be added later
whddf = pd.read_csv("assets/WHD.csv")
whd15df = whddf.set_index('Country').query("Year==2015")
whd15df = whd15df.drop(columns=['Year'])
whd15df["Happiness Ratio"] = 1/whd15df["Happiness Rank"]
whd19df = whddf.set_index('Country').query("Year==2019")
whd19df = whd19df.drop(columns=['Year'])
whd19df["Happiness Ratio"] = 1/whd19df["Happiness Rank"]

# add all constants and code associated with data churning below
musicdf = musicdf.drop(columns=['Timestamp', 'Permissions'])
# you can decide how to handle missing data per column
# for example, with age you might want to impute a value based on the mean
musicdf["Age"] = musicdf["Age"].fillna(value=round(musicdf.Age.mean()))
# for something like music effects, you might want to assume no effect since it was not reported
musicdf["Music effects"] = musicdf["Music effects"].fillna(value="No effect")
musicdf["While working"] = musicdf["While working"].fillna(value="No")
musicdf["Instrumentalist"] = musicdf["Instrumentalist"].fillna(value="No")
musicdf["Composer"] = musicdf["Composer"].fillna(value="No")
musicdf["Primary streaming service"] = musicdf["Primary streaming service"].fillna(value="I do not use a streaming service.")
# feel free to impute missing values however you wish for your data
# you can also make new values
musicdf["Mental health severity"] = musicdf["Anxiety"] + musicdf["Depression"] + musicdf["Insomnia"] + musicdf["OCD"]
# data churning is done!!!

# time to create figures

# by default, we will initialize the music / mental health data set
# if you want to change the figures that load on start-up, edit these figures below
# Please be *very* careful with changing the names of these figures, as they are referenced multiple times in the code
# if you change any of the IDs above, you need to change where they are referenced below
# change figure names at your own risk
mainFig = go.Figure()
mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['Depression'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='Depression/10', scalegroup='Depression/10', name='Depression/10',
                                line_color='hotpink', box_visible=True)
                      )
mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['Anxiety'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='Anxiety/10', scalegroup='Anxiety/10', name='Anxiety/10',
                                line_color='green', box_visible=True)
                      )
mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['OCD'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='OCD/10', scalegroup='OCD/10', name='OCD/10',
                                line_color='blue', box_visible=True)
                      )
mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['Insomnia'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='Insomnia/10', scalegroup='Insomnia/10', name='Insomnia/10',
                                line_color='purple', box_visible=True)
                      )
mainFig.update_traces(meanline_visible=True)
mainFig.update_layout(violingap=0, violinmode='group')
mainFig.update_layout(yaxis_title="Self-Ranked Score Out of 10",
                          xaxis_title="Music Tends to ______ My Mental Health")

histoFig = px.histogram(musicdf, x="Fav genre", histfunc='count', color="Music effects",
                            color_discrete_sequence=px.colors.qualitative.Prism)
histoFig.update_layout(yaxis_title="Number of People")

denseFig = px.density_heatmap(musicdf, x="Depression", y="Anxiety", nbinsx=10, nbinsy=10, facet_row="Composer",
                                  facet_col="Instrumentalist")

scatterFig = px.scatter_ternary(musicdf, a="OCD", b="Anxiety", c="Insomnia", color="Exploratory",
                                    size="Mental health severity", size_max=20,
                                    color_discrete_sequence=px.colors.qualitative.Prism)

pieFig = px.sunburst(musicdf, path=['Primary streaming service', 'Exploratory'], values='Hours per day',
                         color='Primary streaming service', color_discrete_sequence=px.colors.sequential.Plasma)

# this is what makes the web server look pretty
app.layout = html.Div(
    children=[
        html.Div(
            [ # title section with your logo can go here
                html.H1(
                    children=[
                        "Frontera Hacks A Dashboard",
                        html.A(
                            html.Img(
                                src="assets/Kristen-Hallas.png",
                                style={"float": "right", "height": "75px"},
                            ),
                            href="https://www.kristenhallas.com",
                        ),
                    ],
                    style={"text-align": "left", "color": "#ffffff"},
                ),
            ]
        ),
html.Div(
            children=[ # this contains the intro text and the toggle buttons
            html.H4("Application overview", style={"margin-top": "0"}),
            dcc.Markdown(
                        """
                Welcome to all those participating in Frontera Hacks, or any other visitors who may have stumbled here! 
                If you are seeing this on some IP address, then congratulations for successfully launching 
                this Plotly Dash app! 
                
                This app is ideal for someone who has a data set they want to explore and share with the world. I love 
                Plotly Dash because it is interactive, it looks nice, you can customize so much, and the best part is 
                if you need to do anything special, or even machine learning, the fact that this is all written 
                in Python makes it possible. Thus, I designed this app with two goals in mind: 1) minimize the time 
                it takes to launch something with a bunch of features that looks nice and 2) maximize the time 
                you can spend processing and showcasing data that is interesting to you. 
                
                Some notable features include
                * this layout, which is compatible with Markdown
                * baked-in help modals (click the ? icon!)
                * callback function buttons that swap out datasets (but can do so much more - 
                [definitely worth the research](https://dash.plotly.com/basic-callbacks)) 
                * samples of some of the coolest Plotly plots available to you
                
                Click the buttons to load sample data sets, explore the interactivity of the Plotly plots, and enjoy 
                customizing this dashboard! 
                """
                ),
                html.Div(
                            children=[
                                        html.Button(
                                            "Music And Mental Health",
                                            id="mxmh",
                                            className="button",
                                            style={"padding-left": "10px", "padding-right": "10px",
                                                   "margin-left": "10px", "margin-right": "10px"}
                                        ),
                                        html.Button(
                                            "World Happiness Data 2015",
                                            id="whd15",
                                            className="button",
                                            style={"padding-left": "10px", "padding-right": "10px",
                                                   "margin-left": "10px", "margin-right": "10px"}
                                        ),
                                        html.Button(
                                            "World Happiness Data 2019",
                                            id="whd19",
                                            className="button",
                                            style={"padding-left": "10px", "padding-right": "10px",
                                                   "margin-left": "10px", "margin-right": "10px"}
                                        ),
                                        html.Button(
                                            "World Happiness Data 15-19",
                                            id="whd",
                                            className="button",
                                            style={"padding-left": "10px", "padding-right": "10px",
                                                   "margin-left": "10px", "margin-right": "10px"}
                                        )
                            ],
                        ),
                ],
            style={
                "width": "98%",
                "margin-right": "0",
                "padding": "10px",
            },
            className="twelve columns pretty_container",
        ),
        html.Div(
            children=[ # this does the help text for each of the help modals
                build_modal_info_overlay(
                    "histo",
                    "bottom",
                    dedent(
                        """
            The _**Histogram example**_ panel displays an example of the Histogram plot. You can edit this panel to
            contain information that is relevant to the plot you created. 
            
            [You can learn more about Histograms at this link](https://plotly.com/python/histograms/).
            """
                    ),
                ),
                build_modal_info_overlay(
                    "dense",
                    "bottom",
                    dedent(
                        """
            The _**Density map example **_ panel displays an example of the Density map plot. You can edit this panel to
            contain information that is relevant to the plot you created. 
            
            [You can learn more about Density Map plots at this link](https://plotly.com/python/2D-Histogram/).
            """
                    ),
                ),
                build_modal_info_overlay(
                    "main",
                    "bottom",
                    dedent(
                        """
            The _**Main plot example **_ panel displays an example of a larger plot within the scheme of the app. 
            You can edit this panel to contain information that is relevant to the plot you created. 
            
            [Plotly has all sorts of examples for plots, you can see all of them here.](https://plotly.com/python/plotly-express/).
            """
                    ),
                ),
                build_modal_info_overlay(
                    "pie",
                    "top",
                    dedent(
                        """
            The _**Pie example **_ panel displays an example of a Pie plot. You can edit this panel to
            contain information that is relevant to the plot you created. 
            
            [You can learn more about Pie plots at this link](https://plotly.com/python/sunburst-charts/).
        """
                    ),
                ),
                build_modal_info_overlay(
                    "scatter",
                    "top",
                    dedent(
                        """
            The _**Scatter example **_ panel displays an example of a Scatter plot. You can edit this panel to
            contain information that is relevant to the plot you created. 
            
            [You can learn more about Scatter plots at this link](https://plotly.com/python/line-and-scatter/).
        """
                    ),
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[ # contains the top row charts
                                html.H4(
                                    [
                                        "Histogram Example", # top left chart
                                        html.Img(
                                            id="show-histo-modal",
                                            src="assets/question-circle-solid.svg",
                                            n_clicks=0,
                                            className="info-icon",
                                        ),
                                    ],
                                    className="container_title",
                                ),
                                dcc.Loading(
                                    dcc.Graph(
                                        id="histo-graph",
                                        figure=histoFig,
                                        config={"displayModeBar": False},
                                    ),
                                    className="svg-container",
                                    style={"height": 150},
                                ),
                            ],
                            className="six columns pretty_container",
                            id="histo-div",
                        ),
                        html.Div(
                            children=[
                                html.H4(
                                    [
                                        "Density Map Example", #top right chart
                                        html.Img(
                                            id="show-dense-modal",
                                            src="assets/question-circle-solid.svg",
                                            className="info-icon",
                                        ),
                                    ],
                                    className="container_title",
                                ),
                                dcc.Graph(
                                    id="dense-graph",
                                    figure=denseFig,
                                    config={"displayModeBar": False},
                                ),
                            ],
                            className="six columns pretty_container",
                            id="dense-div",
                        ),
                    ]
                ),
                html.Div(
                    children=[ # this contains the main chart
                        html.H4(
                            [
                                "Main Plot Example",
                                html.Img(
                                    id="show-main-modal",
                                    src="assets/question-circle-solid.svg",
                                    className="info-icon",
                                ),
                            ],
                            className="container_title",
                        ),
                        dcc.Graph(
                            id="main-graph",
                            figure=mainFig,
                        ),
                    ],
                    className="twelve columns pretty_container",
                    style={
                        "width": "98%",
                        "margin-right": "0",
                    },
                    id="main-div",
                ),
                html.Div(
                    children=[
                        html.Div(
                            children=[ # this contains the bottom row charts
                                html.H4(
                                    [
                                        "Pie Example", # left plot
                                        html.Img(
                                            id="show-pie-modal",
                                            src="assets/question-circle-solid.svg",
                                            className="info-icon",
                                        ),
                                    ],
                                    className="container_title",
                                ),
                                dcc.Graph(
                                    id="pie-graph",
                                    figure=pieFig,
                                    config={"displayModeBar": False},
                                ),
                            ],
                            className="six columns pretty_container",
                            id="pie-div",
                        ),
                        html.Div(
                            children=[
                                html.H4(
                                    [
                                        "Scatter Example", # right plot
                                        html.Img(
                                            id="show-scatter-modal",
                                            src="assets/question-circle-solid.svg",
                                            className="info-icon",
                                        ),
                                    ],
                                    className="container_title",
                                ),
                                dcc.Graph(
                                    id="scatter-graph",
                                    config={"displayModeBar": False},
                                    figure=scatterFig,
                                ),
                            ],
                            className="six columns pretty_container",
                            id="scatter-div",
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
            children=[ # the acknowledgments section

                html.H4("Acknowledgements", style={"margin-top": "0"}),
                dcc.Markdown(
                    """\
This template was repurposed with love by Kristen Hallas, for the purpose of the inaugural 
[Frontera Hacks](https://fronterahacks.com/) Hackathon. Frontera Hacks A Dashboard would not be possible
 without the following sources. 
 - Dashboard written in Python using the [Plotly](https://plotly.com) [Dash](https://dash.plot.ly/) web framework.
 - This dashboard was sourced heavily from [World Cell Towers](https://dash.gallery/dash-world-cell-towers/) found 
 [here](https://dash.gallery/Portal/). 
 - For huge data, parallel and distributed calculations can be implemented using the [Dask](https://dask.org/) 
 Python library.
 - Icons provided by [Font Awesome](https://fontawesome.com/) and used under the
[_Font Awesome Free License_](https://fontawesome.com/license/free). 
 - Primary dataset is from Catherine Rasgaitis on Kaggle, 
 [Music & Mental Health Survey Results](https://www.kaggle.com/datasets/catherinerasgaitis/mxmh-survey-results).
 - Secondary dataset was collated/cleaned by Kristen Hallas, sourced from the 
 [World Happiness Report](https://www.kaggle.com/datasets/unsdsn/world-happiness) on Kaggle.
 - Last and certainly not least, Oak Ridge National Lab (ORNL) deserves a big thank you - 
 in Summer 2022, through the U.S. Department of Energy's Omni Technology Alliance Internship Program, 
 I was appointed to work on real-world challenges related to cybersecurity and information technology. 
 To this end, I developed a 
 [novel, dynamically colored map](https://www.kristenhallas.com/projects/visualizing-supercomputers-ornl) 
 using a similar interactive visualization framework.
"""
                ),
            ],
            style={
                "width": "98%",
                "margin-right": "0",
                "padding": "10px",
            },
            className="twelve columns pretty_container",
        ),
    ],
)

# callbacks
# this is what makes the app interactive

# first function create show/hide callbacks for each info modal
# if you change any of the IDs above, you need to change them here
# change at your own risk
for id in ["histo", "dense", "main", "pie", "scatter"]:

    @app.callback(
        [Output(f"{id}-modal", "style"), Output(f"{id}-div", "style")],
        [Input(f"show-{id}-modal", "n_clicks"), Input(f"close-{id}-modal", "n_clicks")],
    )
    def toggle_modal(n_show, n_close):
        ctx = dash.callback_context
        if ctx.triggered and ctx.triggered[0]["prop_id"].startswith("show-"):
            return {"display": "block"}, {"zIndex": 1003}
        else:
            return {"display": "none"}, {"zIndex": 0}

# create callback to show each graph. you can't do multiple callbacks that use the same output/input ID
# so that's why we do it in a big function like this
# if you need help understanding each of the graph plots I comment about them up at their initialization
@app.callback([
    Output("histo-graph", "figure"),
    Output("dense-graph", "figure"),
    Output("main-graph", "figure"),
    Output("pie-graph", "figure"),
    Output("scatter-graph", "figure")],
    [Input("mxmh", "n_clicks"),
     Input("whd15", "n_clicks"),
     Input("whd19", "n_clicks"),
     Input("whd", "n_clicks")], prevent_initial_call=True)

# you need the number of input in update_graphs to match the number of buttons you have updating graphs
def update_graphs(b1, b2, b3, b4):
    triggered_id = ctx.triggered[0]['prop_id']
    if 'mxmh.n_clicks' == triggered_id:
        return update_mxmh()
    elif 'whd15.n_clicks' == triggered_id:
        return update_whd15()
    elif 'whd19.n_clicks' == triggered_id:
        return update_whd19()
    else:
        return update_whd()

# the output should be returning the figures you wanted to update
def update_mxmh():
    mainFig = go.Figure()
    mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['Depression'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='Depression/10', scalegroup='Depression/10', name='Depression/10',
                                line_color='hotpink', box_visible=True)
                      )
    mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['Anxiety'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='Anxiety/10', scalegroup='Anxiety/10', name='Anxiety/10',
                                line_color='green', box_visible=True)
                      )
    mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['OCD'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='OCD/10', scalegroup='OCD/10', name='OCD/10',
                                line_color='blue', box_visible=True)
                      )
    mainFig.add_trace(go.Violin(x=musicdf['Music effects'][musicdf['Music effects'] != 'No effect'],
                                y=musicdf['Insomnia'][musicdf['Music effects'] != 'No effect'],
                                legendgroup='Insomnia/10', scalegroup='Insomnia/10', name='Insomnia/10',
                                line_color='purple', box_visible=True)
                      )
    mainFig.update_traces(meanline_visible=True)
    mainFig.update_layout(violingap=0, violinmode='group')
    mainFig.update_layout(yaxis_title="Self-Ranked Score Out of 10",
                          xaxis_title="Music Tends to ______ My Mental Health")

    histoFig = px.histogram(musicdf, x="Fav genre", histfunc='count', color="Music effects",
                            color_discrete_sequence=px.colors.qualitative.Prism)
    histoFig.update_layout(yaxis_title="Number of People")

    denseFig = px.density_heatmap(musicdf, x="Depression", y="Anxiety", nbinsx=10, nbinsy=10, facet_row="Composer",
                                  facet_col="Instrumentalist")

    scatterFig = px.scatter_ternary(musicdf, a="OCD", b="Anxiety", c="Insomnia", color="Exploratory",
                                    size="Mental health severity", size_max=20,
                                    color_discrete_sequence=px.colors.qualitative.Prism)

    pieFig = px.sunburst(musicdf, path=['Primary streaming service', 'Exploratory'], values='Hours per day',
                         color='Primary streaming service', color_discrete_sequence=px.colors.sequential.Plasma)
    return histoFig, denseFig, mainFig, pieFig, scatterFig


def update_whd15():
    histoFig = px.histogram(whd15df, x="Happiness Score", y='Health (Life Expectancy)', histfunc='avg',
                   color="Region", color_discrete_sequence=px.colors.sequential.Plasma)

    tempdf = whd15df.where(whd15df["Happiness Score"] > 5)
    scatterFig = px.scatter_3d(tempdf,
                               x="Economy (GDP per Capita)", y="Trust (Government Corruption)", z="Freedom",
                               color='Region', hover_name=whd15df.index,
                               hover_data=['Economy (GDP per Capita)', 'Family',
                                           'Health (Life Expectancy)', 'Freedom',
                                           'Trust (Government Corruption)',
                                           'Generosity'], color_discrete_sequence=px.colors.sequential.Plasma)

    # draw the floor plan fig
    mainFig = px.choropleth(whd15df, locations="iso_alpha",
                    color="Happiness Score", fitbounds='locations',
                    hover_name=whd15df.index, hover_data=['Economy (GDP per Capita)', 'Family',
                                                      'Health (Life Expectancy)', 'Freedom',
                                                      'Trust (Government Corruption)', 'Generosity'],
                    color_continuous_scale=px.colors.sequential.RdBu)
    mainFig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                          legend=dict(orientation='h', y=-0.1, yanchor='bottom', x=0.5, xanchor='center'))

    # draw the figure that counts instances of a component being the max consumer
    denseFig = px.treemap(whd15df, path=[px.Constant("world"), 'Region', whd15df.index], values='Happiness Ratio',
                  color='Happiness Score', hover_data=['Happiness Ratio'], color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(whd15df['Happiness Score'], weights=whd15df['Happiness Ratio'])
                )
    denseFig.update_layout(margin = dict(t=50, l=25, r=25, b=25))

    # draw the figure that counts instances of a component being the hottest
    pieFig = px.sunburst(whd15df, path=['Region', whd15df.index], values='Happiness Ratio',
                  color='Happiness Score', hover_data=['Happiness Ratio'], color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(whd15df['Happiness Score'], weights=whd15df['Happiness Ratio']))
    return histoFig, denseFig, mainFig, pieFig, scatterFig


def update_whd19():
    mainFig = px.choropleth(whd19df, locations="iso_alpha",
                    color="Happiness Score", fitbounds='locations',
                    hover_name=whd19df.index, hover_data=['Economy (GDP per Capita)', 'Family',
                                                      'Health (Life Expectancy)', 'Freedom',
                                                      'Trust (Government Corruption)', 'Generosity'],
                    color_continuous_scale=px.colors.sequential.RdBu)
    mainFig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                          legend=dict(orientation='h', y=-0.1, yanchor='bottom', x=0.5, xanchor='center'))

    histoFig = px.histogram(whd19df, x="Happiness Score", y='Health (Life Expectancy)', histfunc='avg',
                   color="Region", color_discrete_sequence=px.colors.sequential.Plasma)

    tempdf = whd19df.where(whd19df["Happiness Score"] > 5)
    scatterFig = px.scatter_3d(tempdf,
                        x="Economy (GDP per Capita)", y="Trust (Government Corruption)", z="Freedom",
                        color='Region', hover_name=whd19df.index, hover_data=['Economy (GDP per Capita)', 'Family',
                                                                              'Health (Life Expectancy)', 'Freedom',
                                                                              'Trust (Government Corruption)',
                                                                              'Generosity'],
                               color_discrete_sequence=px.colors.sequential.Plasma)

    denseFig = px.treemap(whd19df, path=[px.Constant("world"), 'Region', whd19df.index], values='Happiness Ratio',
                  color='Happiness Score', hover_data=['Happiness Ratio'], color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(whd19df['Happiness Score'], weights=whd19df['Happiness Ratio'])
                )
    denseFig.update_layout(margin = dict(t=50, l=25, r=25, b=25))

    pieFig = px.sunburst(whd19df, path=['Region', whd19df.index], values='Happiness Ratio',
                  color='Happiness Score', hover_data=['Happiness Ratio'], color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(whd19df['Happiness Score'], weights=whd19df['Happiness Ratio']))
    return histoFig, denseFig, mainFig, pieFig, scatterFig


def update_whd():
    mainFig = px.choropleth(whddf, locations="iso_alpha",
                    color="Happiness Score", fitbounds='locations',
                    hover_name="Country", hover_data=['Economy (GDP per Capita)', 'Family',
                                                      'Health (Life Expectancy)', 'Freedom',
                                                      'Trust (Government Corruption)', 'Generosity'],
                    color_continuous_scale=px.colors.sequential.RdBu, animation_frame="Year")
    mainFig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                          legend=dict(orientation='h', y=-0.1, yanchor='bottom', x=0.5, xanchor='center'))

    histoFig = px.histogram(whddf, x="Happiness Score", histfunc='count', color="Region",
                   color_discrete_sequence=px.colors.sequential.Plasma,
                   animation_frame="Year")
    histoFig.update_layout(yaxis_title="Number of Countries")

    scatterFig = px.scatter_ternary(whddf, a="Generosity", b="Trust (Government Corruption)", c="Freedom",
                         hover_name="Country", color="Region", size="Happiness Score", size_max=15,
                         hover_data=['Happiness Score', 'Economy (GDP per Capita)', 'Family',
                                                      'Health (Life Expectancy)', 'Freedom',
                                                      'Trust (Government Corruption)', 'Generosity'],
                         animation_frame="Year", color_discrete_sequence=px.colors.sequential.Plasma)

    denseFig = px.treemap(whddf, path=[px.Constant("world"), 'Region', 'Country'], values='Economy (GDP per Capita)',
                  color='Happiness Score', hover_data=['Economy (GDP per Capita)'],
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(whddf['Happiness Score'], weights=whddf['Economy (GDP per Capita)']))
    denseFig.update_layout(margin = dict(t=50, l=25, r=25, b=25))

    pieFig = px.sunburst(whddf, path=['Region', 'Country'], values='Trust (Government Corruption)',
                  color='Happiness Score', hover_data=['iso_alpha'],
                  color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(whddf['Happiness Score'], weights=whddf['Trust (Government Corruption)']))

    return histoFig, denseFig, mainFig, pieFig, scatterFig

# FYI you can't have multiple callbacks with the same id so don't try lol

# run the app
if __name__ == '__main__': 
    app.run_server(debug=True)
