import string
import pandas as pd
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

df = pd.read_csv('babynames1880-2020.csv')
alphabet_string = string.ascii_uppercase
list_selected = []

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.H1(children='Look up baby names 1880-2020',
            style={'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}
            ),
    dbc.Row(html.Div([], style={'padding': 40})),
    dbc.Row([html.H3("Distribution of births by gender:"),
            html.Div([dbc.Button('Show distribution', id='show_btn', n_clicks=0)]),
             dbc.Col([html.Div([dcc.Graph(id='gender_dist')])], width=12)
             ]),
    dbc.Row([
        dbc.Col(html.Div(children=[
            html.H3("Filtering of top 10"),
            dbc.Row(html.Div([], style={'padding': 10})),
            html.H6("Select gender:"),
            dcc.RadioItems(id='radio_gender', labelStyle={'display': 'block'},
                           options=[{'label': 'Male', 'value': 'M'},
                                    {'label': 'Female', 'value': 'F'}, ], value='M'),
            html.H6(" "),
            html.H6("Select initial letter(s):"),
            dcc.Dropdown(id='start_letter', options=[
                {'value': x, 'label': x} for x in alphabet_string
            ], multi=True),
            html.H6("Year"),
            dcc.RangeSlider(min=1880, max=2020, id='year_slider', tooltip={'placement': 'bottom'}, value=[1880, 2020]),
            html.H6("Rank"),
            dcc.RangeSlider(min=1, max=1000, id='rank_slider', tooltip={'placement': 'bottom'}, value=[1, 1000]),
        ]), width=3),
        dbc.Col(html.Div(children=[
            html.H3("Total births top 10", style={'textAlign': 'center'}),
            dcc.Graph(id='top_20')
        ], style={'margin-left': 100}), width=9)
    ]),
    dbc.Row([html.Div([
        html.H3("Click on scatter in the top 10 to show graph below:", style={'textAlign': 'center'})
    ])]),
    dbc.Row([
        dbc.Col([html.H3("Births over time", style={'textAlign': 'center', 'padding': 10}), dcc.Graph(id='birth_time')],
                width=10),
        dbc.Col(html.Div([dbc.Button("Clear graph", id='btn', n_clicks=0)], style={'margin-top': 100}), width=2)
    ]),
])


@app.callback(
    Output(component_id='gender_dist', component_property='figure'),
    Input(component_id='show_btn', component_property='n_clicks'),
)
def show_dist_graphs(n_click):
    if n_click > 0:
        dff = df
        dff = dff[['Year', 'Births', 'Gender']]
        dff = dff.groupby(['Year', 'Gender']).sum()
        print(dff.head())
        dff.reset_index(level=0, inplace=True)
        dff.reset_index(level=0, inplace=True)
        print(dff.head())
        fig = px.area(dff, x='Year', y='Births', color='Gender')
        return fig
    else:
        return px.line()

@app.callback(
    Output(component_id='top_20', component_property='figure'),
    Input(component_id='radio_gender', component_property='value'),
    Input(component_id='start_letter', component_property='value'),
    Input(component_id='year_slider', component_property='value'),
    Input(component_id='rank_slider', component_property='value'),
)
def update_name_graph(gender, letter, year, rank):
    dff = df
    dff = dff[dff['Gender'] == gender]
    dff = dff[dff['Year'] >= year[0]]
    dff = dff[dff['Year'] <= year[1]]
    dff = dff[dff['Rank'] <= rank[1]]
    dff = dff[dff['Rank'] >= rank[0]]

    if letter is not None:
        if len(letter) > 1:
            new_df = dff[dff['Name'].str.get(0) == letter[0]]
            for i in range(1, len(letter)):
                filtered_df = dff[dff['Name'].str.get(0) == letter[i]]
                new_df = new_df.append(filtered_df, ignore_index=True)
            dff = new_df
        elif len(letter) == 1:
            dff = dff[dff['Name'].str.get(0) == letter[0]]

    dff = dff[['Name', 'Births', 'Rank']]
    dff = dff.groupby('Name').agg(Births=('Births', 'sum'), Rank=('Rank', 'mean'))
    dff.reset_index(level=0, inplace=True)
    dff = dff.sort_values(by='Births', ascending=False)

    dff = dff.head(10)
    dff['Rank'] = dff['Rank'].round(0).astype(int)
    dff.rename(columns={'Rank': 'Average rank'}, inplace=True)
    fig = px.scatter(dff, x="Name", y="Births", color='Average rank',
                     color_continuous_scale=px.colors.sequential.Plotly3).update_xaxes(categoryorder='total descending')
    fig.update_traces(marker=dict(size=20, line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))
    return fig


@app.callback(
    Output(component_id='birth_time', component_property='figure'),
    Output(component_id='btn', component_property='n_clicks'),
    Output(component_id='top_20', component_property='clickData'),
    Input(component_id='top_20', component_property='clickData'),
    Input(component_id='radio_gender', component_property='value'),
    Input(component_id='btn', component_property='n_clicks'),
    prevent_initial_call=True
)
def update_name_graph(selected_name, gender, n_clicks):
    if n_clicks > 0:
        list_selected.clear()
        return px.line(), 0, None

    if selected_name is not None:
        name = selected_name['points'][0]['x']

        if name in list_selected:
            list_selected.remove(name)
        else:
            list_selected.insert(len(list_selected), name)

        dff = df
        dff = dff[dff['Name'].isin(list_selected)]
        dff = dff[dff['Gender'] == gender]
        fig = px.line(dff, x='Year', y='Births', color='Name')
    else:
        fig = px.line()
    return fig, 0, None


if __name__ == '__main__':
    app.run_server(debug=True)
