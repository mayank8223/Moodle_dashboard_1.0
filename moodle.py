#Importing all the libraries
import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import datetime
import time
from datetime import date
from datetime import timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go

 # Read scv
df=pd.read_csv("LA.csv")

# cleaning and Restructurig the data
user=set([])
for index, row in df.iterrows():
    if row['Origin'] =="cli":
        df.drop(index, inplace=True)
    elif row["User full name"]=="-" or row["User full name"]=="Admin User":
        df.drop(index, inplace=True)
    elif row["Event name"]=="Course module created" or row["Event name"]=="User enrolled in course" or row["Event name"]=="Course section created":
        user.add(row["User full name"])
for i in user:
    df=df[df["User full name"] != i]  

# adding date column
D=[]
for d in df["Time"]:
  D.append(date.fromtimestamp(time.mktime(datetime.datetime.strptime(d.split(",")[0], "%d/%m/%y").timetuple())))
df["Date"]=D

#reversing the dataframe
df1=df.to_numpy()
df2=pd.DataFrame(df1[::-1])
df2.columns=df.columns

# addin week column
WEEK=[]
a=df2["Date"][0]
k=1
for i in df2["Date"]:
  if (i < ( a + timedelta(days=7))):
    WEEK.append("week"+str(k))
  else:
    a=i
    k+=1
    WEEK.append("week"+str(k))
df2["Week"]=WEEK


# obtaining user names
user_name=df2["User full name"].unique()

# list of assignments
assig = []
for i,j in zip(df2["Event context"],df2["Component"]):
    if j == 'Assignment':
        assig.append(i)
assig=list(set(assig))


# Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
html.Div([
        dbc.Row(dbc.Col(html.H1("Teacher Dashboard"),width={'size': 6, 'offset': 5} ) ),
        
        dbc.Row(dbc.Col(html.H4("Participation"),width={'size': 6, 'offset': 1}) ),
        
        dbc.Row([dbc.Col(dcc.Dropdown(id='drop_down1',options=[{"label": i ,"value": i} for i in df2["Week"].unique()],value="week1",style={"width": "50%"}),width={'size': 6, 'offset': 1})])
        ]),

html.Div([dcc.Graph(id='the_graph')]),


html.Div([
        dbc.Row( dbc.Col(html.H4("Discussion Forum"),width={'size': 6, 'offset': 1})),

        dbc.Row(dbc.Col(html.H6("This section displays the students activity in Discussion Forum"),width={'size': 6, 'offset': 1}) ),
        
        dbc.Row([dbc.Col(dcc.Dropdown(id='drop_down2', options=[{"label": i ,"value": i} for i in df2["Week"].unique()],value="week1",style={"width": "50%"}),width={'size': 6, 'offset': 1})])
        ]),
    
html.Div([dcc.Graph(id='graph_dis')]),

html.Div([
        dbc.Row( dbc.Col(html.H4("Assignment"),width={'size': 6, 'offset': 1})),
    
        dbc.Row(dbc.Col(html.H6("This section displays the information about assignments in the course"),width={'size': 6, 'offset': 1}) ),
        
        dbc.Row([dbc.Col(dcc.Dropdown(id='drop_down3',options=[{"label": i ,"value": i} for i in assig],value=assig[0],style={"width": "50%"}),width={'size': 6, 'offset': 1})]),
        ]),

html.Div([dcc.Graph(id='graph_asg')]),
    
html.Div([
        dbc.Row( dbc.Col(html.H4("Student Information"),width={'size': 6, 'offset': 1})),
        
        dbc.Row(dbc.Col(html.H6("This section displays the information about individual Student"),width={'size': 6, 'offset': 1},) ),
        
        dbc.Row([dbc.Col(dcc.Dropdown(id='drop_down4',options=[{"label": i ,"value": i} for i in user_name],value=user_name[0],style={"width": "50%"}),width={'size': 6, 'offset': 1})]),
        ]),

html.Div([dcc.Graph(id='graph_std')])


])

@app.callback(Output(component_id='graph_std', component_property='figure'),[Input(component_id='drop_down4', component_property='value')])

def update_graph_std(drop_down4):
    
    action_category={"Course view":0,"Activity on Discussion Forum":0,"Action on Assignment":0,"Course module viewed":0,"Mis":0}
    weekly_act=list(np.zeros(len(df2["Week"].unique())))
    for i in range(len(df2["User full name"])):
        if df2["User full name"][i]==drop_down4:
            for j in range(len(weekly_act)):
                if df2["Week"][i]==("week"+str(j)):
                    weekly_act[j]+=1
        if df2["Event name"][i]=="Course viewed":
            action_category["Course view"]+=1
        elif df2["Component"][i]=="Forum":
            action_category["Activity on Discussion Forum"]+=1
        elif df2["Component"][i]=="Assignment":
            action_category["Action on Assignment"]+=1
        elif df2["Event name"][i]=="Course module viewed":
            action_category["Course module viewed"]+=1
        else :
             action_category["Mis"]+=1
    
    fig = make_subplots(rows=1, cols=2,specs=[[{'type':'domain'},{'type':'xy'}]])
          
    fig.add_trace(go.Pie(values=list(action_category.values()),labels=list(action_category.keys())),row=1,col=1)
    fig.update_traces(hole=.2, hoverinfo="label+percent+name")
    fig.add_trace(go.Scatter(x=df2["Week"].unique(),y=weekly_act),row=1,col=2)
    
    fig.update_layout(template="plotly_dark",height=500, showlegend=False)
    
    return (fig)

