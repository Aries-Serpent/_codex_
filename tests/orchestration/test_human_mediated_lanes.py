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
