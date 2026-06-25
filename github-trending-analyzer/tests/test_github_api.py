from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest import mock


def load_module():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "github-deep-research"
        / "scripts"
        / "github_api.py"
    )
    spec = spec_from_file_location("github_api", module_path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class _FakeProc:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr


def test_get_builds_gh_command_no_params():
    """_get should call `gh api <endpoint>` for a plain GET."""
    module = load_module()
    with mock.patch.object(module.shutil, "which", return_value="/usr/bin/gh"):
        api = module.GitHubAPI()
    with mock.patch.object(
        module.subprocess, "run", return_value=_FakeProc(stdout='{"ok": true}')
    ) as run:
        result = api._get("/repos/foo/bar")
    assert result == {"ok": True}
    cmd = run.call_args[0][0]
    assert cmd[:3] == ["gh", "api", "repos/foo/bar"]


def test_get_builds_gh_command_with_params():
    """Params must be sent as `-X GET -f k=v` (not a POST body)."""
    module = load_module()
    with mock.patch.object(module.shutil, "which", return_value="/usr/bin/gh"):
        api = module.GitHubAPI()
    with mock.patch.object(
        module.subprocess, "run", return_value=_FakeProc(stdout="[]")
    ) as run:
        api._get("/repos/foo/bar/contributors", params={"per_page": 3})
    cmd = run.call_args[0][0]
    assert "-X" in cmd and "GET" in cmd
    assert "-f" in cmd
    assert "per_page=3" in cmd


def test_get_raw_accept_returns_text():
    """raw Accept header should return stdout text, not parsed JSON."""
    module = load_module()
    with mock.patch.object(module.shutil, "which", return_value="/usr/bin/gh"):
        api = module.GitHubAPI()
    with mock.patch.object(
        module.subprocess, "run", return_value=_FakeProc(stdout="# Title\nbody")
    ):
        result = api._get(
            "/repos/foo/bar/readme", accept="application/vnd.github.raw"
        )
    assert result == "# Title\nbody"
