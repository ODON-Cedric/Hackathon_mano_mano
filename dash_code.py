import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import re
import plotly.express as px


# PREPROCESS
df = pd.read_csv("hackathon_mano.csv", low_memory=False).drop(columns="Unnamed: 0", axis=1)
df.created_at = df.created_at.apply(lambda row: re.search("\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}:\d{2})", row)[1])
df["browser_simplified"] = df.browser.apply(lambda row: re.search("[A-z ]+", row)[0].strip())
df["os_simplified"] = df.operating_system.apply(lambda row: re.search("[A-z ]+", row)[0].strip())
df["calc_purp"] = 1


# APP SETTING
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'initial-scale=1.0'}]
                )

# APP LAYOUT
app.layout = dbc.Container([
    dbc.Row([
            # UNIQUE COL FOR TITLE
            dbc.Col(html.H1("Comprehensive KPI dashboard",
                            className='text-center text-primary, mb-4'),
                            width=12,
                            style={'color': '#008c9d'})
        ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='dropdown',
                         options=[
                             {'label': 'Geographic Zone', 'value': 'platform'},
                             {'label': 'Device', 'value': 'device'},
                             {'label': 'Day of the week', 'value': 'day'},
                             {'label': 'Month', 'value': 'month'},
                             {'label': 'Browser', 'value': 'browser_simplified'},
                             {'label': 'OS', 'value': 'os_simplified'},
                             {'label': 'Payment method', 'value': 'payment_method'},
                             {'label': 'Provider', 'value': 'provider'},
                             {'label': 'Family', 'value': 'family'},
                             {'label': 'First order', 'value': 'first_order'},
                             {'label': 'Csat presales', 'value': 'csat_presales'},
                             {'label': 'Presales contact', 'value': 'has_presales_contact'},
                             {'label': 'Manodvisor contact', 'value': 'has_manodvisor_contact'},
                         ],
                         optionHeight=35,  # height/space between dropdown options
                         value=['device', 'platform'],  # dropdown value selected automatically when page loads
                         disabled=False,  # disable dropdown value selection
                         multi=True,  # allow multiple dropdown values to be selected
                         searchable=True,  # allow user-searching of dropdown values
                         search_value='',  # remembers the value searched in dropdown
                         placeholder='Please select up to 2 values',  # gray, default text shown when no option is selected
                         clearable=True,  # allow user to removes the selected value
                         style={'width': "100%",},  # use dictionary to define CSS styles of your dropdown
                         # className='select_box',           #activate separate CSS document in assets folder
                         # persistence=True,                 #remembers dropdown value. Used with persistence_type
                         # persistence_type='memory'         #remembers dropdown value selected until...
                         ),
            dcc.RadioItems(id='raditem',
                           options=[{'label': 'BV Transaction', 'value': 'bv_transaction'},
                                    {'label': 'Satisfaction', 'value': 'score'},
                                    {'label': 'Nb Articles', 'value': 'nb_articles'},
                                    {'label': 'Shipping Fees', 'value': 'shipping_fees'},
                                    ],
                           inputStyle={"margin-left": "5px",
                                       "margin-top": "20px"
                                       },
                           value='bv_transaction',
                           style={"width": "100%"}
                           ),
            dcc.RadioItems(id='raditem2',
                           options=[{'label': 'Count', 'value': 'count'},
                                    {'label': 'Mean', 'value': 'mean'},
                                    {'label': 'Min', 'value': 'min'},
                                    {'label': 'Max', 'value': 'max'},
                                    {'label': 'Sum', 'value': 'sum'}
                                    ],
                           inputStyle={"margin-left": "5px",
                                       "margin-top": "20px",
                                       },
                           value='count',
                           style={"width": "100%"}
            ),
            dcc.Graph(id='barchart')
        ])
    ]),
    dbc.Row([
            dbc.Col([
                dcc.Dropdown(id='dropdown2',
                             options=[
                                 {'label': 'Geographic Zone', 'value': 'platform'},
                                 {'label': 'Device', 'value': 'device'},
                                 {'label': 'Day of the week', 'value': 'day'},
                                 {'label': 'Month', 'value': 'month'},
                                 {'label': 'Browser', 'value': 'browser_simplified'},
                                 {'label': 'OS', 'value': 'os_simplified'},
                                 {'label': 'Payment method', 'value': 'payment_method'},
                                 {'label': 'Provider', 'value': 'provider'},
                                 {'label': 'Family', 'value': 'family'},
                                 {'label': 'First order', 'value': 'first_order'},
                                 {'label': 'Csat presales', 'value': 'csat_presales'},
                                 {'label': 'Presales contact', 'value': 'has_presales_contact'},
                                 {'label': 'Manodvisor contact', 'value': 'has_manodvisor_contact'},
                             ],
                             optionHeight=35,  # height/space between dropdown options
                             value=['device', 'platform'],  # dropdown value selected automatically when page loads
                             disabled=False,  # disable dropdown value selection
                             multi=True,  # allow multiple dropdown values to be selected
                             searchable=True,  # allow user-searching of dropdown values
                             search_value='',  # remembers the value searched in dropdown
                             placeholder='Please select atleast 2 values',  # gray, default text shown when no option is selected
                             clearable=True,  # allow user to removes the selected value
                             style={'width': "100%"},  # use dictionary to define CSS styles of your dropdown
                             # className='select_box',           #activate separate CSS document in assets folder
                             # persistence=True,                 #remembers dropdown value. Used with persistence_type
                             # persistence_type='memory'         #remembers dropdown value selected until...
                             ),
                dcc.RadioItems(id='raditem3',
                               options=[{'label': 'BV Transaction', 'value': 'bv_transaction'},
                                        {'label': 'Nb Articles', 'value': 'nb_articles'},
                                        {'label': 'Shipping Fees', 'value': 'shipping_fees'},
                                        ],
                               inputStyle={"margin-left": "5px",
                                           "margin-top": "20px"
                                           },
                               value='bv_transaction',
                               style={"width": "100%"}
                               ),
                dcc.Graph(id='sunburst',
                          style={"margin-top": "50px"})
            ])
        ])
])


