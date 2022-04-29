import subprocess

import pytest

from kuebiko import PROJECT_DIR


@pytest.mark.flow
def test_Sic2007Structure():
    out = subprocess.check_output(
        [
            "python",
            f"{PROJECT_DIR}/kuebiko/pipeline/sic/flow.py",
            "--metadata",
            "service",
            "--datastore",
            "local",
            "run",
        ]
    )
    print(out.decode())
