# Gunicorn configuration for Render
import multiprocessing

# Bind to port
bind = "0.0.0.0:8000"

# Worker settings
workers = 2  # Reduced for memory
worker_class = "sync"
timeout = 120  # Increased timeout
graceful_timeout = 30
max_requests = 1000
max_requests_jitter = 100

# Memory management
worker_connections = 1000
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
