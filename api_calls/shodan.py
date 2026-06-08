import shodan

from lib.settings import start_animation
from lib.errors import AutoSploitAPIConnectionError
from lib.settings import (
    HOST_FILE,
    write_to_file
)


class ShodanAPIHook(object):

    """
    Shodan API hook using the official shodan Python library (pip install shodan).
    Replaces the previous raw-HTTP implementation for Python 3 compatibility and
    to gain access to the library's built-in error handling and pagination.
    """

    def __init__(self, token=None, query=None, proxy=None, agent=None, save_mode=None, **kwargs):
        self.token = token
        self.query = query
        self.proxy = proxy
        self.user_agent = agent
        self.host_file = HOST_FILE
        self.save_mode = save_mode

    def search(self):
        """
        Connect to the Shodan API via the official library and collect all IP
        addresses that match the provided query.
        """
        start_animation("searching Shodan with given query '{}'".format(self.query))
        discovered_shodan_hosts = set()
        try:
            api = shodan.Shodan(self.token)
            results = api.search(self.query)
            for match in results["matches"]:
                discovered_shodan_hosts.add(match["ip_str"])
            write_to_file(discovered_shodan_hosts, self.host_file, mode=self.save_mode)
            return True
        except shodan.APIError as e:
            raise AutoSploitAPIConnectionError(str(e))
        except Exception as e:
            raise AutoSploitAPIConnectionError(str(e))
