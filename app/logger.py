import logging
import os
from logging.handlers import SocketHandler
from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def setup_loki_logger(name: str, loki_url: str = None, service_name: str = None):
    """
    Configure a logger that sends logs to Loki.
    
    Args:
        name: Logger name
        loki_url: Loki endpoint URL (default: http://loki-gateway.loki.svc.cluster.local)
        service_name: Service name for Loki tags (default: from SERVICE_NAME env var or 'fastapi-app')
    
    Returns:
        Configured logger instance
    """
    if loki_url is None:
        loki_url = os.getenv("LOKI_URL", "http://loki-gateway.loki.svc.cluster.local")
    
    if service_name is None:
        service_name = os.getenv("SERVICE_NAME", "fastapi-app")
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Add service_name to all log records
    class ServiceNameFilter(logging.Filter):
        def filter(self, record):
            record.service_name = service_name
            return True
    
    service_filter = ServiceNameFilter()
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.addFilter(service_filter)
    json_formatter = jsonlogger.JsonFormatter(
        fmt='%(timestamp)s %(level)s %(name)s %(message)s %(service_name)s'
    )
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    # Loki handler (requires loki-logger-handler or similar)
    try:
        from loki_logger_handler import LokiLoggerHandler
        
        # Build headers
        headers = {
            "Content-Type": "application/json",
            "X-Scope-OrgID": os.getenv("LOKI_ORG_ID", "default"),
        }
        
        # Add authorization header if provided
        loki_auth = os.getenv("LOKI_AUTH")
        if loki_auth:
            headers["Authorization"] = f"Bearer {loki_auth}"
        
        loki_handler = LokiLoggerHandler(
            url=f"{loki_url}/loki/api/v1/push",
            tags={"app": service_name, "environment": os.getenv("ENVIRONMENT", "dev"), "service": service_name},
            auth=None,  # Add auth if needed: (username, password)
            headers=headers,
        )
        loki_handler.setLevel(logging.INFO)
        loki_handler.addFilter(service_filter)
        loki_handler.setFormatter(json_formatter)
        logger.addHandler(loki_handler)
    except ImportError:
        logger.warning("loki-logger-handler not installed. Install with: pip install loki-logger-handler")
    
    return logger
