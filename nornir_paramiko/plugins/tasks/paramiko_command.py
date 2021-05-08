from nornir.core.task import Result, Task
from nornir_paramiko.plugins.connections import CONNECTION_NAME
from nornir_paramiko.exceptions import CommandError


def paramiko_command(task: Task, command: str) -> Result:
    """
    Executes a command remotely on the host
    Args:
        command: The command to execute

    Returns:
        :class:`Result` object with the following attributes set:
          * result (``str``): stderr or stdout
          * stdout (``str``): stdout
          * stderr (``str``): stderr
    Raises:
        nornir_paramiko.exceptions.CommandError: When there is a command error.
    """
    client = task.host.get_connection(CONNECTION_NAME, task.nornir.config)

    chan = client.get_transport().open_session()

    chan.exec_command(command)

    with chan.makefile() as f:
        stdout = f.read().decode()
    with chan.makefile_stderr() as f:
        stderr = f.read().decode()

    exit_status_code = chan.recv_exit_status()

    if exit_status_code:
        raise CommandError(command, exit_status_code, stdout, stderr)

    result = stderr if stderr else stdout
    return Result(result=result, host=task.host, stderr=stderr, stdout=stdout)
