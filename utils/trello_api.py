# utils/trello_api.py
import requests
from typing import Tuple
from utils.logging import AppLogger

logger = AppLogger.get()

def verify_credentials(api_key: str, token: str) -> bool:
    """Check if the provided API key and token are valid with Trello."""
    url = "https://api.trello.com/1/members/me"
    params = {'key': api_key, 'token': token}
    try:
        response = requests.get(url, params=params, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def create_board(api_key: str, token: str, board_name: str = "Proofreading Kanban 🌱") -> Tuple[str, str]:
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

def create_list(api_key: str, token: str, board_id: str, list_name: str = "To Review 🌅") -> str:
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
        return response.json()['id']
    except requests.RequestException as e:
        logger.exception(f"Failed to create list '{list_name}'")
        raise

def create_card(api_key: str, token: str, list_id: str, card_name: str, desc: str) -> bool:
    """Create a single card. Returns True on success."""
    url = "https://api.trello.com/1/cards"
    params = {
        'key': api_key,
        'token': token,
        'idList': list_id,
        'name': card_name,
        'desc': desc,
        'pos': 'bottom'
    }
    try:
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False