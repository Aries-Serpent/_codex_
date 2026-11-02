"""A scheduling request is not successful execution."""

from orchestration.scheduling.lane_scheduler_v1 import Lane, LaneSchedulerV1, LaneState


def test_unscheduled_runtime_never_passes():
    scheduler = LaneSchedulerV1()
    scheduler.register_lanes([Lane("A", "analysis"), Lane("B", "dependent", ["A"])])
    results = scheduler.schedule_all_lanes()
    assert results["A"].state is LaneState.INCOMPLETE
    assert "Human-mediated" in results["A"].error_message
    assert results["B"].state is LaneState.BLOCKED
    assert all(lane.state is not LaneState.PASSED for lane in scheduler.lanes.values())


def test_passed_lane_remains_complete_until_explicit_reset():
    scheduler = LaneSchedulerV1()
    scheduler.register_lanes(
        [Lane("A", "analysis", state=LaneState.PASSED), Lane("B", "dependent", ["A"])]
    )
    results = scheduler.schedule_all_lanes()
    assert results["A"].state is LaneState.PASSED
    assert scheduler.get_lane_state("A") is LaneState.PASSED
    assert results["B"].state is LaneState.INCOMPLETE
    assert [result.lane_id for result in scheduler.execution_history] == ["B"]

    scheduler.reset_lane("A")
    results = scheduler.schedule_all_lanes()
    assert results["A"].state is LaneState.INCOMPLETE
    assert results["B"].state is LaneState.BLOCKED


def test_passed_lane_is_not_rechecked_against_incomplete_dependencies():
    scheduler = LaneSchedulerV1()
    scheduler.register_lanes(
        [Lane("A", "analysis"), Lane("B", "dependent", ["A"], state=LaneState.PASSED)]
    )
    result = scheduler.schedule_lane("B")
    assert result.state is LaneState.PASSED
    assert scheduler.get_lane_state("B") is LaneState.PASSED
    assert not scheduler.execution_history
