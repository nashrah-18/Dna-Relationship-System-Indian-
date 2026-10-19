import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import plotly.graph_objs as go

def generate_cluster_chart(profiles):
    if not profiles:
        return {"data": [], "layout": {"title": "No DNA profiles loaded"}}
    
    data = []
    for p in profiles:
        row = {
            'sample_id': p.sample_id,
            'sex': p.sex,
            'amel': p.amel,
            'd3s1358': p.d3s1358,
            'vwa': p.vwa,
            'd16s539': p.d16s539,
            'csf1po': p.csf1po,
            'tpox': p.tpox,
            'd8s1179': p.d8s1179,
            'd21s11': p.d21s11,
            'd18s51': p.d18s51,
            'dys391': p.dys391,
            'd2s441': p.d2s441,
            'd19s433': p.d19s433,
            'tho1': p.tho1,
            'fga': p.fga,
            'd22s1045': p.d22s1045,
            'd5s818': p.d5s818,
            'd13s317': p.d13s317,
            'd7s820': p.d7s820,
            'se33': p.se33,
            'd10s1248': p.d10s1248,
            'd1s1656': p.d1s1656,
            'd12s391': p.d12s391,
            'd2s1338': p.d2s1338
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    feature_cols = [c for c in df.columns if c not in ['sample_id', 'sex']]
    X = df[feature_cols].fillna(0).values
    
    if len(X) < 2:
        return {"data": [], "layout": {"title": "Need at least 2 samples for clustering"}}
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    pca = PCA(n_components=2)
    components = pca.fit_transform(X_scaled)
    
    trace = go.Scatter(
        x=components[:, 0],
        y=components[:, 1],
        mode='markers+text',
        text=df['sample_id'],
        marker=dict(
            size=10,
            color=[0 if sex == 'XX' else 1 for sex in df['sex']],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Sex (0=XX,1=YX)")
        ),
        textposition="top center"
    )
    
    layout = go.Layout(
        title="DNA Profile PCA Clustering",
        xaxis=dict(title="PC1"),
        yaxis=dict(title="PC2"),
        hovermode='closest'
    )
    
    fig = go.Figure(data=[trace], layout=layout)
    return fig.to_dict()