import string
import pandas as pd
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output

df = pd.read_csv('babynames1880-2020.csv')
#df = df.head(200)
alphabet_string = string.ascii_uppercase

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.H1(children='A web application to look up baby names 1880-2020',
            style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
            ),
    dbc.Row([
        dbc.Col(html.Div(children=[
            html.H6("Select gender:"),
            dcc.RadioItems(id='radio_gender',
                           options=[{'label': 'Male', 'value': 'M'},
                                    {'label': 'Female', 'value': 'F'}, ], value='M'),
            html.H6(" "),
            html.H6("Select initial letter:"),
            dcc.Dropdown(id='start_letter', options=[
                {'value': x, 'label': x} for x in alphabet_string
            ], multi=True),
            html.H6("Max. year"),
            dcc.Dropdown(id='max_year', options=[
                {'value': x, 'label': x} for x in range(1880, 2021)
            ], value=2020),
            html.H6("Min. year:"),
            dcc.Dropdown(id='min_year', options=[
                {'value': x, 'label': x} for x in range(1880, 2021)
            ], value=1880),
            html.H6("Max. rank:"),
            dcc.Dropdown(id='max_rank', options=[
                {'value': x, 'label': x} for x in range(1, 1001)
            ], value=1),
            html.H6("Min. rank:"),
            dcc.Dropdown(id='min_rank', options=[
                {'value': x, 'label': x} for x in range(1, 1001)
            ], value=1000)
        ]), width=3),
        dbc.Col([
            dcc.Graph(id='top_20')
        ], width=9)
    ]),
    dbc.Row([
        dbc.Col([html.H3("Rank over time:"), dcc.Graph(id='rank_time')], width=6),
        dbc.Col([html.H3("Births over time:"), dcc.Graph(id='birth_time')], width=6)
    ])
])

@app.callback(
    Output(component_id='top_20', component_property='figure'),
    Input(component_id='radio_gender', component_property='value'),
    Input(component_id='start_letter', component_property='value'),
    Input(component_id='max_year', component_property='value'),
    Input(component_id='min_year', component_property='value'),
    Input(component_id='max_rank', component_property='value'),
    Input(component_id='min_rank', component_property='value')
)
def update_name_graph(gender, letter, y_max, y_min, r_max, r_min):
    dff = df
    dff = dff[dff['Gender'] == gender]
    dff = dff[dff['Year'] >= y_min]
    dff = dff[dff['Year'] <= y_max]
    dff = dff[dff['Rank'] <= r_min]
    dff = dff[dff['Rank'] >= r_max]

    if letter is not None:
        if len(letter) > 1:
            new_df = []
            for i in range(len(letter)):
                dff = dff[dff['Name'].str.get(0) == letter[i]]
                new_df.append(dff)
                print(new_df)
            dff = new_df
        elif len(letter) == 1:
            dff = dff[dff['Name'].str.get(0) == letter[0]]

    dff.sort_values(by='Births', ascending=False)

    dff = dff.head(20)
    fig = px.scatter(dff, x="Name", y="Births")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)