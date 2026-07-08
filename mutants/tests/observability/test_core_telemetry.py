import unittest

from scripts.observability.core_telemetry_collector import CoreTelemetryCollector


class TestCoreTelemetry(unittest.TestCase):
    def test_core_telemetry_collector_agent_lifecycle(self):
        collector = CoreTelemetryCollector()
        collector.record_agent_launch("agent-01", "explore", "user-01")
        collector.update_agent_uptime("agent-01", "explore", 3600)
        
        snapshot = collector.get_metrics_snapshot()
        self.assertIn("agent_launches_total{agent_id=agent-01,agent_type=explore,initiator_id=user-01}", snapshot["counters"])
        self.assertEqual(snapshot["gauges"]["agent_uptime_seconds{agent_id=agent-01,agent_type=explore}"], 3600)
        self.assertEqual(snapshot["event_count"], 1)

    def test_core_telemetry_collector_workflow(self):
        collector = CoreTelemetryCollector()
        collector.record_workflow_trigger("wf-123", "manual", "user-01")
        collector.record_workflow_completion("wf-123", "ci-build", "success", 125.5)
        
        snapshot = collector.get_metrics_snapshot()
        self.assertEqual(snapshot["counters"]["workflow_triggers_total{initiator_id=user-01,trigger_type=manual,workflow_id=wf-123}"], 1)
        self.assertEqual(snapshot["histograms"]["workflow_duration_seconds{workflow_id=wf-123,workflow_type=ci-build}"]["count"], 1)

    def test_core_telemetry_cardinality_limit(self):
        collector = CoreTelemetryCollector(cardinality_limit=10)
        for i in range(15):
            collector.record_agent_launch(f"agent-{i}", "explore", "user-01")
        
        snapshot = collector.get_metrics_snapshot()
        self.assertEqual(snapshot["timeseries_count"], 10)
        self.assertEqual(len(snapshot["counters"]), 10)

if __name__ == '__main__':
    unittest.main()
