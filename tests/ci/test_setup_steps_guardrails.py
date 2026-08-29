from pathlib import Path

from scripts.ci.validate_copilot_setup_steps import test_complexity_analysis, test_lfs_configuration


def test_lfs_configuration_accepts_single_quoted_skip_smudge(tmp_path: Path) -> None:
    workflow = tmp_path / "copilot-setup-steps.yml"
    workflow.write_text("GIT_LFS_SKIP_SMUDGE: '1'\n", encoding="utf-8")

    result = test_lfs_configuration(str(workflow))

    assert result.passed is True
    assert "LFS configuration correct" in result.message


def test_complexity_analysis_ignores_reasonable_step_count(tmp_path: Path) -> None:
    workflow = tmp_path / "copilot-setup-steps.yml"
    workflow.write_text(
        "jobs:\n"
        "  setup:\n"
        "    steps:\n"
        "      - name: one\n"
        "        run: echo one\n"
        "      - name: two\n"
        "        run: echo two\n"
        "      - name: three\n"
        "        run: echo three\n"
        "      - name: four\n"
        "        run: echo four\n"
        "      - name: five\n"
        "        run: echo five\n"
        "      - name: six\n"
        "        run: echo six\n"
        "      - name: seven\n"
        "        run: echo seven\n"
        "      - name: eight\n"
        "        run: echo eight\n"
        "      - name: nine\n"
        "        run: echo nine\n"
        "      - name: ten\n"
        "        run: echo ten\n"
        "      - name: eleven\n"
        "        run: echo eleven\n"
        "      - name: twelve\n"
        "        run: echo twelve\n"
        "      - name: thirteen\n"
        "        run: echo thirteen\n"
        "      - name: fourteen\n"
        "        run: echo fourteen\n"
        "      - name: fifteen\n"
        "        run: echo fifteen\n"
        "      - name: sixteen\n"
        "        run: echo sixteen\n"
        "      - name: seventeen\n"
        "        run: echo seventeen\n"
        "      - name: eighteen\n"
        "        run: echo eighteen\n"
        "      - name: nineteen\n"
        "        run: echo nineteen\n"
        "      - name: twenty\n"
        "        run: echo twenty\n"
        "      - name: twenty-one\n"
        "        run: echo twenty-one\n"
        "      - name: twenty-two\n"
        "        run: echo twenty-two\n"
        "      - name: twenty-three\n"
        "        run: echo twenty-three\n"
        "      - name: twenty-four\n"
        "        run: echo twenty-four\n"
        "      - name: twenty-five\n"
        "        run: echo twenty-five\n"
        "      - name: twenty-six\n"
        "        run: echo twenty-six\n"
        "      - name: twenty-seven\n"
        "        run: echo twenty-seven\n"
        "      - name: twenty-eight\n"
        "        run: echo twenty-eight\n"
        "      - name: twenty-nine\n"
        "        run: echo twenty-nine\n"
        "      - name: thirty\n"
        "        run: echo thirty\n"
        "      - name: thirty-one\n"
        "        run: echo thirty-one\n"
        "      - name: thirty-two\n"
        "        run: echo thirty-two\n"
        "      - name: thirty-three\n"
        "        run: echo thirty-three\n"
        "      - name: thirty-four\n"
        "        run: echo thirty-four\n"
        "      - name: thirty-five\n"
        "        run: echo thirty-five\n"
        "      - name: thirty-six\n"
        "        run: echo thirty-six\n"
        "      - name: thirty-seven\n"
        "        run: echo thirty-seven\n"
        "      - name: thirty-eight\n"
        "        run: echo thirty-eight\n"
        "  lint:\n"
        "    steps:\n"
        "      - name: l1\n"
        "        run: echo l1\n",
        encoding="utf-8",
    )

    result = test_complexity_analysis(str(workflow))

    assert result.passed is True
