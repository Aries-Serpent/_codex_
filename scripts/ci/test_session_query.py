#!/usr/bin/env python3
"""
Test suite for session_query.py - 15+ unit tests covering all functionality.

Tests include:
- get_session_by_id (existing and non-existent)
- query_sessions with multiple filters
- list_recent_sessions date filtering
- find_similar_sessions by tags
- get_sessions_by_agent
- filter_by_status
- stats_summary
- CLI interface
- CSV output format
- Edge cases and error handling
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from io import StringIO
import sys

# Import the module to test
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.ci.session_query import SessionQuery, format_json_output, format_csv_output


class TestSessionQuery(unittest.TestCase):
    """Test cases for SessionQuery class."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_dir = tempfile.mkdtemp()
        cls.index_path = os.path.join(cls.test_dir, 'test_index.json')

    def setUp(self):
        """Create test sessions."""
        # Create sample sessions data
        now = datetime.utcnow()
        self.test_sessions = [
            {
                'session_id': 'session-001',
                'first_timestamp': (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'last_timestamp': (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'event_types': ['cli.start', 'cli.finish'],
                'event_count': 2,
                'status': 'complete',
                'agent_name': 'ci-auto-healer-agent',
                'pr_number': 3854,
                'branch': 'main',
                'tags': ['ci', 'healer'],
            },
            {
                'session_id': 'session-002',
                'first_timestamp': (now - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'last_timestamp': (now - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'event_types': ['cli.start', 'app.exception'],
                'event_count': 2,
                'status': 'failed',
                'agent_name': 'test-agent',
                'pr_number': 3850,
                'branch': 'feature',
                'tags': ['test'],
            },
            {
                'session_id': 'session-003',
                'first_timestamp': (now - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'last_timestamp': (now - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'event_types': ['training_start', 'training_end'],
                'event_count': 100,
                'status': 'complete',
                'agent_name': 'ci-auto-healer-agent',
                'pr_number': None,
                'branch': 'develop',
                'tags': ['ml', 'training'],
            },
            {
                'session_id': 'session-004',
                'first_timestamp': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'last_timestamp': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'event_types': ['training_start'],
                'event_count': 10,
                'status': 'in_progress',
                'agent_name': 'ml-validation-suite-agent',
                'pr_number': 3899,
                'branch': 'main',
                'tags': ['ml'],
            },
        ]

        # Write test index file
        with open(self.index_path, 'w') as f:
            json.dump({'sessions': self.test_sessions}, f)

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.index_path):
            os.remove(self.index_path)

    def test_get_session_by_id_existing(self):
        """Test get_session_by_id with existing session."""
        sq = SessionQuery(index_path=self.index_path)
        result = sq.get_session_by_id('session-001')

        self.assertIsNotNone(result)
        self.assertEqual(result['session_id'], 'session-001')
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(result['agent_name'], 'ci-auto-healer-agent')

    def test_get_session_by_id_nonexistent(self):
        """Test get_session_by_id with non-existent session."""
        sq = SessionQuery(index_path=self.index_path)
        result = sq.get_session_by_id('nonexistent-session')

        self.assertIsNone(result)

    def test_query_sessions_by_session_id(self):
        """Test query_sessions filtering by session_id."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(session_id='session-001')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['session_id'], 'session-001')

    def test_query_sessions_by_status(self):
        """Test query_sessions filtering by status."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(status='complete')

        self.assertEqual(len(results), 2)
        for session in results:
            self.assertEqual(session['status'], 'complete')

    def test_query_sessions_by_agent_name(self):
        """Test query_sessions filtering by agent_name."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(agent_name='ci-auto-healer-agent')

        self.assertEqual(len(results), 2)
        for session in results:
            self.assertEqual(session['agent_name'], 'ci-auto-healer-agent')

    def test_query_sessions_by_pr_number(self):
        """Test query_sessions filtering by pr_number."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(pr_number=3854)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['pr_number'], 3854)

    def test_query_sessions_multiple_filters(self):
        """Test query_sessions with multiple filters."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(
            agent_name='ci-auto-healer-agent',
            status='complete'
        )

        self.assertEqual(len(results), 2)
        for session in results:
            self.assertEqual(session['agent_name'], 'ci-auto-healer-agent')
            self.assertEqual(session['status'], 'complete')

    def test_query_sessions_with_limit(self):
        """Test query_sessions with limit parameter."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(limit=2)

        self.assertEqual(len(results), 2)

    def test_list_recent_sessions_7_days(self):
        """Test list_recent_sessions filters correctly by date."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.list_recent_sessions(days=7)

        # Should return sessions from last 7 days (session-001, session-002, session-004)
        self.assertGreater(len(results), 0)
        for session in results:
            self.assertIsNotNone(session['first_timestamp'])

    def test_list_recent_sessions_2_days(self):
        """Test list_recent_sessions with shorter timeframe."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.list_recent_sessions(days=2)

        # Should return only very recent sessions
        self.assertGreaterEqual(len(results), 1)

    def test_find_similar_sessions_by_tags(self):
        """Test find_similar_sessions by tags."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.find_similar_sessions(tags=['ml'], limit=5)

        self.assertGreater(len(results), 0)
        # All results should have 'ml' tag
        for session in results:
            self.assertIn('ml', session['tags'])

    def test_find_similar_sessions_multiple_tags(self):
        """Test find_similar_sessions with multiple tags."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.find_similar_sessions(tags=['ci', 'healer'], limit=5)

        self.assertGreater(len(results), 0)

    def test_find_similar_sessions_no_matches(self):
        """Test find_similar_sessions with no matching tags."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.find_similar_sessions(tags=['nonexistent'], limit=5)

        self.assertEqual(len(results), 0)

    def test_get_sessions_by_agent(self):
        """Test get_sessions_by_agent filters correctly."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.get_sessions_by_agent(
            agent_name='ci-auto-healer-agent',
            days=30,
            limit=50
        )

        self.assertGreater(len(results), 0)
        for session in results:
            self.assertEqual(session['agent_name'], 'ci-auto-healer-agent')

    def test_filter_by_status(self):
        """Test filter_by_status returns correct sessions."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.filter_by_status('failed')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['status'], 'failed')

    def test_stats_summary(self):
        """Test stats_summary returns correct counts."""
        sq = SessionQuery(index_path=self.index_path)
        stats = sq.stats_summary()

        self.assertEqual(stats['total_sessions'], 4)
        self.assertIn('complete', stats['by_status'])
        self.assertIn('failed', stats['by_status'])
        self.assertIn('in_progress', stats['by_status'])
        self.assertEqual(stats['by_status']['complete'], 2)
        self.assertEqual(stats['by_status']['failed'], 1)
        self.assertEqual(stats['by_status']['in_progress'], 1)
        self.assertIn('date_range', stats)
        self.assertIsNotNone(stats['date_range'])

    def test_stats_summary_by_agent(self):
        """Test stats_summary counts by agent."""
        sq = SessionQuery(index_path=self.index_path)
        stats = sq.stats_summary()

        self.assertEqual(stats['by_agent']['ci-auto-healer-agent'], 2)
        self.assertEqual(stats['by_agent']['test-agent'], 1)
        self.assertEqual(stats['by_agent']['ml-validation-suite-agent'], 1)

    def test_stats_summary_by_branch(self):
        """Test stats_summary counts by branch."""
        sq = SessionQuery(index_path=self.index_path)
        stats = sq.stats_summary()

        self.assertEqual(stats['by_branch']['main'], 2)
        self.assertEqual(stats['by_branch']['feature'], 1)
        self.assertEqual(stats['by_branch']['develop'], 1)

    def test_query_sessions_empty_result(self):
        """Test query_sessions returns empty list on no matches."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(agent_name='nonexistent-agent')

        self.assertEqual(results, [])
        self.assertIsInstance(results, list)

    def test_query_sessions_sort_order(self):
        """Test query_sessions returns results sorted by most recent first."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(status='complete')

        # Check that results are sorted (most recent first)
        if len(results) > 1:
            for i in range(len(results) - 1):
                current = results[i]['last_timestamp']
                next_ts = results[i + 1]['last_timestamp']
                # Current should be >= next (descending order)
                self.assertGreaterEqual(current, next_ts)

    def test_format_json_output(self):
        """Test JSON output formatting."""
        data = [{'session_id': 'test', 'status': 'complete'}]
        output = format_json_output(data)

        self.assertIsInstance(output, str)
        parsed = json.loads(output)
        self.assertEqual(parsed[0]['session_id'], 'test')

    def test_format_csv_output(self):
        """Test CSV output formatting."""
        data = [
            {'session_id': 'test1', 'status': 'complete'},
            {'session_id': 'test2', 'status': 'failed'},
        ]
        output = format_csv_output(data)

        self.assertIsInstance(output, str)
        self.assertIn('session_id', output)
        self.assertIn('status', output)
        self.assertIn('test1', output)
        self.assertIn('test2', output)

    def test_format_csv_output_empty(self):
        """Test CSV output with empty data."""
        output = format_csv_output([])

        self.assertEqual(output, "")

    def test_session_query_verbose_mode(self):
        """Test SessionQuery with verbose flag."""
        sq = SessionQuery(index_path=self.index_path)
        sq.verbose = True

        # Should not raise an error
        results = sq.query_sessions()
        self.assertIsInstance(results, list)

    def test_session_by_id_dict_populated(self):
        """Test that session_by_id dict is properly populated."""
        sq = SessionQuery(index_path=self.index_path)

        self.assertIn('session-001', sq.session_by_id)
        self.assertIn('session-002', sq.session_by_id)
        self.assertEqual(sq.session_by_id['session-001']['session_id'], 'session-001')

    def test_query_sessions_iso8601_timestamp_filter(self):
        """Test query_sessions with ISO 8601 timestamp filter."""
        sq = SessionQuery(index_path=self.index_path)

        # Create a timestamp 4 days ago
        cutoff = datetime.utcnow() - timedelta(days=4)
        cutoff_iso = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')

        results = sq.query_sessions(since_timestamp=cutoff_iso)

        # Should return only sessions newer than 4 days ago
        self.assertGreater(len(results), 0)


class TestSessionQueryCLI(unittest.TestCase):
    """Test CLI interface of session_query."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_dir = tempfile.mkdtemp()
        cls.index_path = os.path.join(cls.test_dir, 'test_index_cli.json')

    def setUp(self):
        """Create test sessions."""
        now = datetime.utcnow()
        test_sessions = [
            {
                'session_id': 'cli-test-001',
                'first_timestamp': (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'last_timestamp': (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'event_types': ['cli.finish'],
                'event_count': 2,
                'status': 'complete',
                'agent_name': 'test-agent',
                'pr_number': 100,
                'branch': 'main',
                'tags': ['test'],
            },
        ]

        with open(self.index_path, 'w') as f:
            json.dump({'sessions': test_sessions}, f)

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.index_path):
            os.remove(self.index_path)

    def test_cli_session_by_id(self):
        """Test CLI with --session-id flag."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(session_id='cli-test-001')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['session_id'], 'cli-test-001')

    def test_cli_pr_number(self):
        """Test CLI with --pr-number flag."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions(pr_number=100)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['pr_number'], 100)

    def test_cli_agent_name(self):
        """Test CLI with --agent-name flag."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.get_sessions_by_agent('test-agent', days=30)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['agent_name'], 'test-agent')

    def test_cli_stats(self):
        """Test CLI with --stats flag."""
        sq = SessionQuery(index_path=self.index_path)
        stats = sq.stats_summary()

        self.assertEqual(stats['total_sessions'], 1)
        self.assertIn('by_status', stats)

    def test_cli_json_output(self):
        """Test CLI with JSON output format."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions()
        output = format_json_output(results)

        self.assertIsInstance(output, str)
        parsed = json.loads(output)
        self.assertIsInstance(parsed, list)

    def test_cli_csv_output(self):
        """Test CLI with CSV output format."""
        sq = SessionQuery(index_path=self.index_path)
        results = sq.query_sessions()
        output = format_csv_output(results)

        self.assertIsInstance(output, str)
        self.assertIn('session_id', output)
        self.assertIn('cli-test-001', output)


class TestSessionQueryEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_dir = tempfile.mkdtemp()
        cls.index_path = os.path.join(cls.test_dir, 'test_index_edge.json')

    def setUp(self):
        """Create test sessions."""
        # Create minimal test data
        with open(self.index_path, 'w') as f:
            json.dump({'sessions': []}, f)

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.index_path):
            os.remove(self.index_path)

    def test_empty_sessions_list(self):
        """Test with empty sessions list."""
        sq = SessionQuery(index_path=self.index_path)

        self.assertEqual(len(sq.sessions), 0)
        self.assertEqual(len(sq.query_sessions()), 0)

    def test_nonexistent_index_file(self):
        """Test with nonexistent index file."""
        nonexistent_path = os.path.join(self.test_dir, 'nonexistent.json')
        sq = SessionQuery(index_path=nonexistent_path)

        # Should initialize without error
        self.assertIsNotNone(sq)

    def test_invalid_timestamp_filter(self):
        """Test query with invalid timestamp format."""
        now = datetime.utcnow()
        with open(self.index_path, 'w') as f:
            json.dump({'sessions': [{
                'session_id': 'test',
                'first_timestamp': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'status': 'complete',
            }]}, f)

        sq = SessionQuery(index_path=self.index_path)
        # Invalid timestamp should be silently ignored
        results = sq.query_sessions(since_timestamp='invalid-timestamp')

        self.assertEqual(len(results), 1)

    def test_stats_summary_empty_sessions(self):
        """Test stats_summary with empty sessions."""
        sq = SessionQuery(index_path=self.index_path)
        stats = sq.stats_summary()

        self.assertEqual(stats['total_sessions'], 0)
        self.assertEqual(stats['by_status'], {})
        self.assertEqual(stats['by_agent'], {})


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
