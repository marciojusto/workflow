#!/usr/bin/env python3
"""
Integration test for complete workflow execution.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')


class TestWorkflowIntegration(unittest.TestCase):
    """Integration tests for complete workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.workflow_id = "INTEGRATION-TEST"
        self.session_id = None
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _run_workflow_cmd(self, *args):
        """Run workflow.py command."""
        cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "workflow.py")] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result
    
    def _run_state_cmd(self, *args):
        """Run install-state.py command."""
        cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "install-state.py")] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result
    
    def test_complete_workflow_lifecycle(self):
        """Test complete workflow: create -> log -> validate -> snapshot -> complete."""
        # 1. Create session
        result = self._run_workflow_cmd("session-create", self.workflow_id, "auto")
        self.assertEqual(result.returncode, 0)
        
        data = json.loads(result.stdout)
        self.session_id = data.get("session_id")
        self.assertIsNotNone(self.session_id)
        
        # 2. Log step start
        result = self._run_workflow_cmd(
            "log-start", self.workflow_id, "orchestrator", "init", "Starting",
            "--session-id", self.session_id
        )
        self.assertEqual(result.returncode, 0)
        
        # 3. Log step end
        result = self._run_workflow_cmd(
            "log-end", self.workflow_id, "orchestrator", "init", "success", "Done",
            "--session-id", self.session_id
        )
        self.assertEqual(result.returncode, 0)
        
        # 4. Create test plan
        plan_path = os.path.join(self.test_dir, "test-plan.md")
        with open(plan_path, 'w') as f:
            f.write("""
# Test Plan

## Code Principles Adherence

### DRY
Reuse existing code.

### KISS
Simple solution.

### YAGNI
Only what's needed.

### SOLID
Single responsibility.

### SoC
Separation of concerns.

## Clean Code Compliance

### Small Functions
Under 20 lines.

### Descriptive Names
Clear names.

### Max 3 Parameters
Max 3 params.

### Early Return
Guard clauses.

### English Only
English code.

### Readability First
Readable code.

## Testing Strategy

### Given-When-Then
BDD pattern.

### Arrange-Act-Assert
AAA pattern.

### Test Names
Descriptive names.

## Implementation

User can login.
            """)
        
        # 5. Validate plan
        result = self._run_workflow_cmd(
            "validate-plan", plan_path,
            "--current-ac", "User can login"
        )
        self.assertEqual(result.returncode, 0)
        
        validation = json.loads(result.stdout)
        self.assertTrue(validation["is_valid"])
        
        # 6. Create snapshot
        result = self._run_workflow_cmd(
            "snapshot-create", self.session_id, "test-snap", self.test_dir
        )
        self.assertEqual(result.returncode, 0)
        
        # 7. List snapshots
        result = self._run_workflow_cmd("snapshot-list", self.session_id)
        self.assertEqual(result.returncode, 0)
        self.assertIn("test-snap", result.stdout)
        
        # 8. Complete session
        result = self._run_workflow_cmd("session-complete", self.session_id, "completed")
        self.assertEqual(result.returncode, 0)
        
        # 9. Verify session is completed
        result = self._run_state_cmd("session-get", self.session_id)
        session = json.loads(result.stdout)
        self.assertIsNone(session)  # Should be in history, not active
    
    def test_pause_and_resume_workflow(self):
        """Test pausing and resuming a workflow."""
        # Create session
        result = self._run_workflow_cmd("session-create", self.workflow_id, "auto")
        data = json.loads(result.stdout)
        self.session_id = data.get("session_id")
        
        # Pause
        result = self._run_workflow_cmd("session-pause", self.session_id, "test_pause")
        self.assertEqual(result.returncode, 0)
        
        # Verify paused
        result = self._run_state_cmd("session-get", self.session_id)
        session = json.loads(result.stdout)
        self.assertEqual(session["status"], "paused")
        
        # Resume
        result = self._run_workflow_cmd("session-resume", self.session_id)
        self.assertEqual(result.returncode, 0)
        
        # Verify running
        result = self._run_state_cmd("session-get", self.session_id)
        session = json.loads(result.stdout)
        self.assertEqual(session["status"], "running")
        
        # Cleanup
        self._run_workflow_cmd("session-complete", self.session_id, "completed")
    
    def test_rollback_workflow(self):
        """Test rollback functionality."""
        # Create session
        result = self._run_workflow_cmd("session-create", self.workflow_id, "auto")
        data = json.loads(result.stdout)
        self.session_id = data.get("session_id")
        
        # Create test file
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("original content")
        
        # Create snapshot
        result = self._run_workflow_cmd(
            "snapshot-create", self.session_id, "snap1", self.test_dir
        )
        self.assertEqual(result.returncode, 0)
        
        # Modify file
        with open(test_file, 'w') as f:
            f.write("modified content")
        
        # Rollback
        restore_dir = os.path.join(self.test_dir, "restore")
        result = self._run_workflow_cmd(
            "rollback", self.session_id, "--target-dir", restore_dir
        )
        self.assertEqual(result.returncode, 0)
        
        # Verify restored content
        restored_file = os.path.join(restore_dir, os.path.basename(self.test_dir), "test.txt")
        with open(restored_file) as f:
            content = f.read()
        self.assertEqual(content, "original content")
        
        # Cleanup
        self._run_workflow_cmd("session-complete", self.session_id, "completed")
    
    def test_session_list_and_status(self):
        """Test session listing and status commands."""
        # Create multiple sessions
        result1 = self._run_workflow_cmd("session-create", f"{self.workflow_id}-1", "auto")
        result2 = self._run_workflow_cmd("session-create", f"{self.workflow_id}-2", "plan")
        
        sid1 = json.loads(result1.stdout)["session_id"]
        sid2 = json.loads(result2.stdout)["session_id"]
        
        # List all
        result = self._run_workflow_cmd("session-list")
        self.assertEqual(result.returncode, 0)
        # Workflow IDs are truncated to 15 chars in display, check session IDs instead
        self.assertIn(sid1[:8], result.stdout)
        self.assertIn(sid2[:8], result.stdout)
        
        # Pause one
        self._run_workflow_cmd("session-pause", sid2, "test")
        
        # List by status
        result = self._run_workflow_cmd("session-list", "running")
        self.assertIn(sid1[:8], result.stdout)
        self.assertNotIn(sid2[:8], result.stdout)
        
        result = self._run_workflow_cmd("session-list", "paused")
        self.assertNotIn(sid1[:8], result.stdout)
        self.assertIn(sid2[:8], result.stdout)
        
        # Status
        result = self._run_workflow_cmd("status")
        self.assertEqual(result.returncode, 0)
        
        # Cleanup
        self._run_workflow_cmd("session-complete", sid1, "completed")
        self._run_workflow_cmd("session-complete", sid2, "completed")


if __name__ == '__main__':
    unittest.main()
