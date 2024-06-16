# Import required libraries
#%%
import pandas as pd
#%%
import dash
from dash import html
#import dash_html_components as html
from dash import dcc
#import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
#%%
# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
#%%
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                    ],
                                    value='ALL',  # default value
                                    placeholder="Select a Launch Site",  # placeholder text
                                    searchable=False  # disable search
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,  # step increment
                                    value=[min_payload, max_payload],  # default value
                                    marks={min_payload: str(min_payload), max_payload: str(max_payload)}  # slider labels
                                ),


                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Count successful launches for all sites
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts()
        labels = ['Success', 'Failure']
        values = [success_counts.sum(), len(spacex_df) - success_counts.sum()]
        title = 'Total Successful Launches by Site'
    else:
        # Filter dataframe based on selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        # Count successful and failed launches for the selected site
        success_counts = filtered_df['class'].value_counts()
        labels = ['Success', 'Failure']
        values = [success_counts.get(1, 0), success_counts.get(0, 0)]
        title = f'Success vs. Failure for {selected_site}'
    
    # Create pie chart figure
    fig = px.pie(names=labels, values=values, title=title)
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter dataframe based on selected launch site and payload range
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) & 
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    # Create scatter chart
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='class',
                     title='Correlation between Payload and Launch Success',
                     labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Launch Outcome'},
                     hover_name='Booster Version')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()