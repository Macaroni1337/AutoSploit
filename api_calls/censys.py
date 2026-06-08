import requests

import lib.settings
from lib.errors import AutoSploitAPIConnectionError
from lib.settings import (
    HOST_FILE,
    API_URLS,
    write_to_file
)

# Censys moved from v1 (censys.io/api/v1/search/ipv4) to v2 in 2021.
# v2 uses Basic auth with (API_ID, API_SECRET) and returns paginated results
# via a cursor.  Credentials are stored in:
#   etc/tokens/censys.key  — API secret
#   etc/tokens/censys.id   — API ID


class CensysAPIHook(object):

    """
    Censys API hook — v2 host search.
    """

    def __init__(self, identity=None, token=None, query=None, proxy=None, agent=None, save_mode=None, **kwargs):
        # identity = API ID, token = API Secret (matches the original parameter names)
        self.api_id = identity
        self.api_secret = token
        self.query = query
        self.proxy = proxy
        self.user_agent = agent
        self.host_file = HOST_FILE
        self.save_mode = save_mode

    def search(self):
        """
        Connect to the Censys v2 API and collect all IP addresses matching the
        provided query.  Results are paginated via cursor; collects up to 100
        hits per request (the API maximum).
        """
        lib.settings.start_animation("searching Censys with given query '{}'".format(self.query))
        discovered_censys_hosts = set()
        try:
            params = {"q": self.query, "per_page": 100}
            req = requests.get(
                API_URLS["censys"],
                params=params,
                auth=(self.api_id, self.api_secret),
                headers=self.user_agent,
                proxies=self.proxy,
            )
            req.raise_for_status()
            json_data = req.json()

            hits = json_data.get("result", {}).get("hits", [])
            for item in hits:
                ip = item.get("ip")
                if ip:
                    discovered_censys_hosts.add(str(ip))

            write_to_file(discovered_censys_hosts, self.host_file, mode=self.save_mode)
            return True
        except requests.HTTPError as e:
            raise AutoSploitAPIConnectionError(
                "Censys API error (HTTP {}): {}".format(e.response.status_code, e)
            )
        except Exception as e:
            raise AutoSploitAPIConnectionError(str(e))
