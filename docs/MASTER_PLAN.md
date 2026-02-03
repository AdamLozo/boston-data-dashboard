# Boston Data Dashboard - Master Plan

## Vision
A hyperlocal civic tool that makes Boston's building permit data accessible and useful for residents, with a foundation designed for expansion to other Analyze Boston datasets.

---

## Milestones

### Milestone 1: Local Prototype (Target: 1 session)
**Goal**: Working end-to-end on localhost

- [ ] Database schema created and tested
- [ ] Sync job fetches 90 days of permits
- [ ] API endpoints return real data
- [ ] Map displays permits with clustering
- [ ] Filters work (ZIP, work type, date range)

**Success Criteria**: Can filter permits by ZIP and see them on a map locally

### Milestone 2: Production Deployment (Target: 1 session)
**Goal**: Live on Render with automated updates

- [ ] GitHub repo created and code pushed
- [ ] Render PostgreSQL provisioned
- [ ] Web service deployed and accessible
- [ ] Cron job scheduled and verified
- [ ] Health endpoint returns accurate status

**Success Criteria**: Dashboard accessible at .onrender.com, syncs daily at 6 AM

### Milestone 3: Polish & Mobile (Target: 1 session)
**Goal**: Production-ready UX

- [ ] Mobile-responsive design tested
- [ ] Loading states and error handling
- [ ] Neighborhood quick-select
- [ ] Basic stats display
- [ ] README with screenshots

**Success Criteria**: Usable on phone, shareable with neighbors

### Milestone 4: Restaurant Inspections (Future)
**Goal**: Second dataset integrated

- [ ] New table schema
- [ ] Separate sync job
- [ ] Toggle between datasets in UI
- [ ] Combined map view option

---

## Knowledge Base Index

| Section | Path | Purpose |
|---------|------|---------|
| Infrastructure | `01-infrastructure/` | Database, deployment, environment |
| Data Pipeline | `02-data-pipeline/` | CKAN API, sync job, data validation |
| Backend | `03-backend/` | FastAPI, endpoints, error handling |
| Frontend | `04-frontend/` | Leaflet, responsive design, UX |
| Monitoring | `05-monitoring/` | Health checks, logging, alerts |
| Future | `06-future/` | Expansion datasets, features |

Each section has a `CONTEXT.md` that serves as the entry point.

---

## Tool Strategy

### When to Use Claude.ai (This Interface)
- **Planning sessions** - architecture decisions, trade-offs
- **Research** - API exploration, library comparison
- **Debugging complex issues** - full conversation context
- **Code review** - discussing approaches
- **Documentation** - writing guides, README

### When to Use Claude Code
- **Implementation** - writing actual code files
- **Multi-file changes** - refactoring, feature additions
- **Testing** - running code, checking output
- **Git operations** - commits, branches, pushes
- **Deployment** - Render CLI, environment setup

### Handoff Pattern
1. **Claude.ai**: Plan the feature, document in knowledge-base
2. **Claude Code**: Implement using context files
3. **Claude.ai**: Review, iterate on approach if needed

---

## Speed Multipliers

### Skills to Integrate (from your skills library)
1. **frontend-design** - Already have it, use for dashboard polish
2. **brainstorming** - Transform rough ideas into designs
3. **writing-plans** - Create detailed implementation plans
4. **executing-plans** - Task-by-task with verification

### Custom Claude Code Commands to Create
```
/.claude/commands/
├── sync.md      # Test sync job locally
├── api.md       # Start FastAPI dev server
├── deploy.md    # Push to GitHub, check Render
└── db.md        # Database operations (reset, seed, migrate)
```

### Automations to Build
1. **Local dev script** - One command to start Postgres + FastAPI
2. **Seed data script** - Pre-populate with sample permits for testing
3. **Health check script** - Verify all endpoints responding

---

## Session Workflow

### Starting a Session (Claude Code)
```
1. Read .claude/CLAUDE.md
2. Check current milestone status
3. Read relevant knowledge-base CONTEXT.md
4. Implement next unchecked item
5. Test locally
6. Commit with clear message
```

### Ending a Session
```
1. Update milestone checkboxes
2. Note any blockers in CONTEXT.md
3. Commit work-in-progress if needed
```

---

## Risk Register

| Risk | Mitigation |
|------|------------|
| CKAN API rate limits | Batch queries, respect limits, cache locally |
| Render free tier limits | Monitor usage, upgrade if needed |
| Stale data | Health endpoint warns if sync fails |
| Map performance with many markers | Marker clustering (already planned) |

---

## Definition of Done (Each Feature)
- [ ] Code works locally
- [ ] Error handling in place
- [ ] Mobile-responsive (if frontend)
- [ ] Documented in knowledge-base
- [ ] Tested in production
