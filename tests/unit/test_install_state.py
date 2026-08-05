#!/usr/bin/env python3
"""
Test suite for install-state.py session management.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, mock_open

# Add scripts to path
scripts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')
sys.path.insert(0, scripts_dir)

# Import module with hyphen using importlib
import importlib.util
spec = importlib.util.spec_from_file_location(
    "install_state",
    os.path.join(scripts_dir, "install-state.py")
)
install_state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install_state)


class TestInstallState(unittest.TestCase):
    """Test cases for install-state.py."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_state_file = tempfile.mktemp(suffix='.json')
        install_state.STATE_FILE = self.test_state_file
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_state_file):
            os.remove(self.test_state_file)
    
    def test_load_empty_state(self):
        """Test loading non-existent state file."""
        state = install_state.load()
        self.assertEqual(state, {})
    
    def test_save_and_load_state(self):
        """Test saving and loading state."""
        test_data = {"version": "2.0.0", "workflow_root": "/test/path"}
        install_state.save(test_data)
        
        loaded = install_state.load()
        self.assertEqual(loaded["version"], "2.0.0")
        self.assertEqual(loaded["workflow_root"], "/test/path")
    
    def test_get_key(self):
        """Test getting a key from state."""
        test_data = {"test_key": "test_value"}
        install_state.save(test_data)
        
        self.assertEqual(install_state.get("test_key"), "test_value")
        self.assertEqual(install_state.get("nonexistent"), None)
        self.assertEqual(install_state.get("nonexistent", "default"), "default")
    
    def test_set_key(self):
        """Test setting a key in state."""
        install_state.set("new_key", "new_value")
        
        state = install_state.load()
        self.assertEqual(state["new_key"], "new_value")
    
    def test_create_session(self):
        """Test creating a new session."""
        session_id = install_state.create_session("TEST-001", "auto")
        
        self.assertIsNotNone(session_id)
        self.assertEqual(len(session_id), 8)
        
        session = install_state.get_session(session_id)
        self.assertEqual(session["workflow_id"], "TEST-001")
        self.assertEqual(session["mode"], "auto")
        self.assertEqual(session["status"], "running")
    
    def test_update_session(self):
        """Test updating session fields."""
        session_id = install_state.create_session("TEST-002", "auto")
        
        success = install_state.update_session(
            session_id,
            current_step="execute-plan",
            current_ac_index=2
        )
        self.assertTrue(success)
        
        session = install_state.get_session(session_id)
        self.assertEqual(session["current_step"], "execute-plan")
        self.assertEqual(session["current_ac_index"], 2)
    
    def test_pause_and_resume_session(self):
        """Test pausing and resuming a session."""
        session_id = install_state.create_session("TEST-003", "auto")
        
        # Pause
        success = install_state.pause_session(session_id, "test_pause")
        self.assertTrue(success)
        
        session = install_state.get_session(session_id)
        self.assertEqual(session["status"], "paused")
        self.assertEqual(len(session["checkpoints"]), 1)
        self.assertEqual(session["checkpoints"][0]["reason"], "test_pause")
        
        # Resume
        resumed = install_state.resume_session(session_id)
        self.assertIsNotNone(resumed)
        self.assertEqual(resumed["status"], "running")
    
    def test_complete_session(self):
        """Test completing a session."""
        session_id = install_state.create_session("TEST-004", "auto")
        
        success = install_state.complete_session(session_id, "completed")
        self.assertTrue(success)
        
        # Session should be removed from active sessions
        session = install_state.get_session(session_id)
        self.assertIsNone(session)
        
        # Should be in history
        state = install_state.load()
        self.assertEqual(len(state["workflow_history"]), 1)
        self.assertEqual(state["workflow_history"][0]["workflow_id"], "TEST-004")
    
    def test_list_sessions(self):
        """Test listing sessions with filters."""
        install_state.create_session("TEST-005", "auto")
        install_state.create_session("TEST-006", "plan")
        
        # Pause one
        sessions = install_state.list_sessions()
        install_state.pause_session(sessions[1]["session_id"])
        
        running = install_state.list_sessions("running")
        paused = install_state.list_sessions("paused")
        
        self.assertEqual(len(running), 1)
        self.assertEqual(len(paused), 1)
    
    def test_get_latest_checkpoint(self):
        """Test getting latest checkpoint."""
        session_id = install_state.create_session("TEST-007", "auto")
        
        # No checkpoints initially
        checkpoint = install_state.get_latest_checkpoint(session_id)
        self.assertIsNone(checkpoint)
        
        # Add checkpoints
        install_state.pause_session(session_id, "first")
        install_state.resume_session(session_id)
        install_state.pause_session(session_id, "second")
        
        checkpoint = install_state.get_latest_checkpoint(session_id)
        self.assertEqual(checkpoint["reason"], "second")


if __name__ == '__main__':
    unittest.main()
