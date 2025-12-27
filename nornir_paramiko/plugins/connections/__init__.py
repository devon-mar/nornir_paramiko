import os
from typing import Any, Optional

import paramiko
from nornir.core.configuration import Config

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
        hostname: str | None,
        username: str | None,
        password: str | None,
        port: int | None,
        platform: str | None,
        extras: dict[str, Any] | None = None,
        configuration: Config | None = None,
    ) -> None:
        if hostname is None:
            raise ValueError("hostname must not be none")

        extras = extras or {}

        port = port or 22

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        ssh_config = paramiko.SSHConfig()
        ssh_config_file = configuration.ssh.config_file  # type: ignore
        if os.path.exists(ssh_config_file):
            with open(ssh_config_file) as f:
                ssh_config.parse(f)
        parameters: dict[str, Any] = {
            "hostname": hostname,
            "username": username,
            "password": password,
            "port": port,
        }

        user_config = ssh_config.lookup(hostname)

        for k in ("hostname", "port"):
            if k in user_config:
                parameters[k] = user_config[k]
        if "user" in user_config:
            parameters["username"] = user_config["user"]

        if "proxycommand" in user_config:
            parameters["sock"] = paramiko.ProxyCommand(user_config["proxycommand"])

        if "identityfile" in user_config:
            parameters["key_filename"] = user_config["identityfile"]

        extras.update(parameters)
        client.connect(**extras)
        self.connection = client

    def close(self) -> None:
        self.connection.close()
