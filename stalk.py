"""OS Library, Pathing utils, HTTP Requests"""

from datetime import datetime
from typing import Any
import sys
import requests

import lib.request_token as apiUtils
from lib.logger_config import logger


def request_user(header: dict[str, str], login: str) -> requests.Response:
    """Requests the user data from the 42 API

    Args:
        token (str): _The bearer token for the API request_
        login (str): _The login to query_

    Returns:
        object: _The GET response from https://api.intra.42.fr/v2/users/login_
    """
    return requests.get(
        "https://api.intra.42.fr/v2/users/" + login, headers=header, timeout=5
    )


def print_title(txt: str) -> None:
    """Prints a section title

    Args:
        txt (str): the string to print as a title

    Returns:
        str: txt, made bold
    """
    print("\n------------\n\033[1m" + txt + "\033[0m")


def print_user_info(user: dict[str, Any]) -> None:
    """_Prints the user's informations_

    Args:
        user (dict[str, Any]): _The json object obtained from the API query_
    """
    print(f"{'Name':12} {user['displayname']}")
    print(f"{'Login':12} {user['login']}")
    url = user["url"]
    if isinstance(url, str):
        url = url.replace("https://api.intra.42.fr/v2/", "https://profile.intra.42.fr/")
    print(f"{'Profile':12} {url}")

    i = 0

    cursus = user["cursus_users"]
    level = ""
    while i < len(cursus):
        if cursus[i]["grade"] == "Pisciner":
            level = cursus[i]["level"]
        if cursus[i]["grade"] == "Transcender" or cursus[i]["grade"] == "Cadet":
            level = cursus[i]["level"]
            break
        i += 1
    print(f"{'Level':12} {level}")


def pformat_validated(proj: dict[str, Any]) -> None:
    """
    Prints the formatted line for current projects with the project name
    and the time elapsed since project registration

    Args:
        proj (dict[str, Any]): the object reprenting the user projects
    """
    date = datetime.fromisoformat(proj["marked_at"].replace("Z", ""))
    print(
        f"{proj['project']['name'][:25]:25}",
        f"{proj['final_mark']:^10}",
        f"{date.strftime('%d/%m/%Y'):>10}",
    )


def pformat_current(proj: dict[str, Any], now: datetime) -> None:
    """Prints the formatted line for current projects with the project name
    and the time elapsed since project registration

    Args:
        proj (dict[str, Any]): the object reprenting the user projects
    """
    then = datetime.fromisoformat(proj["created_at"].replace("Z", ""))
    elapsed = (now - then).days
    print(f"{proj['project']['name'][:25]:25}", f"{elapsed:^10}")


def print_current_projects(projects: list[dict[str, Any]]) -> None:
    """Prints the user's current projects

    Args:
        projects (list[dict[str, Any]]): The array of project objects to be
        processed
    """

    print_title("Working on")
    i = 0
    date_now = datetime.now().isoformat()
    now = datetime.fromisoformat(date_now)
    while i < len(projects):
        if projects[i]["marked"] is False:
            pformat_current(projects[i], now)
        i += 1


def print_validated_projects(projects: list[dict[str, Any]]) -> None:
    """Prints the last 10 projects the user validated

    Args:
        projects (list[dict[str, Any]]): The array of project objects to be
        processed
    """

    print_title("Evaluated projects")
    i = 0
    _max = 0
    while i < len(projects) and _max < 10:
        if projects[i]["marked"] is True:
            pformat_validated(projects[i])
            _max += 1
        i += 1


def main() -> int:
    """Entrypoint to the script"""
    if len(sys.argv) < 2:
        logger.warning("Usage: python3 stalk.py <login>")
        return 1

    try:
        login = sys.argv[1]
        logger.info("Attempting to fetch informations for %s", login)
        header = apiUtils.get_authorization_field(0)
        res = request_user(header, login)
        if res.status_code != 200:
            logger.error("Request failed with %s", res.status_code)
            return False
        res_json = res.json()
        if not res_json:
            print("Error: no such login")
            return 1

        print_user_info(res_json)
        print_current_projects(res_json["projects_users"])
        print_validated_projects(res_json["projects_users"])
    except EnvironmentError as e:
        logger.error("%s", e)
        return 1
    return 0


if __name__ == "__main__":
    main()
