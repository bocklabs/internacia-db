"""Safety and ordering properties of the actual CI/release configuration."""
import ast
import re
import subprocess

import pytest
import yaml

from internacia_builder.paths import project_root


def workflow(name):
    return yaml.load((project_root() / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader)


@pytest.mark.parametrize(("name", "job"), [("validate.yml", "validate"), ("release.yml", "release")])
def test_committed_snapshot_is_checked_against_the_build_and_final_artifacts_are_tested(name, job):
    config = workflow(name)["jobs"][job]
    commands = [step.get("run", "") for step in config["steps"]]
    build = next(i for i, command in enumerate(commands) if "scripts/builder.py build" in command)
    committed = next(i for i, command in enumerate(commands) if "scripts/check_committed_snapshot.py --fresh" in command)
    tests = next(i for i, command in enumerate(commands) if "pytest tests/" in command)
    assert build < committed and build < tests
    assert any("check_generated_artifacts.py --datasets-dir" in command for command in commands)
    assert "INTERNACIA_DATASETS_DIR" in config["env"]
    assert any("check_quality_report.py" in command for command in commands)
    assert any("check_release_bundle.py" in command for command in commands)


def test_docs_pr_build_has_no_publication_permissions_or_deployment():
    config = workflow("deploy-docs.yml")
    assert "pull_request" in config["on"]
    assert config["permissions"] == {"contents": "read"}
    assert config["jobs"]["deploy"]["if"] == "github.event_name != 'pull_request'"
    for step in config["jobs"]["build"]["steps"]:
        if step.get("uses", "").startswith("actions/upload-pages-artifact"):
            assert step["if"] == "github.event_name != 'pull_request'"


def test_workflow_shell_and_embedded_python_parse():
    for path in (project_root() / ".github/workflows").glob("*.yml"):
        for job in workflow(path.name)["jobs"].values():
            for step in job.get("steps", []):
                if "run" not in step:
                    continue
                result = subprocess.run(["bash", "-n"], input=step["run"], text=True, capture_output=True)
                assert result.returncode == 0, f"{path.name}: {result.stderr}"
                for python in re.findall(r"python - <<'PY'\n(.*?)\nPY", step["run"], re.S):
                    ast.parse(python)
