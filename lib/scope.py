"""
Authorisation gate and target-scope validator.

All exploitation runs must pass through confirm_authorization() before any
module fires.  If a scope file is supplied via --scope, only hosts within
the defined networks will be targeted; everything else is skipped with a
warning rather than silently dropped.
"""

import ipaddress


def confirm_authorization(hosts):
    """
    Require the operator to explicitly confirm written authorisation before
    exploitation begins.  The operator must type the exact phrase shown;
    anything else aborts.

    :param hosts: iterable of target host strings used in the warning banner
    :returns: True only if the operator confirms
    """
    print(
        "\n\033[1m\033[31m[!] AUTHORISATION REQUIRED\033[0m\n"
        "    You are about to launch exploitation modules against {} target(s).\n"
        "    Unauthorised access to computer systems is a criminal offence.\n"
        "    Only proceed if you hold WRITTEN authorisation for every target listed.\n".format(len(list(hosts)))
    )
    answer = input(
        "[\033[1m\033[31m!\033[0m] Type 'I HAVE WRITTEN AUTHORISATION' to continue"
        " (anything else aborts): "
    )
    return answer.strip() == "I HAVE WRITTEN AUTHORISATION"


def load_scope(scope_file):
    """
    Load a scope definition file.  Each line may be a single IP address or a
    CIDR range (e.g. 10.0.0.0/8).  Lines starting with '#' are comments.

    :param scope_file: path to the scope file
    :returns: list of ipaddress.ip_network objects
    """
    allowed = []
    with open(scope_file) as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                allowed.append(ipaddress.ip_network(line, strict=False))
            except ValueError as exc:
                print(
                    "[\033[1m\033[33m-\033[0m] Skipping invalid scope entry '{}': {}".format(line, exc)
                )
    return allowed


def ip_in_scope(ip, scope):
    """
    Return True if *ip* falls within any network listed in *scope*.
    If *scope* is empty (no --scope flag supplied), all hosts are in scope.

    :param ip: string IP address
    :param scope: list of ipaddress.ip_network objects from load_scope()
    :returns: bool
    """
    if not scope:
        return True
    try:
        addr = ipaddress.ip_address(ip.strip())
        return any(addr in network for network in scope)
    except ValueError:
        # Non-IP targets (hostnames) are passed through; nmap will resolve them
        return True
