""" This is a configuration file for Pytest. It sets up the environment before any tests run. """

import sys
import os
import pytest
from unittest.mock import MagicMock

# Add the parent directory to Python system's path so we can import 'src'.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# If any code tries to import fluidsynth, it doesn't look for the real library. It gives them this fake MagicMock object instead."
sys.modules["fluidsynth"] = MagicMock()

# Decorates the function so it can be injected into test functions as an argument.
@pytest.fixture

# Returns an AudioEngine instance with a mocked synth.
def mock_audio_engine():
    from src.audio_engine import AudioEngine

    # Creates an instance.
    engine = AudioEngine()

    # Manually replaces the fs (synthesizer) attribute with a mock, just to be double-sure.
    engine.fs = MagicMock()

    # passes this safe engine to any test that asks for mock_audio_engine.
    return engine