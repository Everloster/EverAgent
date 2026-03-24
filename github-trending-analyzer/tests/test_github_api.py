from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


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


def test_encode_query_params():
    module = load_module()
    encoded = module.encode_query_params({"q": "repo:foo/bar is:issue label:good first issue"})
    assert "q=repo%3Afoo%2Fbar+is%3Aissue+label%3Agood+first+issue" in encoded
