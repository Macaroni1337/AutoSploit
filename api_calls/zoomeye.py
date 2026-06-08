import requests

from lib.settings import start_animation
from lib.errors import AutoSploitAPIConnectionError
from lib.settings import (
    API_URLS,
    HOST_FILE,
    write_to_file
)

# ZoomEye v2 host search uses a personal API key — no username/password login
# required.  The key is stored in etc/tokens/zoomeye.key and loaded by
# lib.settings.load_api_keys() the same way as Shodan.
#
# The old approach used hardcoded base64-encoded shared credentials
# (users.lst / passes.lst).  Those files are kept in the repo for historical
# reference but are no longer read by this module.


class ZoomEyeAPIHook(object):

    """
    ZoomEye API hook — v2 host search, API-key authentication.
    """

    def __init__(self, token=None, query=None, proxy=None, agent=None, save_mode=None, **kwargs):
        self.token = token
        self.query = query
        self.host_file = HOST_FILE
        self.proxy = proxy
        self.user_agent = agent
        self.save_mode = save_mode

    def search(self):
        """
        Connect to the ZoomEye v2 API and collect all IP addresses matching
        the provided query.
        """
        start_animation("searching ZoomEye with given query '{}'".format(self.query))
        discovered_zoomeye_hosts = set()
        try:
            headers = {"API-KEY": self.token}
            if self.user_agent:
                headers["User-Agent"] = self.user_agent.get("User-Agent", "")

            params = {"query": self.query, "page": 1}
            req = requests.get(
                API_URLS["zoomeye"],
                params=params,
                headers=headers,
                proxies=self.proxy,
            )
            req.raise_for_status()
            json_data = req.json()

            for item in json_data.get("matches", []):
                ip = item.get("ip")
                if ip:
                    discovered_zoomeye_hosts.add(str(ip))

            write_to_file(discovered_zoomeye_hosts, self.host_file, mode=self.save_mode)
            return True
        except requests.HTTPError as e:
            raise AutoSploitAPIConnectionError(
                "ZoomEye API error (HTTP {}): {}".format(e.response.status_code, e)
            )
        except Exception as e:
            raise AutoSploitAPIConnectionError(str(e))
