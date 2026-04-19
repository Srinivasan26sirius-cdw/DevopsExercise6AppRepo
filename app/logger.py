import logging
import os
import json
from datetime import datetime

ENV = os.getenv("ENV", "prod")
LOKI_URL = os.getenv(
    "LOKI_URL",
    "http://loki-gateway.loki.svc.cluster.local/loki/api/v1/push"
)


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service_name": getattr(record, "service_name", "unknown"),
            "env": ENV
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def create_logger(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    logger.propagate = False

    if logger.handlers:
        return logger

    # Console JSON logs
    console_handler = logging.StreamHandler()
    json_formatter = JSONFormatter()
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    # Add service_name to all records
    for handler in logger.handlers:
        handler.addFilter(
            lambda record: setattr(record, "service_name", service_name) or True
        )

    # Loki handler
    if ENV in ["dev", "prod"]:
        try:
            from logging_loki import LokiHandler

            loki_handler = LokiHandler(
                url=LOKI_URL,
                tags={
                    "service_name": service_name,
                    "app": "fastapi",
                    "env": ENV
                },
                version="1",
            )

            loki_handler.setFormatter(json_formatter)
            logger.addHandler(loki_handler)

            logger.info(f"Loki handler initialized for {service_name}")

        except Exception as e:
            logger.exception(f"Loki initialization failed: {e}")

    return logger