#!/usr/bin/env python3
"""Backward-compatible shim for analysis dashboard."""

from factory_simulator.analyze import *  # noqa: F401,F403
from factory_simulator.analyze import main

if __name__ == "__main__":
    main()
