from pathlib import Path

import pytest
from nornir import InitNornir


@pytest.fixture(scope="session")
def nr():
    cwd = Path(__file__).parent
    nornir = InitNornir(
        logging={"enabled": False},
        inventory={
            "plugin": "SimpleInventory",
            "options": {"host_file": str(cwd.joinpath("inventory/hosts.yml"))},
        },
    )
    yield nornir
    nornir.close_connections()


@pytest.fixture(scope="session")
def nr_dry_run():
    cwd = Path(__file__).parent
    nornir = InitNornir(
        dry_run=True,
        logging={"enabled": False},
        inventory={
            "plugin": "SimpleInventory",
            "options": {"host_file": str(cwd.joinpath("inventory/hosts.yml"))},
        },
    )
    yield nornir
    nornir.close_connections()


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "host" not in metafunc.fixturenames:
        return
    metafunc.parametrize("host", ("password", "key"))
