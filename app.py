# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 15:07:15 2026

@author: HP
"""

from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px

app = Flask(__name__)

STATIONS = ["3494"]
STATION_INFO = {
    "3494": {
        "receiver": "M720",
        "antenna": "MGW310 NONE",
        "latitude": 26.51,
        "longitude": 80.27,
        "height": 64.33 ,
        "reference_epoch": "2026-08-29"
    }
}

@app.route("/")
def home():
     
    return redirect(url_for("station_page", station="3494"
    ))


@app.route("/station/<station>")
def station_page(station):

    show_graphs = request.args.get("show_graphs") == "1"

    resid_file = f"{station}.resid"

    df = pd.read_csv(
        resid_file,
        sep=r"\s+",
        header=None
    )

    df["east_m"] = df[1]
    df["north_m"] = df[2]
    df["up_m"] = df[3]
    
    df["east_mm"] = df["east_m"] * 1000
    df["north_mm"] = df["north_m"] * 1000
    df["up_mm"] = df["up_m"] * 1000

    df["horizontal_mm"] = (
    df["east_mm"]**2 + df["north_mm"]**2
       ) ** 0.5
    
    horizontal_ok = (df["horizontal_mm"] <= 20).all()
    vertical_ok = (df["up_mm"].abs() <= 30).all()
    
    df["point_status"] = "Within tolerance"

    df.loc[
        (df["horizontal_mm"] > 20) | (df["up_mm"].abs() > 30),
        "point_status"
    ] = "Review required"
    if horizontal_ok and vertical_ok:
        status = "green"
    else:
        status = "yellow"
    
    df["date"] = pd.to_datetime(
        dict(
            year=df[11],
            month=df[12],
            day=df[13]
        )
    )
    
    info = STATION_INFO[station]

    start_date = df["date"].min()
    end_date = df["date"].max()
    
    sigma_e = df["east_mm"].std()
    sigma_n = df["north_mm"].std()
    sigma_u = df["up_mm"].std()

    df["east_mm"] = df["east_m"] * 1000
    df["north_mm"] = df["north_m"] * 1000
    df["up_mm"] = df["up_m"] * 1000

    graph_e = None
    graph_n = None
    graph_u = None

    if show_graphs:
        
        fig_e = px.scatter(
            df,
            x="date",
            y="east_mm",
            color="point_status",
            color_discrete_map={
                "Within tolerance": "green",
                "Review required": "goldenrod"
            }
        )
        
        fig_n = px.scatter(
            df,
            x="date",
            y="north_mm",
            color="point_status",
            color_discrete_map={
                "Within tolerance": "green",
                "Review required": "goldenrod"
            }
        )
        
        fig_u = px.scatter(
            df,
            x="date",
            y="up_mm",
            color="point_status",
            color_discrete_map={
                "Within tolerance": "green",
                "Review required": "goldenrod"
            }
        )

        fig_e.update_yaxes(title="East (mm)")
        fig_n.update_yaxes(title="North (mm)")
        fig_u.update_yaxes(title="Up (mm)")
        
        fig_e.update_xaxes(title="")
        fig_n.update_xaxes(title="")
        fig_u.update_xaxes(title="")
        
        
        for fig in [fig_e, fig_n, fig_u]:

            fig.update_layout(
                height=175,
                margin=dict(l=45, r=10, t=5, b=28),
                plot_bgcolor="white",
                paper_bgcolor="white",
                showlegend=False
            )
        
            fig.update_xaxes(
                title="",
                showgrid=True,
                gridcolor="#dddddd",
                zeroline=False
            )
        
            fig.update_yaxes(
                showgrid=True,
                gridcolor="#dddddd",
                zeroline=True,
                zerolinecolor="#999999"
            )

        fig_e.update_traces(marker=dict(size=6))
        fig_n.update_traces(marker=dict(size=6))
        fig_u.update_traces(marker=dict(size=6))
       
        graph_e = fig_e.to_html(full_html=False)
        graph_n = fig_n.to_html(full_html=False)
        graph_u = fig_u.to_html(full_html=False)

    return render_template(
    "station.html",
    station=station,
    stations=STATIONS,
    info=info,
    start_date=start_date,
    end_date=end_date,
    sigma_e=sigma_e,
    sigma_n=sigma_n,
    sigma_u=sigma_u,
    status=status,
    show_graphs=show_graphs,
    graph_e=graph_e,
    graph_n=graph_n,
    graph_u=graph_u
)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)