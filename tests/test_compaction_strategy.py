import configparser
import os
import tempfile
from unittest.mock import patch

from ticca.config import (
    CONFIG_DIR,
    CONFIG_FILE,
    DEFAULT_SECTION,
    get_compaction_strategy,
)


def test_default_compaction_strategy():
    """Test that the default compaction strategy is truncation"""
    with patch("ticca.config.get_value") as mock_get_value:
        mock_get_value.return_value = None
        strategy = get_compaction_strategy()
        assert strategy == "truncation"


def test_set_compaction_strategy_truncation():
    """Test that we can set the compaction strategy to truncation"""
    # Create a temporary config directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        original_config_dir = CONFIG_DIR
        original_config_file = CONFIG_FILE

        # Monkey patch the config directory
        import ticca.config

        ticca.config.CONFIG_DIR = temp_dir
        ticca.config.CONFIG_FILE = os.path.join(temp_dir, "puppy.cfg")

        # Create the config file with truncation strategy
        config = configparser.ConfigParser()
        config[DEFAULT_SECTION] = {}
        config[DEFAULT_SECTION]["compaction_strategy"] = "truncation"

        # Write the config
        with open(ticca.config.CONFIG_FILE, "w") as f:
            config.write(f)

        # Test that the strategy is read correctly
        strategy = get_compaction_strategy()
        assert strategy == "truncation"

        # Reset the config directory
        ticca.config.CONFIG_DIR = original_config_dir
        ticca.config.CONFIG_FILE = original_config_file


def test_set_compaction_strategy_summarization():
    """Test that we can set the compaction strategy to summarization"""
    # Create a temporary config directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        original_config_dir = CONFIG_DIR
        original_config_file = CONFIG_FILE

        # Monkey patch the config directory
        import ticca.config

        ticca.config.CONFIG_DIR = temp_dir
        ticca.config.CONFIG_FILE = os.path.join(temp_dir, "puppy.cfg")

        # Create the config file with summarization strategy
        config = configparser.ConfigParser()
        config[DEFAULT_SECTION] = {}
        config[DEFAULT_SECTION]["compaction_strategy"] = "summarization"

        # Write the config
        with open(ticca.config.CONFIG_FILE, "w") as f:
            config.write(f)

        # Test that the strategy is read correctly
        strategy = get_compaction_strategy()
        assert strategy == "summarization"

        # Reset the config directory
        ticca.config.CONFIG_DIR = original_config_dir
        ticca.config.CONFIG_FILE = original_config_file


def test_set_compaction_strategy_invalid():
    """Test that an invalid compaction strategy defaults to truncation"""
    # Create a temporary config directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        original_config_dir = CONFIG_DIR
        original_config_file = CONFIG_FILE

        # Monkey patch the config directory
        import ticca.config

        ticca.config.CONFIG_DIR = temp_dir
        ticca.config.CONFIG_FILE = os.path.join(temp_dir, "puppy.cfg")

        # Create the config file with an invalid strategy
        config = configparser.ConfigParser()
        config[DEFAULT_SECTION] = {}
        config[DEFAULT_SECTION]["compaction_strategy"] = "invalid_strategy"

        # Write the config
        with open(ticca.config.CONFIG_FILE, "w") as f:
            config.write(f)

        # Test that the strategy defaults to truncation
        strategy = get_compaction_strategy()
        assert strategy == "truncation"

        # Reset the config directory
        ticca.config.CONFIG_DIR = original_config_dir
        ticca.config.CONFIG_FILE = original_config_file
