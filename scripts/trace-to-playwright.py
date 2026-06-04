#!/usr/bin/env python3
"""
trace-to-playwright.py — Converte test_trace JSON do e2e-runner em spec Playwright.

Uso:
  python3 trace-to-playwright.py --trace <trace.json> --output <spec.ts>
  python3 trace-to-playwright.py --trace <trace.json> --output <spec.ts> --run
  python3 trace-to-playwright.py --trace <trace.json> --output <spec.ts> --validate
"""

import json
import os
import re
import subprocess
import sys

PLAYWRIGHT_DIR = os.path.expanduser("~/Development/teamwill/mobilize/playwright")


def js_literal(s, allow_interp=False):
    """Wrap a string as a TypeScript template literal.
    If allow_interp=True, preserve ${...} for template interpolation."""
    if allow_interp:
        # Only escape backticks and backslashes, not ${
        escaped = s.replace("\\", "\\\\").replace("`", "\\`")
    else:
        escaped = s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return f"`{escaped}`"


def sel_literal(sel):
    """Wrap a selector string, replacing {deal_id} with ${dealId} for interpolation."""
    has_deal = "{deal_id}" in sel
    processed = sel.replace("{deal_id}", "${dealId}")
    return js_literal(processed, allow_interp=has_deal)


def action_to_code(action):
    """Convert a trace action dict into Playwright code line."""
    t = action.get("action", "navigate")
    sel = action.get("selector", "")
    url = action.get("url", "")
    value = action.get("value", "")

    if t == "navigate":
        u = url.replace("{deal_id}", "${dealId}")
        return f"    await page.goto({js_literal(u, allow_interp=True)})"
    elif t == "click":
        return f"    await page.locator({sel_literal(sel)}).click()"
    elif t in ("fill", "type"):
        return f"    await page.locator({sel_literal(sel)}).fill({js_literal(value)})"
    elif t == "wait":
        return f"    await page.locator({sel_literal(sel)}).waitFor({{state: 'visible', timeout: 5000}})"
    elif t == "wait_hidden":
        return f"    await page.locator({sel_literal(sel)}).waitFor({{state: 'hidden', timeout: 5000}})"
    elif t == "wait_url":
        u = url.replace("{deal_id}", "${dealId}")
        return f"    await page.waitForURL({js_literal(u, allow_interp=True)}, {{timeout: 10000}})"
    elif t == "assert_visible":
        return f"    await expect(page.locator({sel_literal(sel)})).toBeVisible()"
    elif t == "assert_not_visible":
        return f"    await expect(page.locator({sel_literal(sel)})).not.toBeVisible()"
    elif t == "assert_text":
        return f"    await expect(page.locator({sel_literal(sel)})).toHaveText({js_literal(value)})"
    elif t == "assert_count":
        return f"    await expect(page.locator({sel_literal(sel)})).toHaveCount({action.get('count', 1)})"
    elif t == "screenshot":
        return f"    await page.screenshot({{path: {js_literal('reports/' + action['path'])}, fullPage: true}})"
    else:
        return f"    // Unknown action: {json.dumps(action)}"


