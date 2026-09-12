"""Backward-compatible shim."""

from factory_simulator.factory_builder import *  # noqa: F401,F403
from factory_simulator.factory_builder import main

if __name__ == "__main__":
    main()
