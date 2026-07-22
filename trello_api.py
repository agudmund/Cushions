#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-Cushions - trello_api.py proper cozy TrelloAPI utility class
-The last of the Trello couriers carried the cards to the cloud and back without dropping one, For Enjoying
-Built using a single shared braincell by Yours Truly and various Intelligences
"""
# (First stitched together with Grok, in the cozy era.)

import requests
from typing import Optional, Tuple
from pathlib import Path

from PySide6.QtCore import QThread

from utils.logging import AppLogger
from utils.settings import Settings

from cozy.worker import UploadWorker


class TrelloAPI:
    """Beautiful TrelloAPI class — clean, reusable, and full of cozy warmth 🌱"""

    def __init__(self, api_key: str, token: str):
        """🌱 Validates credentials on creation — both presence and real API test"""
        if not api_key or not token:
            raise ValueError("Trello API keys missing. Please add them in Settings.")

        self.api_key = api_key
        self.token = token
        self.logger = AppLogger.get()

        # Real credentials test — gentle but thorough
        if not self.verify_credentials():
            raise ValueError(
                "Invalid Trello API credentials. "
                "Please double-check your key and token in Settings ✨"
            )

        self.logger.info("TrelloAPI initialized with valid credentials 🌱") 

    @classmethod
    def from_settings(cls) -> "TrelloAPI":
        """Gentle factory — now even lighter because validation lives in __init__"""
        api_key, token = Settings.get_trello_creds()
        return cls(api_key, token)

    def verify_credentials(self) -> bool:
        """Check if the provided API key and token are valid with Trello."""
        url = "https://api.trello.com/1/members/me"
        params = {'key': self.api_key, 'token': self.token}
        try:
            response = requests.get(url, params=params, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_board_by_name(self, board_name: str) -> Optional[Tuple[str, str]]:
        """🌱 Gentle lookup: returns (id, shortUrl) of first board with exact matching name, or None"""
        url = "https://api.trello.com/1/members/me/boards"
        params = {
            'key': self.api_key,
            'token': self.token,
            'fields': 'id,name,shortUrl'
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            boards = response.json()
            for board in boards:
                if board.get('name') == board_name:
                    return board['id'], board['shortUrl']
            return None
        except requests.RequestException as e:
            self.logger.warning(f"Could not fetch boards list: {e}")
            return None  # safe fallback — will create new

    def create_board(self, board_name: str = "Cozy Times 🌱") -> Tuple[str, str]:
        """Create a new Trello board, OR reuse existing one with the same name 🌱"""
        # ✨ First check if we already have this cozy board
        existing = self.get_board_by_name(board_name)
        if existing:
            board_id, board_url = existing
            self.logger.info(f"Reusing existing board: {board_url} (name: {board_name})")
            return board_id, board_url

        # No match → create fresh board (original lovely logic)
        url = "https://api.trello.com/1/boards/"
        data = {
            'key': self.api_key,
            'token': self.token,
            'name': board_name,
            'defaultLists': 'false',
            'prefs_background': 'blue'
        }
        try:
            response = requests.post(url, data=data, timeout=15)
            response.raise_for_status()
            board = response.json()
            self.logger.info(f"Created new board: {board['shortUrl']}")
            return board['id'], board['shortUrl']
        except requests.RequestException as e:
            self.logger.exception(f"Failed to create Trello board '{board_name}'")
            raise

    @classmethod
    def create_upload_worker(cls, path: str):
        """🌱 Full orchestration + all signal emitting lives here (in TrelloAPI)"""
        def trello_task(worker):
            """The exact chunk you pointed out — now completely self-contained"""
            trello = cls.from_settings()
            created, board_url = trello.upload_markdown_file(
                path,
                progress_callback=worker.progress_updated.emit,
                status_callback=worker.status_updated.emit,
                total_callback=worker.total_updated.emit
            )
            worker.finished.emit(created, board_url)   # finished is emitted from the task, not the worker

        return UploadWorker(trello_task)

    def create_list(self, board_id: str, list_name: str = "Worth Considering") -> str:
        """Create a new list on the board, OR reuse existing one with the same name 🌱"""
        # ✨ First check if we already have this cozy list
        existing_id = self.get_list_by_name(board_id, list_name)
        if existing_id:
            self.logger.info(f"Reusing existing list '{list_name}' on board {board_id}")
            return existing_id

        # No match → create fresh list (original lovely logic)
        url = "https://api.trello.com/1/lists"
        params = {
            'key': self.api_key,
            'token': self.token,
            'name': list_name,
            'idBoard': board_id,
            'pos': 'bottom'
        }
        try:
            response = requests.post(url, params=params, timeout=10)
            response.raise_for_status()
            list_id = response.json()['id']
            self.logger.info(f"Created new list '{list_name}' on board {board_id}")
            return list_id
        except requests.RequestException as e:
            self.logger.exception(f"Failed to create list '{list_name}'")
            raise

    def create_card(self, list_id: str, card_name: str, desc: str) -> bool:
        """Create a single card. Returns True on success."""
        url = "https://api.trello.com/1/cards"
        params = {
            'key': self.api_key,
            'token': self.token,
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

    def get_card_names_in_list(self, list_id: str) -> set[str]:
        """Fetch all current card names in a list for gentle duplicate protection 🌱"""
        url = f"https://api.trello.com/1/lists/{list_id}/cards"
        params = {
            'key': self.api_key,
            'token': self.token,
            'fields': 'name'
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            cards = response.json()
            return {card.get('name', '') for card in cards}
        except requests.RequestException as e:
            self.logger.warning(f"Could not fetch existing card names: {e}")
            return set()  # Safe fallback — better to create than to block

    def upload_paragraphs_to_list(self, list_id: str, paragraphs: list[str], progress_callback=None, status_callback=None) -> int:
        """High-level cozy method that handles the entire paragraph → card loop with smart deduplication 🌱"""
        existing_names = self.get_card_names_in_list(list_id)
        created = 0

        for i, para in enumerate(paragraphs, 1):
            clean_para = para.lstrip('#*-> ').strip()
            first_period = clean_para.find('.')
            first_exclaim = clean_para.find('!')
            first_question = clean_para.find('?')
            stops = [pos for pos in [first_period, first_exclaim, first_question] if pos != -1]

            if stops:
                end_of_sentence = min(stops) + 1
                card_name = clean_para[:end_of_sentence].strip()
            else:
                card_name = clean_para.split('\n')[0][:60].strip()

            if len(card_name) > 120:
                card_name = card_name[:117] + "..."
            if not card_name:
                card_name = f"Note {i}"

            desc = (para[:4000] + "…") if len(para) > 4000 else para

            if card_name in existing_names:
                if status_callback:
                    status_callback(f"Skipped (already exists): {card_name[:30]}...")
                if progress_callback:
                    progress_callback(i)
                QThread.msleep(180)   # gentle for skips
                continue

            self.create_card(list_id, card_name, desc)
            existing_names.add(card_name)
            created += 1

            if progress_callback:
                progress_callback(i)
            if status_callback:
                status_callback(f"Created: {card_name[:30]}...")
            QThread.msleep(600)   # lovely breathing room

        return created

    def upload_markdown_file(self, file_path: Path, progress_callback=None, status_callback=None, total_callback=None) -> Tuple[int, str]:
        """🌱 Complete end-to-end markdown upload: read file → board (reuse) → list → cards with dedup"""
        file_path = Path(file_path)
        text = file_path.read_text(encoding='utf-8').strip()
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        if not paragraphs:
            raise ValueError("File is empty.")

        if total_callback:
            total_callback(len(paragraphs))
        if status_callback:
            status_callback("🌱 Preparing your cozy Trello board...")

        # Board reuse + list + smart card creation
        board_id, board_url = self.create_board()
        todo_id = self.create_list(board_id, "To Review 🌅")

        created = self.upload_paragraphs_to_list(
            todo_id,
            paragraphs,
            progress_callback=progress_callback,
            status_callback=status_callback
        )

        return created, board_url

    def get_list_by_name(self, board_id: str, list_name: str) -> Optional[str]:
        """🌱 Gentle lookup: returns the ID of the first list on the board with exact matching name, or None"""
        url = f"https://api.trello.com/1/boards/{board_id}/lists"
        params = {
            'key': self.api_key,
            'token': self.token,
            'fields': 'id,name'
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            lists = response.json()
            for lst in lists:
                if lst.get('name') == list_name:
                    return lst['id']
            return None
        except requests.RequestException as e:
            self.logger.warning(f"Could not fetch lists on board {board_id}: {e}")
            return None  # safe fallback — will create new