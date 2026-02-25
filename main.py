#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Cushions - main.py
# The cozy hybrid Python + .NET MAUI creation that magically turns late-night markdown rambles
# into beautiful, well-organized Trello boards!
# Built using a single shared braincell by Yours Truly and Grok

import sys
import os
from PySide6.QtWidgets import QApplication
from main_window import CushionsWindow
from utils.logging import setup_logging

APP_NAME = "Cushions"
APP_VERSION = "0.1.1"
DEBUG_MODE = os.getenv("COZY_DEBUG", "1") == "1"

def main() -> None:
    logger = setup_logging(debug=DEBUG_MODE)
    try:
        logger.info(f"{APP_NAME} launched (debug mode: {DEBUG_MODE})")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setApplicationName(APP_NAME)
        app.setOrganizationName("Single Shared Braincell")
        app.setApplicationVersion(APP_VERSION)
        window = CushionsWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.critical(f"Starting {APP_NAME} catastrophically failed", exc_info=True)
        print(f"{APP_NAME} has entered the void: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()