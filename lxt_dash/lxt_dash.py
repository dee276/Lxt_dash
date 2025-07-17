from dash import Dash, html, dcc, callback, Output, Input, MATCH, ALL
import plotly.express as px
import pandas as pd
import dash_ag_grid as dag
import sqlite3
import dash_auth

VALID_USERNAME_PASSWORD_PAIRS = {
        'admin':'admin'
        }

# Connexion à la base de données
conn = sqlite3.connect("employee.db")
df_tr = pd.read_sql_query("SELECT * FROM transcripteurs", conn)
df_res = pd.read_sql_query("SELECT * FROM resultats_journaliers", conn)

df_res["jour"] = pd.to_datetime(df_res["jour"])
langues = df_tr["langue"].unique()

app = Dash()
auth = dash_auth.BasicAuth(
        app,
        VALID_USERNAME_PASSWORD_PAIRS
        )


app.layout = html.Div([
    html.H2("Tableau des transcripteurs"),

    dcc.Tabs(
        id="tabs-langue",
        value=langues[0],
        children=[dcc.Tab(label=langue, value=langue) for langue in langues]
    ),

    html.Div(id="tableau-langue"),

    html.Br(),
    html.Div([
        html.Label("Mode d'affichage :"),
        dcc.RadioItems(
            id="mode-affichage",
            options=[
                {"label": "Journalier", "value": "jour"},
                {"label": "Hebdomadaire", "value": "semaine"},
                {"label": "Mensuel", "value": "mois"}
            ],
            value="semaine",
            inline=True
        )
    ]),

    html.Br(),
    html.Label("Plage de dates :"),
    dcc.DatePickerRange(
        id="filtre-dates",
        start_date=df_res["jour"].min(),
        end_date=df_res["jour"].max(),
        display_format="YYYY-MM-DD"
    ),

    html.Hr(),
    html.Div(id="graph-transcripteur")
])


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


@callback(
    Output("graph-transcripteur", "children"),
    Input({"type": "grid", "index": ALL}, "selectedRows"),
    Input("mode-affichage", "value"),
    Input("filtre-dates", "start_date"),
    Input("filtre-dates", "end_date"),
    prevent_initial_call=True
)
def afficher_stat_transcripteur(selected_rows_all, mode, start_date, end_date):
    for selected_rows in selected_rows_all:
        if selected_rows and len(selected_rows) > 0:
            transcripteur_id = selected_rows[0].get("id")
            nom = selected_rows[0].get("nom", "")
            break
    else:
        return html.Div("Aucun transcripteur sélectionné.")

    df_filtré = df_res[df_res["transcripteur_id"] == transcripteur_id].copy()
    if df_filtré.empty:
        return html.Div("Aucune donnée disponible.")

    df_filtré["jour"] = pd.to_datetime(df_filtré["jour"])

    # Appliquer le filtre de dates
    if start_date and end_date:
        df_filtré = df_filtré[
            (df_filtré["jour"] >= pd.to_datetime(start_date)) &
            (df_filtré["jour"] <= pd.to_datetime(end_date))
        ]

    if df_filtré.empty:
        return html.Div("Aucune donnée dans cette plage.")

    # Appliquer le regroupement
    if mode == "jour":
        df_filtré["periode"] = df_filtré["jour"]
    elif mode == "semaine":
        df_filtré["periode"] = df_filtré["jour"].dt.to_period("W").apply(lambda r: r.start_time)
    elif mode == "mois":
        df_filtré["periode"] = df_filtré["jour"].dt.to_period("M").astype(str)
    else:
        df_filtré["periode"] = df_filtré["jour"]

    df_grp = df_filtré.groupby("periode").agg({
        "vitesse_h": "mean",
        "qualite": "mean",
        "productivite": "mean"
    }).reset_index()

    figs = []
    for col in ["vitesse_h", "qualite", "productivite"]:
        fig = px.line(
            df_grp, x="periode", y=col, markers=True,
            title=f"{col.capitalize()} - {mode} - {nom or transcripteur_id}"
        )
        figs.append(dcc.Graph(figure=fig))

    # 4e graphique — Comparaison avec la moyenne de la langue
    langue_transcripteur = df_tr[df_tr["id"] == transcripteur_id]["langue"].values[0]

    df_langue = df_res[
        (df_res["jour"] >= pd.to_datetime(start_date)) &
        (df_res["jour"] <= pd.to_datetime(end_date))
    ]
    df_langue = df_langue.merge(df_tr[["id", "langue"]], left_on="transcripteur_id", right_on="id")
    df_langue = df_langue[df_langue["langue"] == langue_transcripteur]

    moy_tr = df_filtré[["vitesse_h", "qualite", "productivite"]].mean()
    moy_langue = df_langue[["vitesse_h", "qualite", "productivite"]].mean()

    df_comp = pd.DataFrame({
        "Métrique": ["Vitesse", "Qualité", "Productivité"],
        nom or str(transcripteur_id): [moy_tr["vitesse_h"], moy_tr["qualite"], moy_tr["productivite"]],
        f"Moyenne ({langue_transcripteur})": [moy_langue["vitesse_h"], moy_langue["qualite"], moy_langue["productivite"]]
    })

    fig_comp = px.bar(
        df_comp, x="Métrique", barmode="group",
        y=[nom or str(transcripteur_id), f"Moyenne ({langue_transcripteur})"],
        title="Comparaison : Transcripteur vs Moyenne de la langue"
    )

    figs.append(dcc.Graph(figure=fig_comp))

    return figs


#if __name__ == '__main__':
#    app.run(debug=True)


#new import
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)

#end of import
