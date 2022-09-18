"""Python logging config

  env_variables:
    LOG_CONFIG - a path to configuration file
"""

import os
import logging.config

import yaml

with open(os.environ.get("LOG_CONFIG", "log_settings.yaml"), "rb") as file:
  log_config = yaml.safe_load(file)

logging.config.dictConfig(log_config)
del log_config
