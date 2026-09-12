#!/usr/bin/env python3
"""Backward-compatible shim for the main simulation module."""

from factory_simulator.sim import *  # noqa: F401,F403
from factory_simulator.sim import main

if __name__ == "__main__":
    main()
