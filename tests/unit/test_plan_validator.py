#!/usr/bin/env python3
"""
Test suite for plan-validator.py.
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
    "plan_validator",
    os.path.join(scripts_dir, "plan-validator.py")
)
plan_validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan_validator)


class TestPlanValidator(unittest.TestCase):
    """Test cases for plan-validator.py."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_plan = tempfile.mktemp(suffix='.md')
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_plan):
            os.remove(self.test_plan)
    
    def _write_plan(self, content: str):
        """Helper to write plan content."""
        with open(self.test_plan, 'w') as f:
            f.write(content)
    
    def test_validate_complete_plan(self):
        """Test validating a complete, high-quality plan."""
        self._write_plan("""
# Test Plan

## Code Principles Adherence

### DRY
We will reuse existing utilities from shared/utils/ instead of duplicating code.

### KISS
The solution uses a simple boolean toggle instead of a complex state machine.

### YAGNI
We only implement what the AC requires, nothing more.

### SOLID
Each component has a single responsibility: form handles input, service handles API.

### SoC
API calls go through bsClient, data in Pinia stores, logic in composables.

## Clean Code Compliance

### Small Functions
All functions are under 20 lines.

### Descriptive Names
Variables use descriptive names without abbreviations.

### Max 3 Parameters
Functions have at most 3 parameters.

### Early Return
Guard clauses used to reduce nesting.

### English Only
All code in English.

### Readability First
Code is clear and readable for humans.

## Testing Strategy

### Given-When-Then
Behavior tests use Given-When-Then pattern.

### Arrange-Act-Assert
Unit tests use Arrange-Act-Assert pattern.

### Test Names
Test names describe the scenario clearly.

## Implementation

The user can login with valid credentials.
When the user submits the form, the system validates the input.
Then the system calls the API and shows the result.
        """)
        
        result = plan_validator.validate_plan(self.test_plan, "User can login with valid credentials")
        
        self.assertTrue(result["is_valid"])
        self.assertGreaterEqual(result["quality_score"], 70)
        self.assertEqual(len(result["issues"]), 0)
        self.assertEqual(result["principles"]["dry"], "ok")
        self.assertEqual(result["principles"]["kiss"], "ok")
    
    def test_validate_missing_sections(self):
        """Test validating a plan with missing sections."""
        self._write_plan("""
# Incomplete Plan

## Implementation

Some implementation details here.
        """)
        
        result = plan_validator.validate_plan(self.test_plan, "User can login")
        
        self.assertFalse(result["is_valid"])
        self.assertLess(result["quality_score"], 70)
        self.assertGreater(len(result["issues"]), 0)
        
        # Should have structure issues
        structure_issues = [i for i in result["issues"] if "[STRUCTURE]" in i]
        self.assertGreater(len(structure_issues), 0)
    
    def test_validate_missing_file(self):
        """Test validating a non-existent plan file."""
        result = plan_validator.validate_plan("/nonexistent/plan.md", "User can login")
        
        self.assertFalse(result["is_valid"])
        self.assertEqual(result["quality_score"], 0)
    
    def test_ac_coverage(self):
        """Test AC coverage detection."""
        self._write_plan("""
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

The user can login with valid credentials.
The system validates the input form.
        """)
        
        result = plan_validator.validate_plan(
            self.test_plan,
            "User can login with valid credentials",
            ["User can login with valid credentials", "System validates input form"]
        )
        
        self.assertEqual(result["coverage_score"], 100)
    
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        self._write_plan("""
# Minimal Plan

## Code Principles Adherence

### DRY
Reuse.

### KISS
Simple.

### YAGNI
Minimal.

### SOLID
Single.

### SoC
Separation.

## Clean Code Compliance

### Small Functions
Small.

### Descriptive Names
Names.

### Max 3 Parameters
Params.

### Early Return
Return.

### English Only
English.

### Readability First
Read.

## Testing Strategy

### Given-When-Then
GWT.

### Arrange-Act-Assert
AAA.

### Test Names
Names.

## Implementation

User login.
        """)
        
        result = plan_validator.validate_plan(self.test_plan, "User can login")
        
        # Score should be calculated based on multiple factors
        self.assertIn("quality_score", result)
        self.assertIn("coverage_score", result)
        self.assertIn("threshold", result)


if __name__ == '__main__':
    unittest.main()
