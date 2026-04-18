import logging
import os

ENV = os.getenv("ENV", "dev")

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

def create_logger(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Loki only in prod
    if ENV == "dev":
        try:
            from logging_loki import LokiHandler

            loki_handler = LokiHandler(
                url="http://loki-gateway.loki.svc.cluster.local/loki/api/v1/push",
                tags={
                    "service": service_name,
                    "env": ENV
                },
                version="1",
            )
            loki_handler.setFormatter(formatter)
            logger.addHandler(loki_handler)

            logger.info("Loki logger initialized successfully")

        except Exception as e:
            logger.error(f"Loki init failed: {e}")

    return logger
