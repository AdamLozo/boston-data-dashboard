# Boston Data Dashboard - Claude Code Build Prompt

Copy everything below the line into Claude Code:

---

## Project Context

I'm building the Boston Data Dashboard - a hyperlocal building permits tracker using data from Analyze Boston's open data portal.

**Read these files first (in order):**
1. `.claude/CLAUDE.md` - Project overview and conventions
2. `docs/MASTER_PLAN.md` - Milestones and current status
3. `docs/PLAN.md` - Detailed technical specification

**Knowledge base for deep context:**
- `docs/knowledge-base/01-infrastructure/CONTEXT.md` - Database schema, Render config
- `docs/knowledge-base/02-data-pipeline/CONTEXT.md` - CKAN API, sync job
- `docs/knowledge-base/03-backend/CONTEXT.md` - FastAPI endpoints
- `docs/knowledge-base/04-frontend/CONTEXT.md` - Leaflet.js map, responsive design
- `docs/knowledge-base/05-monitoring/CONTEXT.md` - Health checks

**Slash commands available:**
- `/sync` - Test sync job locally
- `/api` - Start FastAPI dev server
- `/db` - Database operations
- `/deploy` - Push to GitHub and Render

## Current Goal

**Milestone 1: Local Prototype**

Build a working end-to-end prototype on localhost:
1. Database schema (PostgreSQL)
2. Sync job that fetches 90 days of permits from CKAN API
3. FastAPI backend with all endpoints
4. Frontend with Leaflet.js map and filters

## Tech Stack
- Python 3.11+ / FastAPI / psycopg2 (raw SQL, no ORM)
- PostgreSQL (local for dev, Render for prod)
- Vanilla JS / Leaflet.js with MarkerCluster
- Render for hosting (web service + cron + PostgreSQL)

## Working Directory
`C:\Users\adam\OneDrive\Claude\Projects\boston-data-dashboard`

## Rules
- Read the knowledge base CONTEXT.md files before implementing each component
- Ask me before making assumptions on unclear requirements
- Test locally before considering a component done
- Commit with clear messages after each working component

## Start

Read the context files listed above, then tell me what you understand about the project and what you'll build first.
