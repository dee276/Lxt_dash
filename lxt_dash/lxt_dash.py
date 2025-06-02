from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_ag_grid as dag
import sqlite3

#connecting to the database
conn = sqlite3.connect("employee.db")
cursor = conn.cursor()
commit = conn.commit()
rollback = conn.rollback()

#variable DataFrame pour les tables "transcripteurs" et "resultats"
df_tr = pd.read_sql_query("select * from transcripteurs",conn)
df_res = pd.read_sql_query("select * from resultats",conn) 

#variable trié par langue
df_fr = df_tr[df_tr['langue']=='Francais']
df_aus = df_tr[df_tr['langue']=='Aus-Eng']
df_indo = df_tr[df_tr['langue']=='Indo']
df_ko = df_tr[df_tr['langue']=='Korean']
df_cmn_t = df_tr[df_tr['langue']=='CMN-Tai']
df_lao = df_tr[df_tr['langue']=='Laos']

#liste des langues
langues = df_tr["langue"].unique()

#Alternative pour filtrer plusieurs langues, à intégrer dans un callback dans une version ultérieure
#df_multi = df[df['langue'].isin(['Français', 'Anglais'])]


app = Dash()

app.layout = html.Div([
    html.H2("Tableau des transcripteurs"),
    dcc.Tabs(
        id = "tabs-langue",
        value = langues[0],
        children = [
            dcc.Tab(label=langue, value=langue) for langue in langues
            ]
        ),
    html.Div(id = "tableau-langue"),
    html.Div(id = "graph-transcripteur"),
    html.Div(id = "graph-comparatif")

    ])


@callback(
        Output("tableau-langue","children"),
        Input("tabs-langue","value")
        )
def afficher_tableau(langue_choisie):
    df_filtré = df_tr[df_tr["langue"] == langue_choisie].drop(columns=["page_id"])
    return dag.AgGrid(
        id=f"grid-{langue_choisie}",
        rowData=df_filtré.to_dict("records"),
        columnDefs=[{"field": col} for col in df_filtré.columns],
        columnSize="sizeToFit",
        defaultColDef={"sortable": True, "filter": True, "resizable": True},
        style={"height": "400px", "width": "100%"}
    )

@callback(
        Output("graph-transcripteur","children"),
        Input("","value")
        )
def afficher_stat_transcripteur(transcripteur):

if __name__ == '__main__':
    app.run(debug=True)
