"""
LEILA Transport Dashboard
=========================
Lancer : python app.py
Accès  : http://127.0.0.1:8100
"""

from dash_app import app
import layout    # noqa: F401 — définit app.layout
import callbacks  # noqa: F401 — enregistre les callbacks
from data import df

if __name__ == "__main__":
    print("=" * 55)
    print("  LEILA Transport Dashboard")
    print(f"  {len(df)} missions chargées depuis MariaDB")
    print("  http://127.0.0.1:8100")
    print("=" * 55)
    app.run(debug=True, host="127.0.0.1", port=8100)
