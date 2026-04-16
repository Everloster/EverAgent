import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


class ValidateWorkspaceRegistryTests(unittest.TestCase):
    @staticmethod
    def _load_module():
        repo_root = Path(__file__).resolve().parents[1]
        scripts_dir = repo_root / "scripts"
        import sys

        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        import validate_workspace  # type: ignore

        return validate_workspace

    def test_registry_validation_passes_for_consistent_registry(self) -> None:
        validate_workspace = self._load_module()
        fake_registry = validate_workspace.ROOT / "docs" / "agents_registry.yaml"
        entries = [
            SimpleNamespace(
                agent="NeuronAgent",
                project="ai-learning",
                protocol="ai-learning/AGENTS.md",
                domain="AI/ML",
                status="🟢",
                title="AI Learning",
            )
        ]
        discovered = {"ai-learning": Path("/tmp/ai-learning")}

        with patch.object(validate_workspace, "AGENTS_REGISTRY", fake_registry), patch.object(
            validate_workspace, "load_agents_registry", return_value=entries
        ), patch.object(validate_workspace, "discover_projects", return_value=discovered), patch.object(
            Path, "exists", return_value=True
        ):
            issues = validate_workspace.validate_agents_registry(strict=True)

        self.assertEqual(issues, [])

    def test_registry_validation_flags_duplicate_project(self) -> None:
        validate_workspace = self._load_module()
        fake_registry = validate_workspace.ROOT / "docs" / "agents_registry.yaml"
        entries = [
            SimpleNamespace(
                agent="NeuronAgent",
                project="ai-learning",
                protocol="ai-learning/AGENTS.md",
                domain="AI/ML",
                status="🟢",
                title="AI Learning",
            ),
            SimpleNamespace(
                agent="OtherAgent",
                project="ai-learning",
                protocol="ai-learning/AGENTS.md",
                domain="AI/ML",
                status="🟢",
                title="AI Learning",
            ),
        ]
        discovered = {"ai-learning": Path("/tmp/ai-learning")}

        with patch.object(validate_workspace, "AGENTS_REGISTRY", fake_registry), patch.object(
            validate_workspace, "load_agents_registry", return_value=entries
        ), patch.object(validate_workspace, "discover_projects", return_value=discovered), patch.object(
            Path, "exists", return_value=True
        ):
            issues = validate_workspace.validate_agents_registry(strict=True)

        self.assertTrue(any("duplicate project in registry" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
