#!/usr/bin/env python3
"""
plan-validator.py — Validação avançada de planos usando LLM.

Analisa qualidade, cobertura de ACs, princípios de código, e clareza.
Retorna score de qualidade + feedback específico.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Dict, Any, List, Tuple

# Thresholds
MIN_QUALITY_SCORE = 70
REQUIRED_SECTIONS = [
    "Code Principles Adherence",
    "Clean Code Compliance",
    "Testing Strategy",
]


def read_plan(plan_path: str) -> str:
    """Read plan content from file."""
    if not os.path.exists(plan_path):
        return ""
    with open(plan_path, "r", encoding="utf-8") as f:
        return f.read()


def check_required_sections(plan_content: str) -> Tuple[bool, List[str]]:
    """Check if plan has all required sections."""
    issues = []
    for section in REQUIRED_SECTIONS:
        if section not in plan_content:
            issues.append(f"[STRUCTURE] Missing required section: '{section}'")
    return len(issues) == 0, issues


def check_ac_coverage(plan_content: str, current_ac: str, acceptance_criteria: List[str]) -> Tuple[bool, List[str], int]:
    """Check if plan covers all acceptance criteria."""
    issues = []
    
    if not current_ac and not acceptance_criteria:
        return True, [], 100
    
    # For bug tickets without ACs, check if description is referenced
    if not acceptance_criteria and current_ac:
        if "bug" in current_ac.lower() or "fix" in current_ac.lower():
            if "description" in plan_content.lower() or "bug" in plan_content.lower():
                return True, [], 100
    
    # Check each AC is mentioned in the plan
    acs_to_check = acceptance_criteria if acceptance_criteria else [current_ac]
    covered = 0
    
    for ac in acs_to_check:
        # Look for AC keywords in plan
        ac_keywords = re.findall(r'\b\w+\b', ac.lower())
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'user', 'system', 'when', 'then', 'that', 'this', 'these', 'those', 'it', 'its'}
        significant_keywords = [w for w in ac_keywords if w not in stop_words and len(w) > 3]
        
        found = sum(1 for kw in significant_keywords if kw in plan_content.lower())
        coverage = found / len(significant_keywords) if significant_keywords else 0
        
        if coverage >= 0.5:  # At least 50% of significant keywords found
            covered += 1
        else:
            issues.append(f"[COVERAGE] AC not adequately covered: '{ac[:80]}...'")
    
    total = len(acs_to_check)
    score = int((covered / total) * 100) if total > 0 else 100
    return covered == total, issues, score


def check_code_principles(plan_content: str) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Validate code principles are documented and applied."""
    issues = []
    principles = {}
    
    # Check DRY
    if "DRY" in plan_content or "Don't Repeat Yourself" in plan_content:
        if "reutiliz" in plan_content.lower() or "reus" in plan_content.lower() or "existing" in plan_content.lower():
            principles["dry"] = "ok"
        else:
            principles["dry"] = {"issue": "DRY section exists but doesn't demonstrate reuse of existing code"}
            issues.append("[PRINCIPLE] DRY: No evidence of code reuse analysis")
    else:
        principles["dry"] = {"issue": "Missing DRY analysis"}
        issues.append("[PRINCIPLE] Missing DRY section")
    
    # Check KISS
    if "KISS" in plan_content or "Keep It Simple" in plan_content:
        if "simple" in plan_content.lower() or "straightforward" in plan_content.lower():
            principles["kiss"] = "ok"
        else:
            principles["kiss"] = {"issue": "KISS section exists but doesn't justify simplicity"}
            issues.append("[PRINCIPLE] KISS: No justification for approach simplicity")
    else:
        principles["kiss"] = {"issue": "Missing KISS analysis"}
        issues.append("[PRINCIPLE] Missing KISS section")
    
    # Check YAGNI
    if "YAGNI" in plan_content or "You Aren't Gonna Need It" in plan_content:
        if "only" in plan_content.lower() or "just" in plan_content.lower() or "minimal" in plan_content.lower():
            principles["yagni"] = "ok"
        else:
            principles["yagni"] = {"issue": "YAGNI section exists but doesn't show restraint"}
            issues.append("[PRINCIPLE] YAGNI: No evidence of implementing only what's needed")
    else:
        principles["yagni"] = {"issue": "Missing YAGNI analysis"}
        issues.append("[PRINCIPLE] Missing YAGNI section")
    
    # Check SOLID
    if "SOLID" in plan_content:
        if "responsibility" in plan_content.lower() or "single" in plan_content.lower():
            principles["solid"] = "ok"
        else:
            principles["solid"] = {"issue": "SOLID section exists but doesn't address single responsibility"}
            issues.append("[PRINCIPLE] SOLID: No single responsibility analysis")
    else:
        principles["solid"] = {"issue": "Missing SOLID analysis"}
        issues.append("[PRINCIPLE] Missing SOLID section")
    
    # Check SoC
    if "SoC" in plan_content or "Separation of Concerns" in plan_content:
        if "layer" in plan_content.lower() or "separat" in plan_content.lower() or "client" in plan_content.lower():
            principles["soc"] = "ok"
        else:
            principles["soc"] = {"issue": "SoC section exists but doesn't show layer separation"}
            issues.append("[PRINCIPLE] SoC: No layer separation analysis")
    else:
        principles["soc"] = {"issue": "Missing SoC analysis"}
        issues.append("[PRINCIPLE] Missing SoC section")
    
    all_ok = all(p == "ok" for p in principles.values())
    return all_ok, issues, principles