# CALLBACKS

@app.callback(
    Output(component_id='barchart', component_property='figure'),
    [Input(component_id='dropdown', component_property='value'),
     Input(component_id='raditem', component_property='value'),
     Input(component_id='raditem2', component_property='value')],
    prevent_initial_call=False
)
def generate_graph(cats, colname, aggr):
    if len(cats) == 0 or len(cats)>2:
        raise dash.exceptions.PreventUpdate
    else:
        da_df = df.groupby(cats, as_index=False)[colname].agg(aggr)
    if len(cats) == 2:
        barplot = px.bar(
            data_frame=da_df,
            x=cats[0],
            y=colname,
            color=cats[1],
            text_auto=True,
            opacity=0.9,
            orientation="v",
            barmode='group',
            template='plotly_white',
            color_discrete_sequence=px.colors.sequential.Tealgrn,
            title=f"{colname.title()} grouped by {cats[0].lower()} and {cats[1].lower()}, aggreged by {aggr}",
        )
    else:
        barplot = px.bar(
            data_frame=da_df,
            x=cats[0],
            y=colname,
            text_auto=True,
            opacity=0.9,
            orientation="v",
            barmode='group',
            template='plotly_white',
            color_discrete_sequence=px.colors.sequential.Tealgrn,
            title=f"{colname.title()} grouped by {cats[0].lower()}, aggreged by {aggr}",
        )
    return barplot


@app.callback(
    Output(component_id='sunburst', component_property='figure'),
    [Input(component_id='dropdown2', component_property='value'),
     Input(component_id='raditem3', component_property='value')],
    prevent_initial_call=False
)
def generate_sunburst(cats, colname):
    if len(cats) < 2:
        raise dash.exceptions.PreventUpdate
    else:
        sunburst = px.sunburst(
            data_frame=df,
            path=cats,
            values=colname,
            template='plotly_white',
            color='score',
            color_continuous_scale='Tealgrn',
            )
    sunburst.update_layout(
        grid=dict(columns=2, rows=1),
        margin=dict(t=0, l=0, r=0, b=0)
    )
    return sunburst

# APP LAUNCH
if __name__ == '__main__':
    app.run_server(debug=True, port=5679)
