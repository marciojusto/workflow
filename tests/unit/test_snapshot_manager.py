#!/usr/bin/env python3
"""
Test suite for snapshot-manager.py.
"""

import json
import os
import sys
import tempfile
import unittest

# Add scripts to path
scripts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')
sys.path.insert(0, scripts_dir)

# Import module with hyphen using importlib
import importlib.util
spec = importlib.util.spec_from_file_location(
    "snapshot_manager",
    os.path.join(scripts_dir, "snapshot-manager.py")
)
snapshot_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot_manager)


class TestSnapshotManager(unittest.TestCase):
    """Test cases for snapshot-manager.py."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_snapshot_dir = tempfile.mkdtemp()
        snapshot_manager.SNAPSHOT_DIR = self.test_snapshot_dir
        
        self.test_source_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_source_dir, "test.txt")
        with open(self.test_file, 'w') as f:
            f.write("test content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        for d in [self.test_snapshot_dir, self.test_source_dir]:
            if os.path.exists(d):
                shutil.rmtree(d)
    
    def test_create_snapshot(self):
        """Test creating a snapshot."""
        meta = snapshot_manager.create_snapshot(
            "session-001",
            "snap-001",
            [self.test_source_dir]
        )
        
        self.assertEqual(meta["snapshot_id"], "snap-001")
        self.assertEqual(meta["session_id"], "session-001")
        
        # Check snapshot file exists
        snapshot_path = snapshot_manager.get_snapshot_path("session-001", "snap-001")
        self.assertTrue(os.path.exists(snapshot_path))
    
    def test_restore_snapshot(self):
        """Test restoring a snapshot."""
        # Create snapshot
        snapshot_manager.create_snapshot(
            "session-002",
            "snap-002",
            [self.test_source_dir]
        )
        
        # Delete original
        os.remove(self.test_file)
        
        # Restore
        restore_dir = tempfile.mkdtemp()
        success = snapshot_manager.restore_snapshot("session-002", "snap-002", restore_dir)
        
        self.assertTrue(success)
        
        # Check restored file
        restored_file = os.path.join(restore_dir, os.path.basename(self.test_source_dir), "test.txt")
        self.assertTrue(os.path.exists(restored_file))
    
    def test_list_snapshots(self):
        """Test listing snapshots."""
        snapshot_manager.create_snapshot("session-003", "snap-003a", [self.test_source_dir])
        snapshot_manager.create_snapshot("session-003", "snap-003b", [self.test_source_dir])
        
        snapshots = snapshot_manager.list_snapshots("session-003")
        self.assertEqual(len(snapshots), 2)
    
    def test_get_latest_snapshot(self):
        """Test getting latest snapshot."""
        import time
        snapshot_manager.create_snapshot("session-004", "snap-004a", [self.test_source_dir])
        time.sleep(0.1)  # Ensure different timestamps
        snapshot_manager.create_snapshot("session-004", "snap-004b", [self.test_source_dir])
        
        latest = snapshot_manager.get_latest_snapshot("session-004")
        self.assertEqual(latest["snapshot_id"], "snap-004b")
    
    def test_delete_snapshot(self):
        """Test deleting a snapshot."""
        snapshot_manager.create_snapshot("session-005", "snap-005", [self.test_source_dir])
        
        success = snapshot_manager.delete_snapshot("session-005", "snap-005")
        self.assertTrue(success)
        
        snapshots = snapshot_manager.list_snapshots("session-005")
        self.assertEqual(len(snapshots), 0)
    
    def test_cleanup_old_snapshots(self):
        """Test cleaning up old snapshots."""
        for i in range(7):
            snapshot_manager.create_snapshot("session-006", f"snap-{i}", [self.test_source_dir])
        
        deleted = snapshot_manager.cleanup_old_snapshots("session-006", keep_count=3)
        self.assertEqual(deleted, 4)
        
        snapshots = snapshot_manager.list_snapshots("session-006")
        self.assertEqual(len(snapshots), 3)
    
    def test_auto_snapshot_before_step(self):
        """Test automatic snapshot creation."""
        snapshot_id = snapshot_manager.auto_snapshot_before_step(
            "session-007",
            "execute-plan",
            [self.test_source_dir]
        )
        
        self.assertIsNotNone(snapshot_id)
        self.assertTrue(snapshot_id.startswith("auto_execute-plan_"))
        
        # Check snapshot exists
        snapshots = snapshot_manager.list_snapshots("session-007")
        self.assertEqual(len(snapshots), 1)
        self.assertTrue(snapshots[0]["metadata"]["auto"])
        self.assertEqual(snapshots[0]["metadata"]["step"], "execute-plan")
    
    def test_rollback_to_snapshot(self):
        """Test rollback to latest snapshot."""
        snapshot_manager.create_snapshot("session-008", "snap-008", [self.test_source_dir])
        
        restore_dir = tempfile.mkdtemp()
        success = snapshot_manager.rollback_to_snapshot("session-008", target_dir=restore_dir)
        
        self.assertTrue(success)
    
    def test_rollback_to_specific_snapshot(self):
        """Test rollback to specific snapshot."""
        snapshot_manager.create_snapshot("session-009", "snap-009a", [self.test_source_dir])
        snapshot_manager.create_snapshot("session-009", "snap-009b", [self.test_source_dir])
        
        restore_dir = tempfile.mkdtemp()
        success = snapshot_manager.rollback_to_snapshot("session-009", snapshot_id="snap-009a", target_dir=restore_dir)
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()