@app.callback(Output(component_id='graph_asg', component_property='figure'),[Input(component_id='drop_down3', component_property='value')])

def update_graph_asg(drop_down3):
    
    asg_sub=list(np.zeros(len(user_name)))
    asg_view=list(np.zeros(len(user_name)))
    for i in range(len(df2["User full name"])):
        for j in range(len(user_name)):
            if df2["User full name"][i]==user_name[j] and df2["Event context"][i]==drop_down3 :
                if df2["Event name"][i]=="A submission has been submitted.":
                    asg_sub[j]=1
                if df2["Event name"][i]=="Course module viewed":
                    asg_view[j]=1
    
    fig = make_subplots(rows=1, cols=2,specs=[[{'type':'domain'}, {'type':'domain'}]])
          
    
    fig.add_trace(go.Pie(values=[asg_sub.count(0.0),asg_sub.count(1)],labels=["Not submitted","Submitted"]),row=1,col=1)
    fig.add_trace(go.Pie(values=[asg_view.count(0.0),asg_view.count(1)],labels=["Not Viewed","Viewed"]),row=1,col=2)
    
    fig.update_traces(hole=.4, hoverinfo="label+percent+name")
    
    fig.update_layout(annotations=[dict(text='Submit', x=0.2, y=0.5, font_size=20, showarrow=False),dict(text='View', x=0.80, y=0.5, font_size=20, showarrow=False)])
    
    return (fig)
                    
    
@app.callback(Output(component_id='the_graph', component_property='figure'),[Input(component_id='drop_down1', component_property='value')])

def update_the_graph(drop_down1):
    
    no_of_act=list(np.zeros(len(user_name)))
    action_category={"Course view":0,"Activity on Discussion Forum":0,"Action on Assignment":0,"Course module viewed":0,"Mis":0}

    for i in range(len(df2["User full name"])):
        if df2["Week"][i]==drop_down1:
            for j in range(len(user_name)):
                if df2["User full name"][i]==user_name[j]:
                    no_of_act[j]+=1
            if df2["Event name"][i]=="Course viewed":
                action_category["Course view"]+=1
            elif df2["Component"][i]=="Forum":
                action_category["Activity on Discussion Forum"]+=1
            elif df2["Component"][i]=="Assignment":
                action_category["Action on Assignment"]+=1
            elif df2["Event name"][i]=="Course module viewed":
                action_category["Course module viewed"]+=1
            else :
                action_category["Mis"]+=1
                
                
    
    fig = make_subplots(rows=1, cols=2)
          
    
    fig.add_trace(go.Box(y=no_of_act),row=1,col=1)
    fig.add_trace(go.Bar(x=list(action_category.keys()),y=list(action_category.values())),row=1,col=2)
    
    fig.update_layout(height=500, showlegend=False)
    
    return (fig)

@app.callback(Output(component_id='graph_dis', component_property='figure'),[Input(component_id='drop_down2', component_property='value')])


def update_graph_dis(drop_down2):    
    no_of_dis=list(np.zeros(len(user_name)))
    no_of_post=list(np.zeros(len(user_name)))
    no_of_view=list(np.zeros(len(user_name)))
    for i in range(len(df2["User full name"])):
        for j in range(len(user_name)):
            if df2["User full name"][i]==user_name[j] and df2["Week"][i]==drop_down2:
                if df2["Event name"][i]=="Discussion created":
                    no_of_dis[j]+=1
                if df2["Event name"][i]=="Post created":
                    no_of_post[j]+=1
                if df2["Event name"][i]=="Discussion viewed":
                    no_of_view[j]+=1
    dis_part=[no_of_dis.count(0.0),len(no_of_dis)-no_of_dis.count(0.0)]
    dis_post=[no_of_post.count(0.0),len(no_of_post)-no_of_post.count(0.0)]
    dis_view=[no_of_view.count(0.0),len(no_of_view)-no_of_view.count(0.0)]

    fig = make_subplots(1,3)
    
    fig.add_trace(go.Bar(x=["No Discussion created","Discussion Created"],y=dis_part),row=1, col=1)
    fig.add_trace(go.Bar(x=["No Post","Post Created"],y=dis_post),row=1, col=3)
    fig.add_trace(go.Bar(x=["Discussion not viewed","Discussion viewed"],y=dis_view),row=1, col=2)

    fig.update_layout(height=500, showlegend=False)

    return (fig)


if __name__ == "__main__":
    app.run_server(debug=True)
