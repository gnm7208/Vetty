"""Entry point for running the Vetty Flask development server."""

from __future__ import annotations

from . import create_app

app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=5555, debug=True)
