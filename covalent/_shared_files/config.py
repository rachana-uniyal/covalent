# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

import os
import shutil
from functools import reduce
from operator import getitem
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import toml

"""Configuration manager."""


class _ConfigManager:
    """Configuration manager class object.

    This class is used to manage an in-memory copy of a TOML configuration file.
    """

    def __init__(self) -> None:
        config_dir = (
            os.environ.get("COVALENT_CONFIG_DIR")
            or (os.environ.get("XDG_CONFIG_DIR") or (os.environ["HOME"] + "/.config"))
        ) + "/covalent"
        self.config_file = f"{config_dir}/covalent.conf"

        if os.path.exists(self.config_file):
            self.read_config()
        else:
            Path(config_dir).mkdir(parents=True, exist_ok=True)

            self.generate_default_config()
            self.write_config()

        Path(self.get("sdk.log_dir")).mkdir(parents=True, exist_ok=True)
        Path(self.get("dispatcher.cache_dir")).mkdir(parents=True, exist_ok=True)
        Path(self.get("dispatcher.results_dir")).mkdir(parents=True, exist_ok=True)
        Path(self.get("dispatcher.log_dir")).mkdir(parents=True, exist_ok=True)
        Path(self.get("user_interface.log_dir")).mkdir(parents=True, exist_ok=True)

    def generate_default_config(self) -> None:
        """
        Load the default configuration into memory.

        Args:
            None

        Returns:
            None
        """

        from .defaults import _DEFAULT_CONFIG

        self.config_data = _DEFAULT_CONFIG

    def read_config(self) -> None:
        """
        Read the configuration from file.

        Args:
            None

        Returns:
            None
        """

        self.config_data = toml.load(self.config_file)

    def write_config(self) -> None:
        """
        Write the configuration to file.

        Args:
            None

        Returns:
            None
        """

        with open(self.config_file, "w") as f:
            toml.dump(self.config_data, f)

    def purge_config(self) -> None:
        """
        Purge the configuration directory.

        Args:
            None

        Returns:
            None
        """

        shutil.rmtree(os.path.dirname(self.config_file), ignore_errors=True)

    def get(self, key: str) -> Any:
        """
        Return a value given a dictionary key.

        Args:
            key: Key value in period-delimited format, e.g., config[dispatcher][port]
                 is queried by passing "dispatcher.port" as the key.

        Returns:
            value: The corresponding configuration value, usually a string or int.
        """

        return reduce(getitem, key.split("."), self.config_data)

    def set(self, key: str, value: Any) -> None:
        """
        Set a key-value pair in the configuration dictionary.

        Args:
            key: Key value in period-delimited format.
            value: The corresponding configuration setting.

        Returns:
            None
        """

        keys = key.split(".")
        reduce(getitem, keys[:-1], self.config_data)[keys[-1]] = value


_config_manager = _ConfigManager()


def set_config(new_config: Union[Dict, str], new_value: Optional[Any] = None) -> None:
    """
    Update the configuration.

    Users may pass a dictionary of new settings, or a string key with a value to set
    a single configuration setting.

    Args:
        new_config: The new configuration dictionary, or a string key name.
        new_value: A new configuration value, if the first argument is a string.

    Returns:
        None
    """

    if isinstance(new_config, str):
        _config_manager.set(new_config, new_value)
    else:
        for key, value in new_config.items():
            _config_manager.set(key, value)
    _config_manager.write_config()


def get_config(entries: Union[str, List] = []) -> Union[Dict, Union[str, int]]:
    """
    Return a configuration setting.

    Invocation with no arguments returns the full configuration description; with a
    list of arguments returns a dictionary of configuration settings; with a string
    key name returns the corresponding value for a single setting.

    Args:
        entries: A string or list of strings specifying key names.

    Returns:
        config: A dictionary or string describing the corresponding configuration
                settings.
    """

    if isinstance(entries, List) and len(entries) == 0:
        # If no arguments are passed, return the full configuration as a dict
        return _config_manager.config_data
    elif isinstance(entries, List) and len(entries) == 1:
        # If the argument is a single key in a List, return the corresponding value
        return _config_manager.get(entries[0])
    elif isinstance(entries, str):
        # If the argument is a string key, return the corresponding value
        return _config_manager.get(entries)
    else:
        # If a set of keys are passed, return a corresponding dict of key-value pairs
        values = [_config_manager.get(entry) for entry in entries]
        return dict(zip(entries, values))


def reload_config() -> None:
    """
    Reload the configuration from the TOML file.

    Args:
        None

    Returns:
        None
    """

    _config_manager.read_config()
