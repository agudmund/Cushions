# utils/trello_api.py
import os
import time
import requests
from typing import Optional, Tuple

from utils.logging import AppLogger


logger = AppLogger.get()


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Retrieve Trello API key and token from environment variables."""
    api_key = os.environ.get("TRELLO_KEY")
    token = os.environ.get("TRELLO_TOKEN")
    api_key = api_key.strip() if api_key else None
    token = token.strip() if token else None

    if not api_key or not token:
        logger.warning("TRELLO_KEY and/or TRELLO_TOKEN environment variables are missing or empty")

    return api_key, token


def create_board(
    api_key: str,
    token: str,
    board_name: str = "Proofreading Kanban 🌱"
) -> Tuple[str, str]:
    """Create a new Trello board and return its ID and short URL."""
    url = "https://api.trello.com/1/boards/"
    data = {
        'key': api_key,
        'token': token,
        'name': board_name,
        'defaultLists': 'false',
        'prefs_background': 'blue'
    }

    try:
        response = requests.post(url, data=data, timeout=15)
        response.raise_for_status()
        board = response.json()
        logger.info(f"Created board: {board['shortUrl']}")
        return board['id'], board['shortUrl']

    except requests.RequestException as e:
        logger.exception(f"Failed to create Trello board '{board_name}'")
        raise


def create_list(
    api_key: str,
    token: str,
    board_id: str,
    list_name: str = "To Review 🌅"
) -> str:
    """Create a new list on the specified board and return its ID."""
    url = "https://api.trello.com/1/lists"
    params = {
        'key': api_key,
        'token': token,
        'name': list_name,
        'idBoard': board_id,
        'pos': 'bottom'
    }

    try:
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        list_id = response.json()['id']
        logger.info(f"Created list '{list_name}' on board {board_id}")
        return list_id

    except requests.RequestException as e:
        logger.exception(f"Failed to create list '{list_name}' on board {board_id}")
        raise


def create_card(
    api_key: str,
    token: str,
    list_id: str,
    card_name: str,
    desc: str,
    pos: str = 'bottom'
) -> bool:
    """Create a single card in the specified list. Returns True on success."""
    url = "https://api.trello.com/1/cards"
    params = {
        'key': api_key,
        'token': token,
        'idList': list_id,
        'name': card_name,
        'desc': desc,
        'pos': pos
    }

    try:
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        logger.info(f"Added card: {card_name}")
        return True

    except requests.HTTPError as e:
        logger.warning(f"Failed to create card '{card_name}': {response.status_code} - {response.text}")
        return False

    except requests.RequestException as e:
        logger.exception(f"Network or unexpected error while creating card '{card_name}'")
        return False