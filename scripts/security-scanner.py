#!/usr/bin/env python3
"""
security-scanner.py — Security vulnerability scanner for the workflow.

Scans for:
1. Dependency vulnerabilities (CVEs)
2. Hardcoded secrets/credentials
3. Common security anti-patterns
4. Pre-existing code security baseline
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Known secret patterns
SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|api[_-]?secret)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{20,}["\']?', "API Key"),
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{8,}["\']', "Password"),
    (r'(?i)(token|auth[_-]?token|access[_-]?token)\s*[=:]\s*["\']?[A-Za-z0-9_\-\.]{20,}["\']?', "Auth Token"),
    (r'(?i)(private[_-]?key|secret[_-]?key)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{20,}["\']?', "Private/Secret Key"),
    (r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----', "Private Key Block"),
    (r'(?i)(aws[_-]?access[_-]?key[_-]?id|aws[_-]?secret[_-]?access[_-]?key)\s*[=:]\s*["\']?[A-Z0-9]{20}["\']?', "AWS Credentials"),
    (r'(?i)(database[_-]?url|db[_-]?url|connection[_-]?string)\s*[=:]\s*["\'][^"\']+["\']', "Database Connection String"),
    (r'(?i)(jwt[_-]?secret|jwt[_-]?key)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{20,}["\']?', "JWT Secret"),
]

# Security anti-patterns
SECURITY_ANTIPATTERNS = [
    (r'eval\s*\(', "Use of eval() - code injection risk", "HIGH"),
    (r'exec\s*\(', "Use of exec() - code injection risk", "HIGH"),
    (r'os\.system\s*\(', "Use of os.system() - command injection risk", "HIGH"),
    (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "subprocess with shell=True - command injection risk", "HIGH"),
    (r'pickle\.loads?\s*\(', "Use of pickle - deserialization attack risk", "MEDIUM"),
    (r'yaml\.load\s*\([^)]*Loader\s*=\s*yaml\.Loader', "yaml.load with unsafe Loader", "MEDIUM"),
    (r'requests\.get\s*\([^)]*verify\s*=\s*False', "SSL verification disabled", "MEDIUM"),
    (r'urllib\.request\.urlopen\s*\([^)]*context\s*=\s*ssl\._create_unverified_context', "SSL verification disabled", "MEDIUM"),
    (r'\.innerHTML\s*=', "Direct innerHTML assignment - XSS risk", "MEDIUM"),
    (r'document\.write\s*\(', "Use of document.write() - XSS risk", "MEDIUM"),
    (r'localStorage\.setItem\s*\([^)]*token', "Token in localStorage - XSS theft risk", "MEDIUM"),
    (r'SELECT\s+\*\s+FROM.*\+', "Potential SQL injection", "HIGH"),
    (r'f["\'].*\{.*\}.*["\'].*%.*\(', "Potential format string injection", "LOW"),
]

# File extensions to scan
SCANNABLE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.kt', '.go', '.rs',
    '.rb', '.php', '.cs', '.cpp', '.c', '.h', '.hpp', '.vue', '.svelte',
    '.yaml', '.yml', '.json', '.env', '.properties', '.conf', '.config',
    '.xml', '.gradle', '.maven', '.pom', '.sql'
}

# Directories to skip
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.next', 'dist', 'build',
    'venv', 'env', '.venv', 'target', 'bin', 'obj', 'coverage',
    '.nuxt', '.output', '.vercel', '.netlify', 'vendor', 'tmp', 'temp'
}


class SecurityScanner:
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)
        self.findings: List[Dict[str, Any]] = []
        self.scanned_files = 0
        self.skipped_files = 0
    
    def scan_all(self) -> Dict[str, Any]:
        """Run all security scans."""
        self._scan_files()
        dependency_findings = self._check_dependencies()
        
        return {
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "project_root": self.project_root,
            "summary": {
                "files_scanned": self.scanned_files,
                "files_skipped": self.skipped_files,
                "total_findings": len(self.findings) + len(dependency_findings),
                "by_severity": self._count_by_severity(self.findings + dependency_findings),
            },
            "findings": self.findings + dependency_findings,
            "passed": len([f for f in self.findings + dependency_findings if f["severity"] in ["CRITICAL", "HIGH"]]) == 0
        }
    
    def _count_by_severity(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count findings by severity."""
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for f in findings:
            sev = f.get("severity", "INFO")
            if sev in counts:
                counts[sev] += 1
        return counts
    
    def _scan_files(self):
        """Scan all scannable files for secrets and anti-patterns."""
        for root, dirs, files in os.walk(self.project_root):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext not in SCANNABLE_EXTENSIONS:
                    self.skipped_files += 1
                    continue
                
                filepath = os.path.join(root, file)
                try:
                    self._scan_file(filepath)
                    self.scanned_files += 1
                except Exception:
                    self.skipped_files += 1
    
    def _scan_file(self, filepath: str):
        """Scan a single file for security issues."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return
        
        rel_path = os.path.relpath(filepath, self.project_root)
        
        # Check for secrets
        for pattern, secret_type in SECRET_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.findings.append({
                    "type": "secret",
                    "severity": "CRITICAL",
                    "file": rel_path,
                    "line": line_num,
                    "match": secret_type,
                    "snippet": self._get_line_snippet(content, line_num),
                    "message": f"Potential {secret_type} hardcoded in source"
                })
        
        # Check for anti-patterns
        for pattern, message, severity in SECURITY_ANTIPATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                self.findings.append({
                    "type": "antipattern",
                    "severity": severity,
                    "file": rel_path,
                    "line": line_num,
                    "match": match.group()[:50],
                    "snippet": self._get_line_snippet(content, line_num),
                    "message": message
                })
    
    def _get_line_snippet(self, content: str, line_num: int, context: int = 1) -> str:
        """Get a snippet of code around a line number."""
        lines = content.split('\n')
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)
        snippet_lines = []
        for i in range(start, end):
            marker = ">>> " if i == line_num - 1 else "    "
            snippet_lines.append(f"{marker}{i+1:4d} | {lines[i][:100]}")
        return "\n".join(snippet_lines)
    
    def _check_dependencies(self) -> List[Dict[str, Any]]:
        """Check for dependency vulnerabilities."""
        findings = []
        
        # Check npm/yarn
        package_json = os.path.join(self.project_root, "package.json")
        if os.path.exists(package_json):
            findings.extend(self._check_npm_vulnerabilities())
        
        # Check Python requirements
        requirements = os.path.join(self.project_root, "requirements.txt")
        if os.path.exists(requirements):
            findings.extend(self._check_python_vulnerabilities())
        
        # Check Java/Maven
        pom_xml = os.path.join(self.project_root, "pom.xml")
        if os.path.exists(pom_xml):
            findings.append({
                "type": "dependency",
                "severity": "INFO",
                "file": "pom.xml",
                "message": "Maven project detected. Run 'mvn dependency:analyze' and OWASP dependency-check for full audit."
            })
        
        return findings
    
    def _check_npm_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Check npm dependencies for vulnerabilities."""
        findings = []
        
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                try:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("vulnerabilities", {})
                    
                    for pkg_name, vuln_data in vulnerabilities.items():
                        severity = vuln_data.get("severity", "unknown").upper()
                        if severity in ["CRITICAL", "HIGH"]:
                            findings.append({
                                "type": "dependency",
                                "severity": severity,
                                "package": pkg_name,
                                "message": f"Vulnerable dependency: {pkg_name} ({severity})",
                                "details": vuln_data.get("title", ""),
                                "fix_available": vuln_data.get("fixAvailable", False)
                            })
                except json.JSONDecodeError:
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            findings.append({
                "type": "dependency",
                "severity": "INFO",
                "message": "npm audit not available. Install npm and run 'npm audit' manually."
            })
        
        return findings
    
    def _check_python_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Check Python dependencies for vulnerabilities."""
        findings = []
        
        # Try safety if available
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                try:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        findings.append({
                            "type": "dependency",
                            "severity": "HIGH",
                            "package": vuln.get("package_name", "unknown"),
                            "message": f"Vulnerable Python package: {vuln.get('package_name')}",
                            "details": vuln.get("vulnerability", ""),
                            "cve": vuln.get("cve", "")
                        })
                except json.JSONDecodeError:
                    pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            findings.append({
                "type": "dependency",
                "severity": "INFO",
                "message": "safety not available. Install with 'pip install safety' for Python vulnerability scanning."
            })
        
        return findings


def baseline_scan(project_root: str, output_file: Optional[str] = None) -> Dict[str, Any]:
    """Run a baseline security scan."""
    scanner = SecurityScanner(project_root)
    results = scanner.scan_all()
    
    if output_file:
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results


def compare_scans(baseline_file: str, current_results: Dict[str, Any]) -> Dict[str, Any]:
    """Compare baseline scan with current scan."""
    try:
        with open(baseline_file, 'r') as f:
            baseline = json.load(f)
    except Exception:
        return {"error": "Could not load baseline file"}
    
    baseline_findings = {(f["file"], f["line"], f["message"]) for f in baseline.get("findings", [])}
    current_findings = {(f["file"], f["line"], f["message"]) for f in current_results.get("findings", [])}
    
    new_findings = current_findings - baseline_findings
    fixed_findings = baseline_findings - current_findings
    
    return {
        "new_issues": len(new_findings),
        "fixed_issues": len(fixed_findings),
        "new_findings": [
            f for f in current_results.get("findings", [])
            if (f["file"], f["line"], f["message"]) in new_findings
        ],
        "fixed_findings": [
            f for f in baseline.get("findings", [])
            if (f["file"], f["line"], f["message"]) in fixed_findings
        ],
        "regression": len(new_findings) > 0
    }


def main():
    parser = argparse.ArgumentParser(description="Security vulnerability scanner")
    parser.add_argument("command", choices=["scan", "baseline", "compare"])
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--baseline", help="Baseline file for comparison")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        scanner = SecurityScanner(args.project_root)
        results = scanner.scan_all()
        
        if args.output:
            os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        if args.format == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"  Security Scan Report")
            print(f"{'='*60}")
            print(f"  Files scanned: {results['summary']['files_scanned']}")
            print(f"  Total findings: {results['summary']['total_findings']}")
            print(f"  By severity:")
            for sev, count in results['summary']['by_severity'].items():
                if count > 0:
                    print(f"    {sev}: {count}")
            print(f"  Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}")
            print(f"{'='*60}\n")
        
        # Exit with error if critical/high findings
        critical_high = results['summary']['by_severity'].get('CRITICAL', 0) + results['summary']['by_severity'].get('HIGH', 0)
        sys.exit(0 if critical_high == 0 else 1)
    
    elif args.command == "baseline":
        if not args.output:
            print("Error: --output required for baseline", file=sys.stderr)
            sys.exit(1)
        
        results = baseline_scan(args.project_root, args.output)
        print(f"Baseline saved to {args.output}")
        print(f"Files scanned: {results['summary']['files_scanned']}")
        print(f"Findings: {results['summary']['total_findings']}")
    
    elif args.command == "compare":
        if not args.baseline:
            print("Error: --baseline required for compare", file=sys.stderr)
            sys.exit(1)
        
        scanner = SecurityScanner(args.project_root)
        current = scanner.scan_all()
        comparison = compare_scans(args.baseline, current)
        
        print(json.dumps(comparison, indent=2, ensure_ascii=False))
        
        if comparison.get("regression"):
            sys.exit(1)


if __name__ == "__main__":
    main()
