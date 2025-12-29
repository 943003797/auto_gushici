<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

## Project Overview

This is **auto_gushici**, an ancient Chinese poetry video editing system that uses AI agents to automatically generate short videos containing ancient poetry content. The system integrates multi-agent collaboration, audio processing, video editing, and material management functions to provide users with a one-click ancient poetry video creation solution.

## Quick Context

- **Domain**: Ancient Chinese poetry video production
- **Core Features**: Multi-agent collaboration with AutoGen, TTS voice synthesis, automatic video editing, material management
- **Tech Stack**: Python 3.13+, AutoGen AgentChat, DashScope, Gradio, Jianying Draft API

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->