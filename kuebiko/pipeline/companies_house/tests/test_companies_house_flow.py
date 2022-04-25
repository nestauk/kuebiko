import subprocess

import pytest

from kuebiko import PROJECT_DIR


@pytest.mark.flow
def test_CompaniesHouseDump():
    out = subprocess.check_output(
        [
            "python",
            f"{PROJECT_DIR}/kuebiko/pipeline/companies_house/flow.py",
            "--metadata",
            "service",
            "--datastore",
            "local",
            "--environment",
            "conda",
            "run",
        ]
    )
    print(out.decode())
