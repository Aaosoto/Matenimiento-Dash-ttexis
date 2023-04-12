import dash
import pandas as pd
import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc
import plotly.express as px
from dash.dependencies import Input, Output

from drive_api import api_drive

from PIL import Image
pil_image = Image.open("assets/ttexis-logo.png")


FILEPATH = 'data/date-transactions.xlsx'
FILEPATH1 = 'data/city-transactions.xlsx'

workbooks = api_drive()

app = dash.Dash()

server = app.server

#df = pd.read_excel(FILEPATH)
image_filename = 'assets/ttexis-logo.png'


app.layout = html.Div(id = 'parent', children = [
        html.Img(src=pil_image, style={'height':'10%','width':'10%', 'display':'inline-block'}),
        html.H1(id = 'H1', children = 'Dashboard Sales', style = {'textAlign':'center','marginLeft':'30%', 'display':'inline-block'}),
        
        html.Button(id='update-button', children="Update", n_clicks=0,style={'marginLeft':'90%','display':'flex'}),
        dcc.Dropdown( id = 'dropdown',
        options = [
            {'label':'2013', 'value':'2013' },
            {'label': '2014', 'value':'2014'},
            {'label': '2015', 'value':'2015'},
            {'label': '2016', 'value':'2016'},
            {'label': '2017', 'value':'2017'},
            {'label': 'All', 'value':'All'}
            ],
        value = 'All'),
        
        dcc.Graph(id = 'line_plot',style={"width":600, "margin": 0,'display': 'inline-block'}),
        dcc.Graph(id = 'bar_plot',style={"width":600, "margin": 0,'display': 'inline-block'}),
        dcc.Graph(id = 'tree_plot',style={"width":600, "margin": 0, 'display': 'inline-block'}),
        dcc.Graph(id = 'pie_plot',style={"width":600, "margin": 0,'display': 'inline-block'})
    ])
#Add a bar chart (max price each one) and a pie chart (% price above $2 FB)
    
@app.callback(
        [Output(component_id='line_plot', component_property= 'figure'),
         Output(component_id='bar_plot', component_property= 'figure'),
         Output(component_id='tree_plot', component_property= 'figure'),
         Output(component_id='pie_plot', component_property= 'figure')],
        [Input(component_id='dropdown', component_property= 'value'),
         Input(component_id='update-button',component_property='n_clicks')]
        )
def graph_update(dropdown_value, num_clicks):
    print(dropdown_value)
    if num_clicks > 0:
        df1 = pd.DataFrame(workbooks[1].get_all_records())
        df = pd.DataFrame(workbooks[0].get_all_records())
    else:
        dash.exceptions.PreventUpdate
    df = pd.DataFrame(workbooks[0].get_all_records())
    df1 = pd.DataFrame(workbooks[1].get_all_records())

    #Date DataSet
    df1['date'] = df1['date'].astype('datetime64')
    df1 = df1.groupby(df1['date'].dt.to_period('m')).sum()
    df1 = df1.reset_index()
    df1['date'] = df1['date'].astype('datetime64')
    df_total_year = df1.groupby(df1['date'].dt.to_period('y')).sum().reset_index()
    df_total_year['date'] = df_total_year['date'].astype('datetime64')

    #City DataSet
    df_city_filter = df.sort_values(by='Sum(transactions)',ascending=False).head()
    df_city_filter.loc[len(df_city_filter.index)] = ['Other', df['Sum(transactions)'].sum()-df_city_filter['Sum(transactions)'].sum()]
    
    if dropdown_value == 'All':
        fig = go.Figure([go.Scatter(x = df1['date'], y = df1['Sum(transactions)'],
                    name='Total Sales')
                    ])
        fig1 = go.Figure([go.Bar(x = df_total_year['date'].dt.year, y = df_total_year['Sum(transactions)'], name='Total Sales per Year')])
    else:
        df_filter = df1[df1['date'].dt.year == int(dropdown_value)]
        df_filter_year = df_total_year[df_total_year['date'].dt.year == int(dropdown_value)]
        fig = go.Figure([go.Scatter(x = df_filter['date'], y = df_filter['Sum(transactions)'],line = dict(color = 'firebrick', width = 4))
            ])
        fig1 = go.Figure([go.Bar(x = df_filter_year['date'].dt.year, y = df_filter_year['Sum(transactions)'], name='Total Sales per Year')])
    fig2 = px.treemap(df, path=[px.Constant("Ecuador"), 'city'], 
                 values='Sum(transactions)', color='city', color_continuous_scale='rdbu'
                 )
    fig3 = px.pie(df_city_filter, values='Sum(transactions)', names='city', title='Sales per City Percentage', hole=.4)
    fig.update_layout(title = 'Total Sales',
                    xaxis_title = 'Date',
                    yaxis_title = 'Sales'
                    )
    fig1.update_layout(title = 'Total Sales per Year',
                    xaxis_title = 'Date',
                    yaxis_title = 'Sales'
                    )    
    fig2.update_layout(title = 'Total Sales per City',
                    margin = dict(t=50, l=25, r=25, b=25)
                    )
    fig3.update_layout(title = 'Total Sales per City Percentage',
                )

    return fig, fig1, fig2, fig3




if __name__ == '__main__': 
    app.run_server(debug=True)