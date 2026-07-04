import logging
import sys

def initialize_production_telemetry():
    """
    📊 Configures structured telemetry logs perfect for local terminal debugging.
    """
    logger = logging.getLogger("amity_helpdesk")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        enterprise_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(enterprise_formatter)
        logger.addHandler(console_handler)
        
    return logger

logger = initialize_production_telemetry()