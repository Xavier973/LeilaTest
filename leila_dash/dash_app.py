# ── Instance Dash (importée par layout.py et callbacks.py) ─
# Module séparé pour éviter les imports circulaires
import dash

app = dash.Dash(
    __name__,
    title="LEILA Transport — Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server  # exposé pour un éventuel déploiement WSGI
