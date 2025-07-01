from dash import Dash, html, dcc, callback, Output, Input, MATCH, ALL
import plotly.express as px
import pandas as pd
import dash_ag_grid as dag
import sqlite3

# Connexion à la base de données
conn = sqlite3.connect("employee.db")
df_tr = pd.read_sql_query("SELECT * FROM transcripteurs", conn)
df_res = pd.read_sql_query("SELECT * FROM resultats_journaliers", conn)

# Liste des langues uniques
langues = df_tr["langue"].unique()

# Initialisation de l'app Dash
app = Dash()

# Layout de l'application
app.layout = html.Div([
    html.H2("Tableau des transcripteurs"),

    dcc.Tabs(
        id="tabs-langue",
        value=langues[0],
        children=[dcc.Tab(label=langue, value=langue) for langue in langues]
    ),

    html.Div(id="tableau-langue"),
    html.Hr(),
    html.Div(id="graph-transcripteur")
])


# Callback pour afficher les transcripteurs selon la langue
@callback(
    Output("tableau-langue", "children"),
    Input("tabs-langue", "value")
)
def afficher_tableau(langue_choisie):
    df_filtré = df_tr[df_tr["langue"] == langue_choisie].drop(columns=["page_id"], errors="ignore")

    return dag.AgGrid(
        id={"type": "grid", "index": langue_choisie},
        rowData=df_filtré.to_dict("records"),
        columnDefs=[{"field": col} for col in df_filtré.columns],
        columnSize="sizeToFit",
        defaultColDef={"sortable": True, "filter": True, "resizable": True},
        dashGridOptions={"rowSelection": "single"},
        style={"height": "400px", "width": "100%"}
    )


# Callback pour générer les graphiques à partir de la sélection
@callback(
    Output("graph-transcripteur", "children"),
    Input({"type": "grid", "index": ALL}, "selectedRows"),
    prevent_initial_call=True
)
def afficher_stat_transcripteur(selected_rows_all):
    for selected_rows in selected_rows_all:
        if selected_rows and len(selected_rows) > 0:
            transcripteur_id = selected_rows[0].get("id")
            nom = selected_rows[0].get("nom", "")
            break
    else:
        return html.Div("Aucun transcripteur sélectionné.")

    # Filtrer les résultats journaliers
    df_filtré = df_res[df_res["transcripteur_id"] == transcripteur_id].copy()
    if df_filtré.empty:
        return html.Div("Aucune donnée disponible pour ce transcripteur.")

    # Convertir 'jour' en datetime
    df_filtré["jour"] = pd.to_datetime(df_filtré["jour"])

    # Grouper par semaine (chaque lundi)
    df_filtré["semaine"] = df_filtré["jour"].dt.to_period("W").apply(lambda r: r.start_time)

    # Moyennes hebdomadaires
    df_grp = df_filtré.groupby("semaine").agg({
        "vitesse_h": "mean",
        "qualite": "mean",
        "productivite": "mean"
    }).reset_index()

    # Générer les graphiques
    figs = []
    for col in ["vitesse_h", "qualite", "productivite"]:
        fig = px.line(
            df_grp, x="semaine", y=col, markers=True,
            title=f"{col.capitalize()} hebdomadaire - {nom or transcripteur_id}"
        )
        figs.append(dcc.Graph(figure=fig))

    return figs


# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)

