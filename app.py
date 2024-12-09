# Imports
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Load Data
df = pd.read_csv("assets/2022.csv")

# Initialize Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    html.Div(className='app-header', children=[
        html.H1("World Happiness Index Dashboard", className='display-3')
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="metric-dropdown",
                options=[
                    {'label': 'Happiness Score', 'value': 'Score'},
                    {'label': 'GDP per capita', 'value': 'GDP per capita'},
                    {'label': 'Social Support', 'value': 'Social support'},
                    {'label': 'Healthy Life Expectancy', 'value': 'Healthy life expectancy'},
                    {'label': 'Freedom to Make Life Choices', 'value': 'Freedom to make life choices'},
                    {'label': 'Generosity', 'value': 'Generosity'},
                    {'label': 'Perceptions of Corruption', 'value': 'Perceptions of corruption'}
                ],
                value='Score',
                className='dropdown'
            )
        ], width=6, className='dropdown-container')
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='world-map'), width=6, className='graph-container'),
        dbc.Col(dcc.Graph(id='pie-chart'), width=6, className='graph-container')
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='data-insights', className='data-insights'), width=8),
        dbc.Col(html.Div(id='country-details', className='country-details'), width=4)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="second-metric-dropdown",
                options=[
                    {'label': metric, 'value': metric}
                    for metric in df.columns if metric not in ['Country or region', 'Overall rank']
                ],
                placeholder="Select a second metric for scatter plot",
                className='dropdown'
            )
        ], width=6),
        dbc.Col(dcc.Graph(id='scatter-plot'), width=6, className='graph-container'),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='bar-chart'), width=6, className='graph-container'),
        dbc.Col(dcc.Graph(id='trend-line'), width=6, className='graph-container'),
    ]),
], fluid=True)

# Callbacks
@app.callback(
    Output('world-map', 'figure'),
    Input("metric-dropdown", 'value')
)
def update_map(selected_metric):
    fig = px.choropleth(
        df,
        locations="Country or region",
        locationmode='country names',
        color=selected_metric,
        hover_name="Country or region",
        color_continuous_scale=px.colors.sequential.Plasma,
        title=f"World Happiness Index: {selected_metric}"
    )
    fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
    return fig

@app.callback(
    Output('data-insights', 'children'),
    Input('metric-dropdown', 'value')
)
def update_insights(selected_metric):
    highest = df.loc[df[selected_metric].idxmax()]
    lowest = df.loc[df[selected_metric].idxmin()]
    insights = [
        html.H3(f"Highest {selected_metric}: {highest['Country or region']} ({highest[selected_metric]})"),
        html.H3(f"Lowest {selected_metric}: {lowest['Country or region']} ({lowest[selected_metric]})")
    ]
    return insights

@app.callback(
    Output('country-details', 'children'),
    Input('world-map', 'clickData')
)
def display_country_details(clickData):
    if clickData:
        country_name = clickData['points'][0]['location']
        country_data = df[df['Country or region'] == country_name]

        if not country_data.empty:
            country = country_data.iloc[0]
            details = [
                html.H3(f"Details for {country_name}"),
                html.P(f"Overall Rank: {country['Overall rank']}"),
                html.P(f"Score: {country['Score']}"),
                html.P(f"GDP per Capita: {country['GDP per capita']}"),
                html.P(f"Social Support: {country['Social support']}"),
                html.P(f"Healthy Life Expectancy: {country['Healthy life expectancy']}"),
                html.P(f"Freedom to Make Life Choices: {country['Freedom to make life choices']}"),
                html.P(f"Generosity: {country['Generosity']}"),
                html.P(f"Perceptions of Corruption: {country['Perceptions of corruption']}")
            ]
            return html.Div(details, className='country-details-section')
    return html.Div("Click on a country to see details.", className='country-details-section')

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('metric-dropdown', 'value'), Input('second-metric-dropdown', 'value')]
)
def update_scatter_plot(metric1, metric2):
    if metric1 and metric2:
        fig = px.scatter(df, x=metric1, y=metric2, color='Country or region',
                         title=f"{metric1} vs {metric2}", hover_name="Country or region")
        fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
        return fig
    return px.scatter(title="Select metrics to visualize")

@app.callback(
    Output('bar-chart', 'figure'),
    Input('metric-dropdown', 'value')
)
def update_bar_chart(selected_metric):
    top_10 = df.nlargest(10, selected_metric)
    fig = px.bar(top_10, x='Country or region', y=selected_metric, 
                 title=f"Top 10 Countries by {selected_metric}", color=selected_metric, color_continuous_scale=px.colors.sequential.Viridis)
    fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
    return fig

@app.callback(
    Output('trend-line', 'figure'),
    Input('metric-dropdown', 'value')
)
def update_trend_line(selected_metric):
    fig = px.line(df.sort_values(selected_metric), x='Overall rank', y=selected_metric,
                  title=f"{selected_metric} Trend vs Overall Rank")
    fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
    return fig

@app.callback(
    Output('pie-chart', 'figure'),
    [Input('world-map', 'clickData'), Input('metric-dropdown', 'value')]
)
def update_pie_chart(clickData, selected_metric):
    if clickData:
        country_name = clickData['points'][0]['location']
        country_data = df[df['Country or region'] == country_name]

        if not country_data.empty:
            country_score = country_data[selected_metric].values[0]
            global_average = df[selected_metric].mean()
            pie_data = pd.DataFrame({
                "Category": [f"{country_name}'s {selected_metric}", "Global Average"],
                "Value": [country_score, global_average]
            })

            fig = px.pie(
                pie_data,
                names='Category',
                values='Value',
                title=f"{selected_metric}: {country_name} vs Global Average",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
            return fig

    return px.pie(
        title="Click on a country to generate the pie chart",
        color_discrete_sequence=px.colors.sequential.RdBu
    ).update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')

if __name__ == "__main__":
    app.run_server(debug=True)
