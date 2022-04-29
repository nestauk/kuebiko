import subprocess

import pytest

from kuebiko import PROJECT_DIR


@pytest.mark.flow
def test_NsplLookup():
    out = subprocess.check_output(
        [
            "python",
            f"{PROJECT_DIR}/kuebiko/pipeline/nspl/flow.py",
            "--environment",
            "conda",
            "--metadata",
            "service",
            "--datastore",
            "local",
            "run",
        ]
    )
    print(out.decode())
