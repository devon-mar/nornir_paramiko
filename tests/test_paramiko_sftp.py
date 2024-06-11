import random
import shutil
import string
import tempfile
from pathlib import Path

import pytest
from nornir.core import Nornir

from nornir_paramiko.plugins.tasks import paramiko_command, paramiko_sftp


def random_str(len: int) -> str:
    return "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(len)
    )


@pytest.fixture
def temp_dir():
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


def test_paramiko_sftp(host: str, nr: Nornir, temp_dir: Path) -> None:
    nr_filtered = nr.filter(name=host)

    test_content = random_str(20)

    host_file = f"/tmp/test_{random_str(5)}"

    test_put_file = temp_dir.joinpath("test_put")

    with open(test_put_file, "w") as f:
        f.write(test_content)
    result = nr_filtered.run(
        task=paramiko_sftp, action="put", src=str(test_put_file), dst=host_file
    )

    assert result.failed is False
    assert len(result[host]) == 1
    host_result = result[host][0]
    assert host_result.changed is True
    assert host_result.files_changed == [host_file]

    # Test idempotence
    result = nr_filtered.run(
        task=paramiko_sftp, action="put", src=str(test_put_file), dst=host_file
    )
    assert result.failed is False
    assert len(result[host]) == 1
    host_result = result[host][0]
    assert host_result.changed is False
    assert host_result.files_changed == []

    # Now change the content then put
    test_content += "a"
    with open(test_put_file, "w") as f:
        f.write(test_content)
    result = nr_filtered.run(
        task=paramiko_sftp, action="put", src=str(test_put_file), dst=host_file
    )

    assert result.failed is False
    assert len(result[host]) == 1
    host_result = result[host][0]
    assert host_result.changed is True
    assert host_result.files_changed == [host_file]

    # Now retrieve the file back from the host
    test_get_file = temp_dir.joinpath("test_get")

    result = nr_filtered.run(
        task=paramiko_sftp, action="get", src=host_file, dst=str(test_get_file)
    )
    assert result.failed is False
    assert len(result[host]) == 1
    host_result = result[host][0]
    assert host_result.changed is True
    assert host_result.files_changed == [str(test_get_file)]

    with open(test_get_file) as f:
        have_content = f.read()
    assert have_content == test_content


def test_paramiko_sftp_dry_run(host: str, nr_dry_run: Nornir, temp_dir: Path) -> None:
    nr_filtered = nr_dry_run.filter(name=host)

    test_content = random_str(20)

    host_file = f"/tmp/test_{random_str(5)}"

    test_put_file = temp_dir.joinpath("test_put")

    with open(test_put_file, "w") as f:
        f.write(test_content)
    result = nr_filtered.run(
        task=paramiko_sftp, action="put", src=str(test_put_file), dst=host_file
    )

    assert result.failed is False
    assert len(result[host]) == 1
    host_result = result[host][0]
    assert host_result.changed is True
    assert host_result.files_changed == [host_file]

    # Check that the file was not written
    result = nr_filtered.run(task=paramiko_command, command=f"test -f '{host_file}'")
    assert result.failed is True  # because the file wasn't written


def test_paramiko_scp_only_host_dry_run(nr_dry_run: Nornir, temp_dir: Path) -> None:
    host = "alpinescp"
    nr_filtered = nr_dry_run.filter(name=host)

    test_content = random_str(20)

    host_file = f"/tmp/test_{random_str(5)}"

    test_put_file = temp_dir.joinpath("test_put")

    with open(test_put_file, "w") as f:
        f.write(test_content)
    result = nr_filtered.run(
        task=paramiko_sftp,
        action="put",
        src=str(test_put_file),
        dst=host_file,
        compare=False,
    )

    assert result.failed is False
    assert len(result[host]) == 1
    host_result = result[host][0]
    assert host_result.changed is True
    assert host_result.files_changed == [str(test_put_file)]

    # Check that the file was not written
    result = nr_filtered.run(task=paramiko_command, command=f"test -f '{host_file}'")
    assert result.failed is True  # because the file wasn't written


def test_paramiko_scp_only_host(nr: Nornir, temp_dir: Path) -> None:
    host = "alpinescp"
    nr_filtered = nr.filter(name=host)

    test_content = random_str(20)

    host_file = f"/tmp/test_{random_str(5)}"

    test_put_file = temp_dir.joinpath("test_put")

    with open(test_put_file, "w") as f:
        f.write(test_content)
    result = nr_filtered.run(
        task=paramiko_sftp,
        action="put",
        src=str(test_put_file),
        dst=host_file,
        compare=False,
    )

    assert result.failed is False
    assert len(result[host]) == 1
    host_result = result[host][0]
    assert host_result.changed is True
    assert host_result.files_changed == [str(test_put_file)]

    # Check that the file was written
    result = nr_filtered.run(task=paramiko_command, command=f"test -f '{host_file}'")
    assert result.failed is False


def test_paramiko_scp_only_host_compare(nr: Nornir, temp_dir: Path) -> None:
    host = "alpinescp"
    nr_filtered = nr.filter(name=host)

    host_file = f"/tmp/test_{random_str(5)}"

    test_put_file = temp_dir.joinpath("test_put")

    result = nr_filtered.run(
        task=paramiko_sftp,
        action="put",
        src=str(test_put_file),
        dst=host_file,
        compare=True,
    )
    assert result.failed is True  # host does not support SFTp
