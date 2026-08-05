#!/usr/bin/env python3
"""
Test suite for step-log.py logging functionality.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add scripts to path
scripts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')
sys.path.insert(0, scripts_dir)

# Import module with hyphen using importlib
import importlib.util
spec = importlib.util.spec_from_file_location(
    "step_log",
    os.path.join(scripts_dir, "step-log.py")
)
step_log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(step_log)


class TestStepLog(unittest.TestCase):
    """Test cases for step-log.py."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_log_dir = tempfile.mkdtemp()
        self.test_step_log = os.path.join(self.test_log_dir, "step-log.ndjson")
        self.test_running_log = os.path.join(self.test_log_dir, "_running.json")
        
        # Override paths
        step_log.LOG_DIR = self.test_log_dir
        step_log.STEP_LOG = self.test_step_log
        step_log.RUNNING_LOG = self.test_running_log
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
    
    def test_cmd_start(self):
        """Test logging step start."""
        step_log.cmd_start("WF-001", "orchestrator", "init", "Starting workflow")
        
        # Check log file
        with open(self.test_step_log) as f:
            entry = json.loads(f.readline())
        
        self.assertEqual(entry["workflow_id"], "WF-001")
        self.assertEqual(entry["agent"], "orchestrator")
        self.assertEqual(entry["step"], "init")
        self.assertEqual(entry["event"], "start")
        self.assertEqual(entry["status"], "in_progress")
        
        # Check running state
        with open(self.test_running_log) as f:
            running = json.load(f)
        
        self.assertIn("WF-001", running)
        self.assertEqual(running["WF-001"]["current_step"], "init")
    
    def test_cmd_end(self):
        """Test logging step end."""
        # First start
        step_log.cmd_start("WF-002", "miles-expert", "analyze", "Analyzing")
        
        # Then end
        step_log.cmd_end("WF-002", "miles-expert", "analyze", "success", "Analysis complete")
        
        # Check log entries
        with open(self.test_step_log) as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 2)
        
        end_entry = json.loads(lines[1])
        self.assertEqual(end_entry["event"], "end")
        self.assertEqual(end_entry["status"], "success")
        self.assertIsNotNone(end_entry["duration_ms"])
    
    def test_cmd_log(self):
        """Test logging intermediate event."""
        step_log.cmd_log("WF-003", "orchestrator", "dispatch", "info", "Sending to expert")
        
        with open(self.test_step_log) as f:
            entry = json.loads(f.readline())
        
        self.assertEqual(entry["event"], "log")
        self.assertEqual(entry["status"], "info")
    
    def test_session_id_integration(self):
        """Test that session_id is included in logs."""
        step_log.cmd_start("WF-004", "orchestrator", "init", "Starting", session_id="abc123")
        
        with open(self.test_step_log) as f:
            entry = json.loads(f.readline())
        
        self.assertEqual(entry["session_id"], "abc123")
    
    def test_read_all(self):
        """Test reading all log entries."""
        step_log.cmd_start("WF-005", "agent1", "step1", "First")
        step_log.cmd_start("WF-005", "agent2", "step2", "Second")
        step_log.cmd_end("WF-005", "agent1", "step1", "success", "Done")
        
        entries = step_log._read_all()
        self.assertEqual(len(entries), 3)
    
    def test_cmd_view_empty(self):
        """Test viewing logs when none exist."""
        # Should not raise exception
        step_log.cmd_view("WF-999")
    
    def test_cmd_status(self):
        """Test workflow status display."""
        step_log.cmd_start("WF-006", "agent1", "step1", "First")
        step_log.cmd_end("WF-006", "agent1", "step1", "success", "Done")
        
        # Should not raise exception
        step_log.cmd_status("WF-006")


if __name__ == '__main__':
    unittest.main()
