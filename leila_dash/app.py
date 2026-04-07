"""
LEILA Transport Dashboard
=========================
Lancer : python app.py
Accès  : http://127.0.0.1:8100
"""

import os

from dash_app import app, server
import layout    # noqa: F401 — définit app.layout
import callbacks  # noqa: F401 — enregistre les callbacks
from data import df

if __name__ == "__main__":
    host = os.getenv("LEILA_HOST", "127.0.0.1")
    port = int(os.getenv("LEILA_PORT", "8100"))
    debug = os.getenv("LEILA_DEBUG", "true").strip().lower() in {"1", "true", "yes", "on"}

    print("=" * 55)
    print("  LEILA Transport Dashboard")
    print(f"  {len(df)} missions chargées depuis MariaDB")
    print(f"  http://{host}:{port}")
    print("=" * 55)
    app.run(debug=debug, host=host, port=port)
