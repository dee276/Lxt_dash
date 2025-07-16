from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Couleurs LXT
LXT_BLEU = "#005A9C"
LXT_ORANGE = "#F36F21"
LXT_GRIS = "#F8F9FA"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2("Connexion à LXT Analytics", className="text-center mb-4", style={"color": LXT_BLEU}),
                dbc.Input(id="username", placeholder="Nom d'utilisateur", type="text", className="mb-3"),
                dbc.Input(id="password", placeholder="Mot de passe", type="password", className="mb-3"),
                dbc.Button("Se connecter", id="login-button", color="primary", style={"backgroundColor": LXT_ORANGE, "borderColor": LXT_ORANGE}, className="w-100"),
                html.Div(id="login-message", className="mt-3 text-center", style={"color": "red"})
            ], style={
                "backgroundColor": "white",
                "padding": "30px",
                "borderRadius": "8px",
                "boxShadow": "0px 0px 10px rgba(0,0,0,0.1)"
            })
        ], width=12, md=6, lg=4)
    ], justify="center", align="center", style={"height": "100vh", "backgroundColor": LXT_GRIS})
])


@app.callback(
    Output("login-message", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def authentifier(n, user, pwd):
    if user == "admin" and pwd == "secret":
        return "✅ Connexion réussie (à remplacer par une redirection)"
    return "❌ Nom d'utilisateur ou mot de passe incorrect."


if __name__ == "__main__":
    app.run(debug=True)

