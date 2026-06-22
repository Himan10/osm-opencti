import os

import yaml
from pycti import get_config_variable


class ConfigConnector:
    """Loads connector configuration from config.yml and/or environment variables.

    Environment variables take precedence over config.yml so the connector can be
    driven entirely from docker-compose without a config file.
    """

    def __init__(self):
        config_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.yml"
        )
        config = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )
        self._load(config)

    def _load(self, config):
        # OpenCTI connection is read by the OpenCTIConnectorHelper directly,
        # we only need the source-specific settings here.
        self.api_base_url = get_config_variable(
            "OPENSOURCEMALWARE_API_BASE_URL",
            ["opensourcemalware", "api_base_url"],
            config,
            default="https://api.opensourcemalware.com/functions/v1",
        )
        self.api_token = get_config_variable(
            "OPENSOURCEMALWARE_API_TOKEN",
            ["opensourcemalware", "api_token"],
            config,
        )

        ecosystems = get_config_variable(
            "OPENSOURCEMALWARE_ECOSYSTEMS",
            ["opensourcemalware", "ecosystems"],
            config,
            default="npm,pypi",
        )
        # Accept a comma-separated string or a YAML list.
        if isinstance(ecosystems, str):
            ecosystems = [e.strip() for e in ecosystems.split(",")]
        self.ecosystems = [e for e in ecosystems if e]

        self.label = get_config_variable(
            "OPENSOURCEMALWARE_LABEL",
            ["opensourcemalware", "label"],
            config,
            default="opensourcemalware",
        )
        self.verified_only = get_config_variable(
            "OPENSOURCEMALWARE_VERIFIED_ONLY",
            ["opensourcemalware", "verified_only"],
            config,
            default=True,
        )
