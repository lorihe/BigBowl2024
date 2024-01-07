import pandas as pd
import numpy as np

import plotly.graph_objects as go
from football_field import plot_field

def plot(tracking_df, date, tacklers, carrier, offense, defense, down, yardstogo, ablos):
    
    # Legend and play info
    fig2 = go.Figure()
    colors = ['midnightblue', 'lightsteelblue', 'peru', 'burlywood']
    sizes = [20, 12, 20, 12]
    labels = ['Tackler', 'Defense', 'Carrier', 'Offense']

    for i in range(4):
        fig2.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
            marker=dict(size=sizes[i], color=colors[i], symbol='arrow', angle = -90),
            name=labels[i], showlegend=True))
    fig2.update_layout(legend = dict(xanchor = 'center', yanchor = 'bottom', x = 0.5, y = 0, orientation='h'),
                      width = 800, height = 70, plot_bgcolor="rgba(0,0,0,0)",
                      xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False),
                      title = dict(
                      text = f'Date: {date} | Offense: {offense} | Defense: {defense} | Down: {down} | YTG: {yardstogo}', 
                      yanchor="bottom", x=0.5, y=0.05),
                      title_font = dict(size = 12))
    fig2.show(config={'displayModeBar': False})

    # Plot
    tracking_df['color'] = tracking_df.apply(
        lambda row: 'midnightblue' if (row['nflId'] in tacklers) & (row['club'] == defense)
                                 else 'lightsteelblue' if row['club'] == defense
                                 else 'peru' if row['nflId'] == carrier
                                 else 'burlywood' if row['club'] == offense
                                 else 'dimgrey' if row['displayName'] == 'football'
                                 else 'white', axis = 1)   
    
    tracking_df['size'] = tracking_df.apply(
        lambda row: 18 if (row['nflId'] in tacklers) & (row['club'] == defense)
                                 else 15 if row['club'] == defense
                                 else 18 if row['nflId'] == carrier
                                 else 15 if row['club'] == offense
                                 else 15 if row['displayName'] == 'football'
                                 else 0, axis = 1)       
    
    frames = tracking_df['frameId'].unique().tolist()
    events = tracking_df[['frameId','event']].drop_duplicates()
    if tracking_df.at[0, 'playDirection'] == 'left':
        tgline = ablos - yardstogo
    elif tracking_df.at[0, 'playDirection'] == 'right':
        tgline = ablos + yardstogo
    else: tgline = None

    fig = plot_field(min(tracking_df['x'])-10, max(tracking_df['x'])+10, ablos, tgline)
    
    for frame in frames:
        sub1 = tracking_df[(tracking_df['frameId'] == frame) & (tracking_df['displayName'] != 'football')]
        fig.add_trace(
            go.Scatter(
                visible=False,
                x=sub1['x'], y=sub1['y'], mode='markers', showlegend = False,
                hovertext = sub1['displayName'],
                hovertemplate = f'%{{hovertext}}',
                marker=dict(symbol='arrow', size=sub1['size'], angle=sub1['o'], color = sub1['color'])))
        sub2 = tracking_df[(tracking_df['frameId'] == frame) & (tracking_df['displayName'] == 'football')]
        fig.add_trace(
            go.Scatter(
                visible=False,
                x=sub2['x'], y=sub2['y'], mode='markers', showlegend = False,
                marker=dict(size=8, color = sub2['color'])))

    fig.data[0].visible = True
    fig.data[1].visible = True

    visibility = []
    for i in range(len(frames)):
        event = events[events['frameId'] == i+1]['event'].reset_index().at[0,'event']
        frame_viz = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                  {"title": f"Event: {event}", 'font': {'size':10}}],
            label = f'frame{i+1}'
        )
        frame_viz["args"][0]["visible"][i*2] = True
        frame_viz["args"][0]["visible"][i*2+1] = True
        visibility.append(frame_viz)

    sliders = [dict(
        active=0, steps=visibility, font=dict(size=10)
    )]

    fig.update_layout(title=dict(yanchor = 'top', x=0.5, y=0.98),
                     title_font = dict(size= 12))

    fig.update_layout(
        sliders=sliders, 
        width=800, height=600,
        margin=dict(t=20)
    )
    fig.update_layout(dragmode=False)
    fig.show(config={'displayModeBar': False})