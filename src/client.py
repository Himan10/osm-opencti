import requests


class OpenSourceMalwareClient:
    """Thin wrapper around the opensourcemalware.com query-latest endpoint.

    The free API exposes /query-latest, which requires an `ecosystem` query
    parameter and returns the most recent (up to 100) verified threats for it.
    """

    def __init__(self, helper, base_url, api_token):
        self.helper = helper
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_token}",
                "Accept": "application/json",
            }
        )

    def query_latest(self, ecosystem):
        """Return the list of latest threat dicts for an ecosystem (npm, pypi, ...)."""
        url = f"{self.base_url}/query-latest"
        try:
            response = self.session.get(
                url, params={"ecosystem": ecosystem}, timeout=60
            )
            response.raise_for_status()
        except requests.RequestException as err:
            self.helper.connector_logger.error(
                "Error fetching threats from opensourcemalware",
                {"ecosystem": ecosystem, "error": str(err)},
            )
            return []

        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            self.helper.connector_logger.error(
                "API returned an error",
                {"ecosystem": ecosystem, "error": data["error"]},
            )
            return []

        return data.get("threats", []) if isinstance(data, dict) else []
