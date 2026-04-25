"""Main entry point for the Fincept Terminal application.

This module initializes and launches the terminal UI, sets up
the application configuration, and orchestrates the main event loop.
"""

import sys
import os
from pathlib import Path


def get_app_dir() -> Path:
    """Return the application data directory, creating it if necessary."""
    app_dir = Path.home() / ".fincept_terminal"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def check_dependencies() -> bool:
    """Verify that required runtime dependencies are available."""
    required = ["textual", "rich", "httpx"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(
            f"[ERROR] Missing required packages: {', '.join(missing)}\n"
            f"Install them with: pip install {' '.join(missing)}"
        )
        return False
    return True


def setup_logging(debug: bool = False) -> None:
    """Configure application-level logging.

    Args:
        debug: If True, set log level to DEBUG; otherwise INFO.
    """
    import logging

    log_level = logging.DEBUG if debug else logging.INFO
    log_file = get_app_dir() / "fincept.log"

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def parse_args():
    """Parse command-line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="fincept",
        description="Fincept Terminal — Financial data & analytics in your terminal.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug logging.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        default=False,
        help="Print version and exit.",
    )
    return parser.parse_args()


def run() -> None:
    """Primary entry point invoked by the console script."""
    args = parse_args()

    if args.version:
        from fincept_terminal import __version__
        print(f"Fincept Terminal v{__version__}")
        sys.exit(0)

    if not check_dependencies():
        sys.exit(1)

    setup_logging(debug=args.debug)

    import logging
    logger = logging.getLogger(__name__)
    logger.info("Starting Fincept Terminal...")

    try:
        # Deferred import so startup errors surface cleanly
        from fincept_terminal.app import FinceptApp
        app = FinceptApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Session terminated by user.")
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled exception during startup: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    run()
