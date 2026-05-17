"""Gunicorn configuration for production.

Bind to the port DigitalOcean App Platform provides via $PORT,
falling back to 5002 for local production-mode testing.
"""
import os
import multiprocessing

bind = f"0.0.0.0:{os.environ.get('PORT', '5002')}"

# Workers: (2 * CPU) + 1 is the standard Gunicorn recommendation
workers = int(os.environ.get("WEB_CONCURRENCY", (multiprocessing.cpu_count() * 2) + 1))
threads = int(os.environ.get("WEB_THREADS", 2))
worker_class = os.environ.get("WORKER_CLASS", "sync")

# Time out long-running PDF generations gracefully
timeout = int(os.environ.get("WEB_TIMEOUT", 120))
graceful_timeout = 30
keepalive = 5

# Log to stdout/stderr so DO captures them
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info")