def generate_trace(trace, output_path):
    """Generate a Playwright spec file from a test_trace JSON."""
    ticket_id = trace.get("ticket_id", "UNKNOWN")
    title = trace.get("title", "Auto-generated regression test")
    ac_summary = trace.get("ac_summary", [])
    page_elements = trace.get("page_elements", {})
    tests = trace.get("tests", [])

    os.makedirs(os.path.join(PLAYWRIGHT_DIR, "reports", ticket_id), exist_ok=True)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    # Header comment with AC summary
    header_lines = [
        f"// {ticket_id}: {title}",
        "// Generated from E2E validation trace",
    ]
    for ac in ac_summary:
        status = "PASS" if ac.get("passed", True) else "FAIL"
        header_lines.append(f"//   {ac.get('id', '?')}: {ac.get('description', '?')} ({status})")

    # Page element constants
    elem_consts = []
    for name, selector in page_elements.items():
        key = re.sub(r'[^a-zA-Z0-9_]', '_', name.upper())
        key = re.sub(r'_+', '_', key).strip('_')
        if not key:
            key = "ELEM"
        elem_consts.append(f"const {key} = {js_literal(selector)}")

    # Test blocks
    test_blocks = []
    for t in tests:
        desc = t.get("description", "Validation")
        steps = t.get("steps", [])
        step_lines = [action_to_code(s) for s in steps]
        steps_str = "\n".join(step_lines)

        block = (
            f"  test({js_literal(desc)}, async ({{ page }}) => {{\n"
            f"{steps_str}\n"
            f"  }})"
        )
        test_blocks.append(block)

    blocks_str = "\n\n".join(test_blocks)
    elem_consts_str = "\n".join(elem_consts)

    lines = [
        "import { test, expect } from '@playwright/test'",
        "import { DealCreatePage } from '../page-objects'",
        "",
        "test.use({ storageState: 'auth.json' })",
        "",
        *header_lines,
        "",
        elem_consts_str,
        "",
        f"test.describe({js_literal(f'{ticket_id}: {title}')}, () => {{",
        "  let dealId: string",
        "",
        "  test.beforeEach(async ({ page }) => {",
        "    const create = new DealCreatePage(page)",
        "    await create.createAnonymousDeal()",
        "    // Get deal ID from current URL",
        "    const match = page.url().match(/\\/deal\\/(\\d+)/)",
        "    if (match) dealId = match[1]",
        "  })",
        "",
        blocks_str,
        "",
        "  test.afterEach(async ({ page }, testInfo) => {",
        f"    await page.screenshot({{path: `reports/{ticket_id}/${{testInfo.title.replace(/\\s+/g, '-')}}.png`, fullPage: true}})",
        "  })",
        "})",
        "",
    ]

    spec = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(spec)

    print(f"  ✓ Spec gerado: {output_path}")
    return True


def validate(output_path):
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--strict", "false", output_path],
            capture_output=True, text=True, timeout=30,
            cwd=PLAYWRIGHT_DIR,
        )
        if result.returncode == 0:
            print(f"  ✓ Validação sintaxe: OK")
            return True
        else:
            print(f"  ⚠ Validação: {result.returncode} issues")
            for line in result.stdout.splitlines()[:8]:
                print(f"    {line}")
            return False
    except FileNotFoundError:
        print(f"  ⚠ tsc não encontrado, a saltar validação")
        return True
    except Exception as e:
        print(f"  ⚠ Erro validação: {e}")
        return True


def run_test(output_path):
    test_file = os.path.relpath(output_path, PLAYWRIGHT_DIR)
    try:
        result = subprocess.run(
            ["npx", "playwright", "test", test_file, "--reporter=list"],
            capture_output=True, text=True, timeout=120000,
            cwd=PLAYWRIGHT_DIR,
        )
        passed = result.returncode == 0
        if passed:
            print(f"  ✓ Teste executado: PASS")
        else:
            print(f"  ✗ Teste executado: FAIL")
        # Show last 3 relevant lines
        lines = result.stdout.splitlines()
        for line in lines[-5:]:
            if line.strip():
                print(f"    {line.strip()}")
        return passed
    except subprocess.TimeoutExpired:
        print(f"  ✗ Teste: timeout (120s)")
        return False
    except Exception as e:
        print(f"  ✗ Teste: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert test_trace to Playwright spec")
    parser.add_argument("--trace", required=True, help="Path to trace JSON file")
    parser.add_argument("--output", required=True, help="Output spec.ts path")
    parser.add_argument("--run", action="store_true", help="Execute the generated test")
    parser.add_argument("--validate", action="store_true", help="Validate syntax with tsc")
    args = parser.parse_args()

    if not os.path.isfile(args.trace):
        print(f"  ✗ Trace não encontrado: {args.trace}")
        sys.exit(1)

    with open(args.trace) as f:
        trace = json.load(f)

    if "test_trace" in trace:
        trace = trace["test_trace"]

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    generate_trace(trace, args.output)

    if args.validate:
        validate(args.output)

    if args.run:
        success = run_test(args.output)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
