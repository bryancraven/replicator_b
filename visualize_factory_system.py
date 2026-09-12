#!/usr/bin/env python3
"""Backward-compatible shim for visualization."""

from factory_simulator.visualize import *  # noqa: F401,F403
from factory_simulator.visualize import main

if __name__ == "__main__":
    main()
