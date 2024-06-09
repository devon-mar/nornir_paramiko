from nornir.core import Nornir

from nornir_paramiko.plugins.tasks import paramiko_command


def test_paramiko_command(host: str, nr: Nornir) -> None:
    result = nr.filter(name=host).run(task=paramiko_command, command="cd /home && pwd")

    assert result.failed is False
    assert len(result[host]) == 1
    host_result = result[host][0]
    assert host_result.stdout is not None
    assert host_result.stdout.strip() == "/home"
