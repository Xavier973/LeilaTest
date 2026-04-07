import os


bind = os.getenv("GUNICORN_BIND", "127.0.0.1:8100")
workers = int(os.getenv("GUNICORN_WORKERS", "3"))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))
reload = os.getenv("GUNICORN_RELOAD", "false").strip().lower() in {"1", "true", "yes", "on"}
accesslog = "-"
errorlog = "-"
capture_output = True
