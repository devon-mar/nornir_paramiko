import os
from typing import Any, Dict, Optional

from nornir.core.configuration import Config

import paramiko

CONNECTION_NAME = "paramiko"


class Paramiko:
    """
    This plugin connects to the device with paramiko to the device and sets the
    relevant connection.

    Args:
        extras: maps to argument passed to ``ConnectHandler``.
    """

    def open(
        self,
        hostname: Optional[str],
        username: Optional[str],
        password: Optional[str],
        port: Optional[int],
        platform: Optional[str],
        extras: Optional[Dict[str, Any]] = None,
        configuration: Optional[Config] = None,
    ) -> None:
        extras = extras or {}

        port = port or 22

        client = paramiko.SSHClient()
        client._policy = paramiko.WarningPolicy()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_config = paramiko.SSHConfig()
        ssh_config_file = configuration.ssh.config_file  # type: ignore
        if os.path.exists(ssh_config_file):
            with open(ssh_config_file) as f:
                ssh_config.parse(f)
        parameters = {
            "hostname": hostname,
            "username": username,
            "password": password,
            "port": port,
        }

        user_config = ssh_config.lookup(hostname)

        for k in ("hostname",  "port"):
            if k in user_config:
                    parameters[k] = user_config[k]
        if "user" in user_config:
            parameters["username"] = user_config["user"]


        if "proxycommand" in user_config:
            parameters["sock"] = paramiko.ProxyCommand(user_config["proxycommand"])

        # TODO configurable
        #  if ssh_key_file:
        #      parameters['key_filename'] = ssh_key_file
        if "identityfile" in user_config:
            parameters["key_filename"] = user_config["identityfile"]

        extras.update(parameters)
        client.connect(**extras)
        self.connection = client

    def close(self) -> None:
        self.connection.close()
