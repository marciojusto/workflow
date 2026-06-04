#!/usr/bin/env python3
"""
Markdown to HTML Converter - Premium Dark Theme with Visual Diagrams
"""

import re
import sys
import os
from pathlib import Path
from datetime import datetime

PREMIUM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-deep: #0a0e14;
    --bg-primary: #0d1117;
    --bg-secondary: #131920;
    --bg-tertiary: #1a2129;
    --bg-elevated: #21262d;
    --border-subtle: #21262d;
    --border-default: #30363d;
    --border-strong: #484f58;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --text-tertiary: #6e7681;
    --text-muted: #484f58;
    --accent-blue: #58a6ff;
    --accent-cyan: #39c5cf;
    --accent-green: #3fb950;
    --accent-yellow: #d29922;
    --accent-orange: #db6d28;
    --accent-red: #f85149;
    --accent-purple: #a371f7;
    --accent-pink: #db61a2;
    --gradient-blue: linear-gradient(135deg, #1f6feb, #388bfd);
    --gradient-green: linear-gradient(135deg, #238636, #3fb950);
    --gradient-purple: linear-gradient(135deg, #a371f7, #db61a2);
    --gradient-orange: linear-gradient(135deg, #d29922, #db6d28);
    --gradient-cyan: linear-gradient(135deg, #0891b2, #39c5cf);
    --glow-blue: rgba(56, 139, 253, 0.3);
    --glow-green: rgba(63, 185, 80, 0.25);
    --glow-purple: rgba(163, 113, 247, 0.25);
    --glow-orange: rgba(219, 109, 40, 0.25);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-deep);
    color: var(--text-primary);
    line-height: 1.7;
    font-size: 15px;
    min-height: 100vh;
}

/* ============ APP CONTAINER ============ */
.app-container { display: flex; min-height: 100vh; }

/* ============ SIDEBAR ============ */
.sidebar {
    width: 280px; background: var(--bg-primary);
    border-right: 1px solid var(--border-subtle);
    position: fixed; height: 100vh; overflow-y: auto;
    z-index: 100; padding: 0;
}
.sidebar-header {
    padding: 24px 24px 20px;
    border-bottom: 1px solid var(--border-subtle);
}
.sidebar-logo {
    display: flex; align-items: center; gap: 12px;
}
.sidebar-logo-icon {
    width: 40px; height: 40px;
    background: var(--gradient-blue);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 4px 20px var(--glow-blue);
}
.sidebar-logo-text {
    font-size: 18px; font-weight: 700;
    background: var(--gradient-blue);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sidebar-version {
    display: inline-block; margin-top: 8px;
    padding: 4px 10px; background: var(--bg-tertiary);
    border-radius: 20px; font-size: 11px;
    color: var(--text-tertiary); font-weight: 500;
}
.sidebar-section {
    padding: 16px 12px 8px;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 1px;
    color: var(--text-muted);
}
.sidebar-nav { padding: 4px 8px; }
.nav-link {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 8px;
    color: var(--text-secondary); text-decoration: none;
    font-size: 14px; font-weight: 500;
    transition: all 0.2s; margin: 2px 0;
    cursor: pointer;
}
.nav-link:hover {
    background: var(--bg-secondary); color: var(--text-primary);
}
.nav-link.active {
    background: rgba(31, 111, 235, 0.15);
    color: var(--accent-blue);
    border: 1px solid rgba(56, 139, 253, 0.3);
}
.nav-link.nav-h2 { padding-left: 28px; font-size: 13px; }
.nav-icon { font-size: 16px; width: 24px; text-align: center; }

/* ============ MAIN ============ */
.main-content { flex: 1; margin-left: 280px; }

/* ============ HERO ============ */
.hero {
    background: linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
    padding: 60px 50px 40px;
    border-bottom: 1px solid var(--border-subtle);
    position: relative; overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -100px; left: -100px; right: -100px;
    height: 400px;
    background:
        radial-gradient(ellipse 600px 300px at 30% 0%, rgba(56,139,253,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 400px 200px at 70% 0%, rgba(163,113,247,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-content { max-width: 800px; position: relative; z-index: 1; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 14px; background: var(--bg-tertiary);
    border-radius: 20px; font-size: 12px;
    color: var(--text-secondary); margin-bottom: 20px;
}
.hero-title {
    font-size: 44px; font-weight: 800; margin-bottom: 16px;
    line-height: 1.15;
}
.hero-title-gradient {
    background: linear-gradient(135deg, #58a6ff, #39c5cf, #a371f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-desc {
    font-size: 18px; color: var(--text-secondary); max-width: 600px;
}
.hero-meta {
    display: flex; gap: 24px; margin-top: 24px;
    flex-wrap: wrap;
}
.hero-meta-item {
    display: flex; align-items: center; gap: 8px;
    font-size: 13px; color: var(--text-tertiary);
}

/* ============ CONTENT ============ */
.content { padding: 50px; max-width: 960px; }

/* ============ SECTION CARDS ============ */
.section-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 32px;
    margin: 32px 0;
}

/* ============ HEADINGS ============ */
h1 {
    font-size: 38px; font-weight: 700; margin: 0 0 24px;
    color: var(--accent-blue);
}
h2 {
    font-size: 28px; font-weight: 600; margin: 48px 0 20px;
    color: var(--text-primary);
    display: flex; align-items: center; gap: 12px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-subtle);
    scroll-margin-top: 20px;
}
h2 .h2-number {
    font-size: 14px; font-weight: 700;
    background: var(--accent-blue); color: var(--bg-deep);
    padding: 4px 10px; border-radius: 6px;
}
h2::after {
    content: '';
    flex: 1; height: 1px;
    background: var(--border-subtle);
}
h3 {
    font-size: 21px; font-weight: 600; margin: 32px 0 16px;
    color: var(--text-primary);
    scroll-margin-top: 20px;
}
h4 {
    font-size: 17px; font-weight: 600; margin: 24px 0 12px;
    color: var(--text-primary);
    scroll-margin-top: 20px;
}
p { margin: 16px 0; color: var(--text-secondary); }
a { color: var(--accent-blue); text-decoration: none; }
a:hover { color: var(--accent-cyan); }

/* ============ WORKFLOW DIAGRAM ============ */
.workflow-section { margin: 32px 0; }
.workflow-section h2 { margin-top: 0; }
.workflow-visual {
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 40px 32px;
    margin: 24px 0;
    overflow-x: auto;
}
.workflow-diagram {
    display: flex; align-items: center; justify-content: center;
    gap: 4px; flex-wrap: nowrap;
    min-width: 700px;
}
.workflow-step {
    display: flex; flex-direction: column; align-items: center;
    gap: 8px; flex-shrink: 0;
}
.flow-node {
    width: 96px; padding: 16px 8px;
    border-radius: 14px;
    display: flex; flex-direction: column; align-items: center;
    text-align: center; gap: 4px;
    position: relative;
    transition: all 0.3s ease;
    cursor: default;
}
.flow-node:hover {
    transform: translateY(-4px);
}
.flow-node::after {
    content: ''; position: absolute; inset: -3px;
    border-radius: 17px; opacity: 0;
    transition: opacity 0.3s;
}
.flow-node:hover::after { opacity: 1; }
.flow-icon { font-size: 22px; }
.flow-label { font-size: 10px; font-weight: 600; color: #fff; line-height: 1.2; }
.flow-meta { font-size: 8px; color: rgba(255,255,255,0.7); }

.node-user { background: var(--gradient-blue); width: 110px; }
.node-user::after { box-shadow: 0 0 25px var(--glow-blue); }
.node-orch { background: linear-gradient(135deg, #6366f1, #818cf8); padding: 14px 8px; }
.node-orch::after { box-shadow: 0 0 25px rgba(99,102,241,0.3); }
.node-keeper { background: var(--gradient-green); }
.node-keeper::after { box-shadow: 0 0 25px var(--glow-green); }
.node-expert { background: var(--gradient-purple); }
.node-expert::after { box-shadow: 0 0 25px var(--glow-purple); }
.node-skill { background: var(--gradient-cyan); }
.node-skill::after { box-shadow: 0 0 25px rgba(57,197,207,0.3); }
.node-runner { background: var(--gradient-orange); }
.node-runner::after { box-shadow: 0 0 25px var(--glow-orange); }

.flow-arrow {
    font-size: 18px; color: var(--text-muted);
    flex-shrink: 0;
    animation: arrowPulse 2s ease-in-out infinite;
}
.flow-line {
    width: 40px; height: 2px;
    background: var(--border-default);
    flex-shrink: 0; position: relative;
}
.flow-line::after {
    content: '▶';
    position: absolute; right: -6px; top: -6px;
    font-size: 10px; color: var(--text-tertiary);
}
@keyframes arrowPulse {
    0%, 100% { opacity: 0.4; transform: translateX(0); }
    50% { opacity: 1; transform: translateX(3px); }
}

/* Workflow details grid */
.wf-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin: 24px 0;
}
.wf-card {
    background: var(--bg-deep);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 16px;
    transition: all 0.2s;
}
.wf-card:hover {
    border-color: var(--border-default);
    background: var(--bg-tertiary);
}
.wf-card-icon { font-size: 20px; margin-bottom: 8px; }
.wf-card-title { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.wf-card-desc { font-size: 12px; color: var(--text-tertiary); margin-top: 4px; }
.wf-card-time {
    display: inline-block; margin-top: 8px;
    padding: 2px 8px; background: var(--bg-tertiary);
    border-radius: 4px; font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-tertiary);
}

/* Workflow alt view (table-like) */
.wf-table {
    margin: 24px 0;
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    overflow: hidden;
}
.wf-row {
    display: flex; align-items: center;
    border-bottom: 1px solid var(--border-subtle);
    padding: 12px 20px;
    transition: background 0.2s;
}
.wf-row:last-child { border-bottom: none; }
.wf-row:hover { background: var(--bg-tertiary); }
.wf-step-num {
    width: 36px; height: 36px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 700;
    flex-shrink: 0; margin-right: 16px;
}
.wf-step-num.s0 { background: var(--gradient-blue); color: #fff; }
.wf-step-num.s1 { background: var(--gradient-green); color: #fff; }
.wf-step-num.s2 { background: var(--gradient-purple); color: #fff; }
.wf-step-num.s3 { background: var(--gradient-cyan); color: #fff; }
.wf-step-num.s4 { background: var(--gradient-orange); color: #fff; }
.wf-step-num.s5 { background: rgba(99,102,241,1); color: #fff; }
.wf-step-num.s6 { background: linear-gradient(135deg, #db61a2, #a371f7); color: #fff; }
.wf-row-icon { font-size: 18px; margin-right: 12px; }
.wf-row-info { flex: 1; }
.wf-row-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.wf-row-desc { font-size: 12px; color: var(--text-tertiary); margin-top: 2px; }
.wf-row-badge {
    padding: 4px 10px; background: var(--bg-tertiary);
    border-radius: 6px; font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-secondary); flex-shrink: 0;
}

/* Orchestrator modes */
.modes-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin: 24px 0;
}
.mode-card {
    background: var(--bg-deep);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s;
}
.mode-card:hover {
    border-color: var(--accent-blue);
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}
.mode-icon { font-size: 32px; margin-bottom: 12px; }
.mode-name {
    font-size: 18px; font-weight: 700;
    color: var(--text-primary); margin-bottom: 8px;
}
.mode-desc { font-size: 13px; color: var(--text-tertiary); }
.mode-cmd {
    display: inline-block; margin-top: 12px;
    padding: 6px 16px; background: var(--bg-tertiary);
    border-radius: 6px; font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-cyan);
}
.mode-card.auto { border-color: rgba(63,185,80,0.3); }
.mode-card.auto:hover { box-shadow: 0 8px 30px var(--glow-green); }
.mode-card.plan { border-color: rgba(56,139,253,0.3); }
.mode-card.plan:hover { box-shadow: 0 8px 30px var(--glow-blue); }
.mode-card.build { border-color: rgba(163,113,247,0.3); }
.mode-card.build:hover { box-shadow: 0 8px 30px var(--glow-purple); }

/* ============ AGENT CARDS ============ */
.agents-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
    gap: 20px;
    margin: 24px 0;
}
.agent-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 24px;
    transition: all 0.3s ease;
}
.agent-card:hover {
    border-color: var(--border-default);
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3);
}
.agent-card-header {
    display: flex; align-items: center; gap: 16px;
    margin-bottom: 16px;
}
.agent-avatar {
    width: 52px; height: 52px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; flex-shrink: 0;
}
.agent-orch { background: linear-gradient(135deg, #6366f1, #818cf8); }
.agent-keeper { background: var(--gradient-green); }
.agent-expert { background: var(--gradient-purple); }
.agent-runner { background: var(--gradient-orange); }
.agent-info { flex: 1; }
.agent-name { font-size: 17px; font-weight: 600; color: var(--text-primary); }
.agent-role { font-size: 12px; color: var(--text-tertiary); margin-top: 2px; }
.agent-tags { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.agent-tag {
    padding: 3px 10px; border-radius: 6px;
    font-size: 11px; font-family: 'JetBrains Mono', monospace;
}
.agent-tag.model { background: rgba(56,139,253,0.15); color: var(--accent-blue); }
.agent-tag.timeout { background: rgba(210,153,34,0.15); color: var(--accent-yellow); }
.agent-tag.retry { background: rgba(163,113,247,0.15); color: var(--accent-purple); }
.agent-body { color: var(--text-secondary); font-size: 14px; }
.agent-body p { margin: 8px 0; }

/* ============ TABLES ============ */
.table-wrap {
    overflow-x: auto; margin: 20px 0;
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
}
table {
    width: 100%; border-collapse: collapse; font-size: 14px;
}
th {
    background: var(--bg-tertiary); color: var(--accent-blue);
    padding: 14px 16px; text-align: left; font-weight: 600;
    border-bottom: 1px solid var(--border-default);
    white-space: nowrap; font-size: 13px;
}
td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-secondary); font-size: 13px;
}
tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--bg-elevated); }

/* ============ CODE BLOCKS ============ */
pre {
    background: var(--bg-deep);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    margin: 20px 0;
    overflow-x: auto;
    position: relative;
    counter-reset: line;
}
pre::before {
    content: attr(data-lang);
    position: absolute;
    top: 0; right: 0;
    padding: 4px 12px;
    background: var(--bg-tertiary);
    color: var(--text-tertiary);
    font-size: 11px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    border-radius: 0 12px 0 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-left: 1px solid var(--border-subtle);
    border-bottom: 1px solid var(--border-subtle);
}
pre code {
    display: block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    line-height: 1.7;
    color: var(--text-primary);
    padding: 16px;
}
/* JSON specific - add subtle color */
.language-json { color: #d4d4d4; }
.language-bash { color: var(--accent-green); }
.language-yaml { color: var(--accent-cyan); }
/* Inline code */
p code, li code, td code {
    background: var(--bg-tertiary);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 13px;
    color: var(--accent-cyan);
    font-family: 'JetBrains Mono', monospace;
    border: 1px solid var(--border-subtle);
}

/* ============ CALLOUTS ============ */
.callout {
    padding: 16px 20px; border-radius: 12px;
    margin: 20px 0;
    display: flex; align-items: flex-start; gap: 12px;
    border: 1px solid;
}
.callout-icon { font-size: 18px; flex-shrink: 0; margin-top: 2px; }
.callout-body { flex: 1; }
.callout-title { font-weight: 600; margin-bottom: 4px; color: var(--text-primary); }
.callout p { margin: 0; font-size: 14px; }
.callout-info { background: rgba(56,139,253,0.08); border-color: rgba(56,139,253,0.25); }
.callout-info .callout-title { color: var(--accent-blue); }
.callout-warn { background: rgba(210,153,34,0.08); border-color: rgba(210,153,34,0.25); }
.callout-warn .callout-title { color: var(--accent-yellow); }
.callout-good { background: rgba(63,185,80,0.08); border-color: rgba(63,185,80,0.25); }
.callout-good .callout-title { color: var(--accent-green); }

/* ============ LISTS ============ */
ul, ol { margin: 16px 0; padding-left: 24px; color: var(--text-secondary); }
li { margin: 8px 0; padding-left: 4px; }
li::marker { color: var(--accent-blue); }

/* ============ BLOCKQUOTE (default fallback) ============ */
blockquote {
    border-left: 4px solid var(--accent-blue);
    background: var(--bg-secondary);
    padding: 16px 20px; margin: 20px 0;
    border-radius: 0 12px 12px 0;
}
blockquote p { color: var(--text-tertiary); }

/* ============ BADGES ============ */
.badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 6px; font-size: 12px; font-weight: 600;
}
.badge-blue { background: rgba(56,139,253,0.2); color: var(--accent-blue); }
.badge-green { background: rgba(63,185,80,0.2); color: var(--accent-green); }
.badge-yellow { background: rgba(210,153,34,0.2); color: var(--accent-yellow); }
.badge-purple { background: rgba(163,113,247,0.2); color: var(--accent-purple); }

/* ============ HR ============ */
hr {
    border: none; height: 1px;
    background: var(--border-subtle); margin: 48px 0;
}

/* ============ FOOTER ============ */
.footer {
    background: var(--bg-primary);
    border-top: 1px solid var(--border-subtle);
    padding: 40px; text-align: center;
    color: var(--text-muted); font-size: 13px;
}

/* ============ RESPONSIVE ============ */
@media (max-width: 900px) {
    .sidebar { display: none; }
    .main-content { margin-left: 0; }
    .hero { padding: 40px 24px; }
    .content { padding: 24px; }
    .hero-title { font-size: 30px; }
    .agents-grid { grid-template-columns: 1fr; }
    .workflow-diagram { min-width: auto; flex-wrap: wrap; gap: 8px; }
    .flow-arrow { transform: rotate(90deg); }
}

/* ============ SCROLLBAR ============ */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border-default); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-strong); }
"""

def extract_frontmatter(content):
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), parts[2]
    return "", content

def parse_frontmatter(fm):
    data = {}
    for line in fm.strip().split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip()] = v.strip()
    return data

def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s

def detect_workflow_diagram(markdown):
    """Detect if markdown contains ASCII workflow diagrams and flag them"""
    return '┌─────────────────┐' in markdown or '│ UTILIZADOR' in markdown

def build_workflow_html():
    """Build the visual workflow diagram HTML"""
    steps = [
        ('👤', 'Utilizador', 'Fornece Ticket', 'node-user'),
        ('🎯', 'Orchestrator', 'Coordena fluxo', 'node-orch'),
        ('📚', 'wiki-keeper', 'Consulta wiki', 'node-keeper'),
        ('🔍', 'miles-expert', 'Análise domínio', 'node-expert'),
        ('⚡', 'workflow-jira', 'Implementação', 'node-skill'),
        ('🧪', 'e2e-runner', 'Testes E2E', 'node-runner'),
        ('✅', 'wiki-keeper', 'Regista ticket', 'node-keeper'),
    ]

    diagram = '<div class="workflow-visual"><div class="workflow-diagram">'
    for i, (icon, name, desc, node_class) in enumerate(steps):
        diagram += f'''
        <div class="workflow-step">
            <div class="flow-node {node_class}">
                <span class="flow-icon">{icon}</span>
                <span class="flow-label">{name}</span>
                <span class="flow-meta">{desc}</span>
            </div>
        </div>'''
        if i < len(steps) - 1:
            diagram += '<div class="flow-arrow">▶</div>'
    diagram += '</div></div>'
    return diagram

def build_workflow_table():
    """Build the alternate workflow table view"""
    rows = [
        ('01', '👤', 'Utilizador', 'Fornece ID do ticket Jira ao orchestrator', 's0'),
        ('02', '🎯', 'workflow-orchestrator', 'Coordena todo o fluxo: delega, gere erros, pede aprovação', 's1'),
        ('03', '📚', 'wiki-keeper', 'Início: verifica conhecimento existente na wiki', 's2'),
        ('04', '🔍', 'miles-expert', 'Análise profunda de domínio: APIs, implementação, riscos', 's3'),
        ('05', '⚡', 'workflow-jira-ticket', 'Skill principal: 8 passos de implementação automática', 's4'),
        ('06', '🧪', 'e2e-runner', 'Executa testes E2E para validar a implementação', 's5'),
        ('07', '✅', 'wiki-keeper', 'Fim: regista nota do ticket no histórico do workflow', 's0'),
    ]
    html = '<div class="wf-table">'
    for num, icon, name, desc, cls in rows:
        html += f'''
        <div class="wf-row">
            <div class="wf-step-num {cls}">{num}</div>
            <span class="wf-row-icon">{icon}</span>
            <div class="wf-row-info">
                <div class="wf-row-name">{name}</div>
                <div class="wf-row-desc">{desc}</div>
            </div>
        </div>'''
    html += '</div>'
    return html

def build_agent_cards(markdown, is_pt=True):
    """Build agent cards from markdown agent sections"""
    if is_pt:
        agents = [
            {
                'icon': '🎯', 'name': 'workflow-orchestrator',
                'role': 'Orquestrador principal', 'cls': 'agent-orch',
                'model': 'deepseek-v4-flash', 'timeout': '10min', 'retry': '3 retries',
                'desc': 'Coordenador do fluxo completo. Recebe tickets Jira, delega tarefas, gere erros e ciclos de correção, e solicita aprovação humana quando necessário.'
            },
            {
                'icon': '📚', 'name': 'wiki-keeper',
                'role': 'Gestor de conhecimento', 'cls': 'agent-keeper',
                'model': 'qwen3.5-flash', 'timeout': '5min', 'retry': '4 retries',
                'desc': 'Mantém a wiki do workflow. Cria, atualiza e consulta notas. Processa PDFs, emails (.eml) e documentação. Sincroniza automaticamente com Obsidian.'
            },
            {
                'icon': '🔍', 'name': 'miles-expert',
                'role': 'Especialista de domínio', 'cls': 'agent-expert',
                'model': 'minimax-m2.7 / V4 Pro', 'timeout': '10-15min', 'retry': '3 retries',
                'desc': 'Especialista em MMP APIs, leasing automóvel EU. Seleciona modelo automaticamente: M2.7 (simples) ou V4 Pro (complexo/cross-module).'
            },
            {
                'icon': '🧪', 'name': 'e2e-runner',
                'role': 'Testador E2E', 'cls': 'agent-runner',
                'model': 'step-3.5-flash', 'timeout': '15min', 'retry': '2 retries',
                'desc': 'Executa testes Playwright E2E contra critérios de aceitação. Valida fluxos completos, tira screenshots e reporta resultados detalhados.'
            },
        ]
    else:
        agents = [
            {
                'icon': '🎯', 'name': 'workflow-orchestrator',
                'role': 'Main orchestrator', 'cls': 'agent-orch',
                'model': 'deepseek-v4-flash', 'timeout': '10min', 'retry': '3 retries',
                'desc': 'Full workflow coordinator. Receives Jira tickets, delegates tasks, manages error handling and correction cycles, requests human approval when needed.'
            },
            {
                'icon': '📚', 'name': 'wiki-keeper',
                'role': 'Knowledge manager', 'cls': 'agent-keeper',
                'model': 'qwen3.5-flash', 'timeout': '5min', 'retry': '4 retries',
                'desc': 'Maintains the workflow wiki. Creates, updates, and queries notes. Processes PDFs, emails (.eml), and documentation. Auto-syncs with Obsidian.'
            },
            {
                'icon': '🔍', 'name': 'miles-expert',
                'role': 'Domain specialist', 'cls': 'agent-expert',
                'model': 'minimax-m2.7 / V4 Pro', 'timeout': '10-15min', 'retry': '3 retries',
                'desc': 'Expert in MMP APIs, EU auto leasing. Auto-selects model: M2.7 (simple) or V4 Pro (complex/cross-module/high risk).'
            },
            {
                'icon': '🧪', 'name': 'e2e-runner',
                'role': 'E2E tester', 'cls': 'agent-runner',
                'model': 'step-3.5-flash', 'timeout': '15min', 'retry': '2 retries',
                'desc': 'Runs Playwright E2E tests against acceptance criteria. Validates full flows, takes screenshots, and reports detailed results.'
            },
        ]
    html = '<div class="agents-grid">'
    for a in agents:
        html += f'''
        <div class="agent-card">
            <div class="agent-card-header">
                <div class="agent-avatar {a['cls']}">{a['icon']}</div>
                <div class="agent-info">
                    <div class="agent-name">{a['name']}</div>
                    <div class="agent-role">{a['role']}</div>
                    <div class="agent-tags">
                        <span class="agent-tag model">{a['model']}</span>
                        <span class="agent-tag timeout">⏱ {a['timeout']}</span>
                        <span class="agent-tag retry">🔄 {a['retry']}</span>
                    </div>
                </div>
            </div>
            <div class="agent-body">
                <p>{a['desc']}</p>
            </div>
        </div>'''
    html += '</div>'
    return html

def build_modes_html(is_pt=True):
    """Build orchestrator modes cards"""
    if is_pt:
        modes = [
            ('🚀', 'Automático', 'Workflow completo: planeamento + execução + testes', 'auto'),
            ('📋', 'Plan', 'Apenas planeamento: análise, APIs afetadas, perguntas', 'plan'),
            ('🔨', 'Build', 'Apenas execução: a partir de plano existente (.json)', 'build'),
        ]
    else:
        modes = [
            ('🚀', 'Automatic', 'Full workflow: planning + execution + tests', 'auto'),
            ('📋', 'Plan', 'Planning only: analysis, affected APIs, questions', 'plan'),
            ('🔨', 'Build', 'Execution only: from existing plan (.json)', 'build'),
        ]
    html = '<div class="modes-container">'
    for icon, name, desc, cmd in modes:
        html += f'''
        <div class="mode-card {cmd}">
            <div class="mode-icon">{icon}</div>
            <div class="mode-name">{name}</div>
            <div class="mode-desc">{desc}</div>
            <span class="mode-cmd">{cmd}</span>
        </div>'''
    html += '</div>'
    return html

def markdown_to_html(markdown):
    """Convert markdown to HTML with special handling for workflow sections"""
    html = markdown

    # Code blocks - use unique placeholders to prevent other regexes from matching inside
    placeholders = {}
    counter = [0]

    def code_replace(m):
        lang = m.group(1) or 'text'
        code = m.group(2).rstrip()
        label = lang.upper() if lang != 'text' else 'CODE'
        placeholder = f'__CODE_BLOCK_{counter[0]}__'
        counter[0] += 1
        rendered = f'<pre data-lang="{label}">\n<code class="language-{lang}">\n{code}\n</code>\n</pre>'
        placeholders[placeholder] = rendered
        return placeholder

    html = re.sub(r'```(\w*)\n(.*?)```', code_replace, html, flags=re.DOTALL)

    # Headers with IDs (must happen before inline formatting)
    def header_replace(m):
        hashes = m.group(1)
        title = m.group(2).strip()
        level = len(hashes)
        anchor = slugify(title)
        if level == 2:
            return f'<h2 id="{anchor}"><span class="h2-number">§</span>{title}</h2>'
        return f'<h{level} id="{anchor}">{title}</h{level}>'
    html = re.sub(r'^(#{1,6})\s+(.+)$', header_replace, html, flags=re.MULTILINE)

    # Bold/Italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # Images
    html = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img src="\2" alt="\1" style="max-width:100%;border-radius:8px;">', html)

    # Horizontal rules
    html = re.sub(r'^---+\s*$', '<hr>', html, flags=re.MULTILINE)

    # Blockquotes with optional callout (if it has a **Title:** pattern)
    def bq_replace(m):
        content = m.group(1).strip()
        if '**' in content and ':' in content[:60]:
            parts = content.split(':', 1)
            title = parts[0].replace('**', '').strip()
            body = parts[1].strip() if len(parts) > 1 else ''
            cls = 'callout-info'
            if 'WARN' in title.upper() or 'ERRO' in title.upper() or 'ATEN' in title.upper():
                cls = 'callout-warn'
            elif 'SUCCESS' in title.upper() or 'DICA' in title.upper() or 'NOTE' in title.upper():
                cls = 'callout-good'
            return f'<div class="callout {cls}"><span class="callout-icon">💡</span><div class="callout-body"><div class="callout-title">{title}</div><p>{body}</p></div></div>'
        return f'<blockquote><p>{content}</p></blockquote>'
    html = re.sub(r'^>\s*(.+)$', bq_replace, html, flags=re.MULTILINE)

    # Tables
    html = re.sub(r'((?:\|.+\|\n?)+)', _convert_table, html)

    # Lists
    html = re.sub(r'^[\*\-]\s+(.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^(\d+)\.\s+(.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)
    html = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\n\1</ul>', html)

    # Paragraphs - wrap remaining text in <p>
    lines = html.split('\n')
    result = []
    in_pre = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append('')
            continue
        if '<pre' in stripped:
            in_pre = True
            result.append(line)
        elif '</pre>' in stripped:
            in_pre = False
            result.append(line)
        elif in_pre:
            result.append(line)
        elif any(stripped.startswith(t) for t in ['<h', '<ul>', '<ol>', '<table', '<li>', '<div', '<blockquote', '<hr', '<img', '</ul>', '<thead', '<tbody', '<tr', '<th', '<td', '<p>', '<span', '<strong', '<em', '</a', '<a ', '__CODE_BLOCK']):
            result.append(line)
        else:
            result.append(f'<p>{line}</p>')
    html = '\n'.join(result)

    # Restore code blocks from placeholders
    for placeholder, rendered in placeholders.items():
        html = html.replace(placeholder, rendered)

    return html

def _convert_table(match):
    raw = match.group(1).strip()
    lines = [l.strip() for l in raw.split('\n') if l.strip() and not l.strip().startswith('|---')]
    if not lines or not (lines[0].startswith('|') and lines[0].endswith('|')):
        return match.group(0)

    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
    body_lines = lines[2:] if len(lines) > 2 else lines[1:]

    html = '<div class="table-wrap"><table>\n<thead>\n<tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr>\n</thead>\n<tbody>\n'
    for row in body_lines:
        cells = [c.strip() for c in row.split('|') if c.strip()]
        if cells:
            html += '<tr>'
            for c in cells:
                html += f'<td>{c}</td>'
            html += '</tr>\n'
    html += '</tbody>\n</table></div>'
    return html

def build_nav(all_headings):
    """Build sidebar navigation from parsed headings"""
    nav = '<nav class="sidebar-nav">\n'

    # Main sections (h2)
    h2_count = 0
    for level, title, anchor in all_headings:
        if level == 2:
            h2_count += 1
            # Limit shown sections
            nav += f'<a href="#{anchor}" class="nav-link nav-h2">{title}</a>\n'
        elif level == 3 and h2_count <= 10:
            nav += f'<a href="#{anchor}" class="nav-link nav-h3">{title}</a>\n'

    nav += '</nav>'
    return nav

def build_toc(all_headings, is_pt=True):
    """Build table of contents HTML"""
    if not all_headings:
        return ''

    label = '📑 Nesta página' if is_pt else '📑 On this page'
    toc = '<div class="section-card" style="padding: 24px;">'
    toc += f'<h4 style="margin: 0 0 16px; color: var(--accent-blue);">{label}</h4>'
    toc += '<ul style="margin:0; padding:0; list-style:none;">'
    for level, title, anchor in all_headings:
        if level <= 3:
            indent = (level - 1) * 20
            toc += f'<li style="margin: 6px 0; padding-left: {indent}px;"><a href="#{anchor}" style="font-size:14px;">{title}</a></li>'
    toc += '</ul></div>'
    return toc

def create_html_document(markdown_file, output_file):
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter, body = extract_frontmatter(content)
    metadata = parse_frontmatter(frontmatter)
    is_pt = 'PT' in metadata.get('name', '') or 'Português' in content[:200]
    lang = 'pt' if is_pt else 'en'
    title = 'Manual do Workflow' if is_pt else 'Workflow Manual'
    version = metadata.get('version', 'v2.3')

    # Parse all headings for navigation
    all_headings = [(len(h), t, slugify(t)) for h, t in re.findall(r'^(#{1,3})\s+(.+)$', body, re.MULTILINE)]

    # Detect if this has a workflow diagram section
    has_diagram = detect_workflow_diagram(body)

    # Replace ASCII workflow diagram with visual version
    if has_diagram:
        lines = body.split('\n')
        cleaned = []
        i = 0
        while i < len(lines):
            if lines[i].startswith('```'):
                start = i
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('```'):
                        end = j
                        break
                else:
                    end = len(lines)
                block = lines[start:end+1]
                has_box = any(
                    any(c in line for c in ['\u250c', '\u2502', '\u2514', '\u251c', '\u25bc', '\u25ba'])
                    for line in block[1:-1]
                )
                if not has_box:
                    cleaned.extend(block)
                i = end + 1
            else:
                cleaned.append(lines[i])
                i += 1
        body = '\n'.join(cleaned)

        # Match either PT or EN workflow heading
        wf_heading = '2. Fluxo do Workflow' if is_pt else '2. Workflow Flowchart'
        wf_heading_full = f'## {wf_heading}'
        body = body.replace(
            wf_heading_full,
            f'{wf_heading_full}\n\n<!-- WORKFLOW_DIAGRAM -->\n\n<!-- WORKFLOW_TABLE -->\n\n'
        )

    wf_diagram = build_workflow_html()
    wf_table = build_workflow_table()
    body = body.replace('<!-- WORKFLOW_DIAGRAM -->', wf_diagram)
    body = body.replace('<!-- WORKFLOW_TABLE -->', wf_table)

    agent_cards = build_agent_cards(body, is_pt)
    modes_html = build_modes_html(is_pt)

    # Remove old modes section (both languages)
    if is_pt:
        body = re.sub(r'### 3\.1\.1 Modos de Operação do Orchestrator.*?(?=### |$)', '', body, flags=re.DOTALL)
        agents_heading = '3. Descrição e Funções dos Agentes'
    else:
        body = re.sub(r'### 3\.1\.1 Orchestrator Operation Modes.*?(?=### |$)', '', body, flags=re.DOTALL)
        agents_heading = '3. Agent Descriptions and Functions'

    body = body.replace(
        f'## {agents_heading}',
        f'## {agents_heading}\n\n{agent_cards}\n\n'
    )

    # Convert rest of markdown to HTML
    body_html = markdown_to_html(body)

    # Build navigation
    nav_html = build_nav(all_headings)

    toc_html = build_toc(all_headings, is_pt)

    # Build final HTML
    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{PREMIUM_CSS}</style>
</head>
<body>
    <div class="app-container">
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="sidebar-logo">
                    <div class="sidebar-logo-icon">📘</div>
                    <div class="sidebar-logo-text">Workflow</div>
                </div>
                <span class="sidebar-version">{version}</span>
            </div>
            <div class="sidebar-section">Navegação</div>
            {nav_html}
        </aside>

        <main class="main-content">
            <div class="hero">
                <div class="hero-content">
                    <div class="hero-badge">🚀 Automação Inteligente</div>
                    <h1 class="hero-title"><span class="hero-title-gradient">{title}</span></h1>
                    <p class="hero-desc">
                        {'Sistema completo de automação de workflow com agentes especializados, habilidades inteligentes e seleção dinâmica de modelos de IA.' if is_pt else 'Complete workflow automation system with specialized agents, intelligent skills, and dynamic AI model selection.'}
                    </p>
                    <div class="hero-meta">
                        <span class="hero-meta-item">🤖 4 Agentes</span>
                        <span class="hero-meta-item">⚡ 7 Skills</span>
                        <span class="hero-meta-item">🔄 Fluxo Automático</span>
                        <span class="hero-meta-item">🧠 Modelos Dinâmicos</span>
                    </div>
                </div>
            </div>

            <div class="content">
                <div class="search-bar" style="position: relative;">
                    <span class="icon">🔍</span>
                    <input id="search-input" type="text" placeholder="{'Pesquisar no manual...' if is_pt else 'Search the manual...'}" autocomplete="off">
                    <span class="count"></span>
                    <div id="search-results" class="search-results"></div>
                </div>
                {toc_html}
                {body_html}
            </div>

            <footer class="footer">
                <p style="margin: 0;">{f'Gerado: {datetime.now().strftime("%Y-%m-%d")} • Workflow Automation System' if is_pt else f'Generated: {datetime.now().strftime("%Y-%m-%d")} • Workflow Automation System'}</p>
            </footer>
        </main>
    </div>
    <style>
    .search-bar {{
        position: relative;
        margin: 0 0 20px;
    }}
    .search-bar input {{
        width: 100%;
        padding: 12px 16px 12px 40px;
        background: var(--bg-deep);
        border: 1px solid var(--border-subtle);
        border-radius: 10px;
        color: var(--text-primary);
        font-size: 14px;
        font-family: 'Inter', sans-serif;
        outline: none;
        transition: all 0.2s;
    }}
    .search-bar input:focus {{
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 3px var(--glow-blue);
    }}
    .search-bar input::placeholder {{
        color: var(--text-muted);
    }}
    .search-bar .icon {{
        position: absolute;
        left: 12px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 16px;
        color: var(--text-muted);
        pointer-events: none;
    }}
    .search-bar .count {{
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 12px;
        color: var(--text-muted);
        pointer-events: none;
    }}
    .search-results {{
        display: none;
        background: var(--bg-secondary);
        border: 1px solid var(--border-default);
        border-radius: 10px;
        max-height: 300px;
        overflow-y: auto;
        margin-top: 4px;
        position: absolute;
        width: 100%;
        z-index: 50;
    }}
    .search-results.visible {{
        display: block;
    }}
    .search-result-item {{
        padding: 10px 14px;
        cursor: pointer;
        border-bottom: 1px solid var(--border-subtle);
        font-size: 13px;
        color: var(--text-secondary);
        transition: all 0.15s;
    }}
    .search-result-item:last-child {{
        border-bottom: none;
    }}
    .search-result-item:hover {{
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }}
    .search-result-item .sr-title {{
        color: var(--accent-blue);
        font-weight: 600;
        font-size: 12px;
        margin-bottom: 2px;
    }}
    .search-result-item .sr-snippet {{
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        font-size: 12px;
        color: var(--text-tertiary);
    }}
    .search-result-item mark {{
        background: rgba(210, 153, 34, 0.3);
        color: var(--text-primary);
        border-radius: 2px;
    }}
    .search-highlight {{
        background: rgba(210, 153, 34, 0.3);
        border-radius: 3px;
        padding: 1px 2px;
    }}
    .search-hide {{
        display: none;
    }}
    </style>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const links = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('h2[id], h3[id]');
        function updateActive() {{
            let current = '';
            sections.forEach(s => {{
                if (window.scrollY >= s.offsetTop - 120) {{
                    current = s.id;
                }}
            }});
            links.forEach(l => {{
                l.classList.remove('active');
                if (l.getAttribute('href') === '#' + current) {{
                    l.classList.add('active');
                }}
            }});
        }}
        window.addEventListener('scroll', updateActive);
        updateActive();

        // Search
        const searchInput = document.getElementById('search-input');
        const resultsPanel = document.getElementById('search-results');
        if (searchInput) {{
            const content = document.querySelector('.content');
            const count = searchInput.nextElementSibling;
            let allElements = [];

            searchInput.addEventListener('input', function() {{
                const q = this.value.toLowerCase().trim();
                const all = content.querySelectorAll('h2, h3, h4, p, li, td');
                const matches = [];

                // Reset highlights
                all.forEach(el => {{
                    el.innerHTML = el.innerHTML.replace(/<span class="search-highlight">(.*?)<\\/span>/g, '$1');
                }});

                if (!q) {{
                    resultsPanel.classList.remove('visible');
                    resultsPanel.innerHTML = '';
                    count.textContent = '';
                    return;
                }}

                // Collect matching elements with context
                all.forEach(el => {{
                    const text = el.textContent.toLowerCase();
                    if (text.includes(q) && el.offsetParent !== null) {{
                        // Find the closest heading above for context
                        let heading = '';
                        let sibling = el.previousElementSibling;
                        while (sibling) {{
                            if (['H2','H3','H4'].includes(sibling.tagName)) {{
                                heading = sibling.textContent;
                                break;
                            }}
                            sibling = sibling.previousElementSibling;
                        }}
                        if (!heading) {{
                            let parent = el.parentElement;
                            while (parent) {{
                                let ps = parent.previousElementSibling;
                                while (ps) {{
                                    if (['H2','H3','H4'].includes(ps.tagName)) {{
                                        heading = ps.textContent;
                                        break;
                                    }}
                                    ps = ps.previousElementSibling;
                                }}
                                if (heading) break;
                                parent = parent.parentElement;
                            }}
                        }}

                        // Highlight
                        const html = el.innerHTML;
                        const idx = html.toLowerCase().indexOf(q);
                        if (idx >= 0 && !html.includes('search-highlight')) {{
                            const orig = html.substring(idx, idx + q.length);
                            el.innerHTML = html.substring(0, idx) +
                                '<span class="search-highlight">' + orig + '</span>' +
                                html.substring(idx + q.length);
                        }}

                        matches.push({{ el, text: text.substring(0, 120), heading }});
                    }}
                }});

                count.textContent = matches.length + ' resultado' + (matches.length !== 1 ? 's' : '');

                // Show results panel
                if (matches.length > 0) {{
                    resultsPanel.innerHTML = '';
                    const maxResults = Math.min(matches.length, 20);
                    for (let i = 0; i < maxResults; i++) {{
                        const m = matches[i];
                        const div = document.createElement('div');
                        div.className = 'search-result-item';
                        const snippet = m.el.textContent.trim().substring(0, 120);
                        const markedSnippet = snippet.replace(new RegExp('(' + q.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&') + ')', 'gi'), '<mark>$1</mark>');
                        div.innerHTML = '<div class="sr-title">' + (m.heading || 'Documento') + '</div><div class="sr-snippet">' + markedSnippet + '</div>';
                        div.addEventListener('click', function() {{
                            searchInput.value = q;
                            resultsPanel.classList.remove('visible');
                            m.el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            // Flash effect
                            m.el.style.transition = 'background 0.5s';
                            m.el.style.background = 'rgba(56, 139, 253, 0.15)';
                            setTimeout(() => {{ m.el.style.background = ''; }}, 1500);
                        }});
                        resultsPanel.appendChild(div);
                    }}
                    resultsPanel.classList.add('visible');
                }} else {{
                    resultsPanel.classList.remove('visible');
                }}
            }});

            // Hide results on blur (with delay for click)
            searchInput.addEventListener('blur', function() {{
                setTimeout(() => resultsPanel.classList.remove('visible'), 200);
            }});
            searchInput.addEventListener('focus', function() {{
                if (this.value.trim()) {{
                    this.dispatchEvent(new Event('input'));
                }}
            }});
        }}
    }});
    </script>
</body>
</html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Created: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: md-to-html.py <input.md> <output.html>")
        sys.exit(1)
    inp, out = sys.argv[1], sys.argv[2]
    if not os.path.exists(inp):
        print(f"❌ File not found: {inp}")
        sys.exit(1)
    create_html_document(inp, out)