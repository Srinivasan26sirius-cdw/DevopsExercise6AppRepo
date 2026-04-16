import logging
import os
from logging.handlers import SocketHandler
from pythonjsonlogger import jsonlogger


def setup_loki_logger(name: str, loki_url: str = None):
    """
    Configure a logger that sends logs to Loki.
    
    Args:
        name: Logger name
        loki_url: Loki endpoint URL (default: http://loki-gateway.loki.svc.cluster.local)
    
    Returns:
        Configured logger instance
    """
    if loki_url is None:
        loki_url = os.getenv("LOKI_URL", "http://loki-gateway.loki.svc.cluster.local")
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s'
    )
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    # Loki handler (requires loki-logger-handler or similar)
    try:
        from loki_logger_handler import LokiLoggerHandler
        
        loki_handler = LokiLoggerHandler(
            url=f"{loki_url}/loki/api/v1/push",
            tags={"app": "fastapi-app", "environment": os.getenv("ENVIRONMENT", "dev")},
            auth=None,  # Add auth if needed: (username, password)
        )
        loki_handler.setLevel(logging.INFO)
        loki_handler.setFormatter(json_formatter)
        logger.addHandler(loki_handler)
    except ImportError:
        logger.warning("loki-logger-handler not installed. Install with: pip install loki-logger-handler")
    
    return logger
