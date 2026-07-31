---
name: {{EXPERT_NAME}}
version: v1.0.0
description: "{{EXPERT_DESCRIPTION}}"
mode: subagent
model: {{PRIMARY_MODEL}}
retry: 3
timeout_minutes: 15
fallback_model: {{FALLBACK_MODEL}}
---

## Knowledge Sources

{{KNOWLEDGE_PATHS}}

## Domain Expertise

{{DOMAIN_SECTIONS}}

## Response Guidelines

{{RESPONSE_GUIDELINES}}