def check_clean_code(plan_content: str) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Validate clean code practices."""
    issues = []
    clean_code = {}
    
    checks = [
        ("small_functions", ["<20", "20 lines", "small function", "short function"]),
        ("descriptive_names", ["descriptive", "meaningful", "clear name", "no abbrev"]),
        ("max_parameters", ["3 parameter", "max 3", "fewer than 4"]),
        ("early_return", ["early return", "guard clause", "guard"]),
        ("english_only", ["english", "in english", "english only"]),
        ("readability_first", ["readable", "readability", "clear", "human"]),
    ]
    
    for key, keywords in checks:
        found = any(kw in plan_content.lower() for kw in keywords)
        if found:
            clean_code[key] = "ok"
        else:
            clean_code[key] = {"issue": f"Missing {key.replace('_', ' ')} validation"}
            issues.append(f"[CLEAN_CODE] Missing {key.replace('_', ' ')} analysis")
    
    all_ok = all(c == "ok" for c in clean_code.values())
    return all_ok, issues, clean_code


def check_testing_strategy(plan_content: str) -> Tuple[bool, List[str], Dict[str, Any]]:
    """Validate testing strategy."""
    issues = []
    testing = {}
    
    checks = [
        ("given_when_then", ["given", "when", "then", "given-when-then"]),
        ("arrange_act_assert", ["arrange", "act", "assert", "arrange-act-assert"]),
        ("test_names", ["test name", "scenario", "should", "describes"]),
    ]
    
    for key, keywords in checks:
        found = any(kw in plan_content.lower() for kw in keywords)
        if found:
            testing[key] = "ok"
        else:
            testing[key] = {"issue": f"Missing {key.replace('_', ' ')} validation"}
            issues.append(f"[TESTING] Missing {key.replace('_', ' ')} analysis")
    
    all_ok = all(t == "ok" for t in testing.values())
    return all_ok, issues, testing


def calculate_quality_score(
    structure_ok: bool,
    coverage_score: int,
    principles: Dict[str, Any],
    clean_code: Dict[str, Any],
    testing: Dict[str, Any]
) -> int:
    """Calculate overall quality score (0-100)."""
    score = 0
    
    # Structure: 20 points
    if structure_ok:
        score += 20
    
    # Coverage: 30 points
    score += int((coverage_score / 100) * 30)
    
    # Principles: 20 points (4 each)
    principle_ok = sum(1 for p in principles.values() if p == "ok")
    score += principle_ok * 4
    
    # Clean Code: 15 points (2.5 each)
    clean_ok = sum(1 for c in clean_code.values() if c == "ok")
    score += int(clean_ok * 2.5)
    
    # Testing: 15 points (5 each)
    test_ok = sum(1 for t in testing.values() if t == "ok")
    score += test_ok * 5
    
    return min(score, 100)


def validate_plan(plan_path: str, current_ac: str = "", acceptance_criteria: List[str] = None) -> Dict[str, Any]:
    """Main validation function."""
    acceptance_criteria = acceptance_criteria or []
    
    plan_content = read_plan(plan_path)
    if not plan_content:
        return {
            "is_valid": False,
            "quality_score": 0,
            "issues": ["[FILE] Plan file not found or empty"],
            "principles": {},
            "clean_code": {},
            "testing": {},
            "coverage_score": 0,
        }
    
    # Run all checks
    structure_ok, structure_issues = check_required_sections(plan_content)
    coverage_ok, coverage_issues, coverage_score = check_ac_coverage(plan_content, current_ac, acceptance_criteria)
    principles_ok, principles_issues, principles = check_code_principles(plan_content)
    clean_ok, clean_issues, clean_code = check_clean_code(plan_content)
    testing_ok, testing_issues, testing = check_testing_strategy(plan_content)
    
    all_issues = structure_issues + coverage_issues + principles_issues + clean_issues + testing_issues
    
    quality_score = calculate_quality_score(structure_ok, coverage_score, principles, clean_code, testing)
    
    is_valid = quality_score >= MIN_QUALITY_SCORE and len(all_issues) == 0
    
    return {
        "is_valid": is_valid,
        "quality_score": quality_score,
        "issues": all_issues,
        "principles": principles,
        "clean_code": clean_code,
        "testing": testing,
        "coverage_score": coverage_score,
        "threshold": MIN_QUALITY_SCORE,
    }


def main():
    parser = argparse.ArgumentParser(description="Advanced Plan Validator")
    parser.add_argument("plan_path", help="Path to plan markdown file")
    parser.add_argument("--current-ac", default="", help="Current acceptance criteria text")
    parser.add_argument("--acs", nargs="*", default=[], help="List of acceptance criteria")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    
    args = parser.parse_args()
    
    result = validate_plan(args.plan_path, args.current_ac, args.acs)
    
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"  Plan Validation Report")
        print(f"{'='*60}")
        print(f"  Quality Score: {result['quality_score']}/100 (threshold: {result['threshold']})")
        print(f"  Valid: {'✅ YES' if result['is_valid'] else '❌ NO'}")
        print(f"  Coverage: {result['coverage_score']}%")
        print(f"\n  Principles:")
        for k, v in result['principles'].items():
            status = "✅" if v == "ok" else "❌"
            print(f"    {status} {k.upper()}")
        print(f"\n  Clean Code:")
        for k, v in result['clean_code'].items():
            status = "✅" if v == "ok" else "❌"
            print(f"    {status} {k.replace('_', ' ').title()}")
        print(f"\n  Testing:")
        for k, v in result['testing'].items():
            status = "✅" if v == "ok" else "❌"
            print(f"    {status} {k.replace('_', ' ').title()}")
        if result['issues']:
            print(f"\n  Issues ({len(result['issues'])}):")
            for issue in result['issues']:
                print(f"    • {issue}")
        print(f"\n{'='*60}\n")
    
    # Exit with error code if invalid
    sys.exit(0 if result['is_valid'] else 1)


if __name__ == "__main__":
    main()
