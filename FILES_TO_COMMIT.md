# Files to Add to GitHub

## ✅ FILES TO ADD (Essential for team)

### Documentation
- README.md
- SETUP.md
- HOW_TO_RUN.md
- CONTRIBUTING.md
- DOCUMENTATION_INDEX.md
- LOCAL_DEVELOPMENT.md
- GITHUB_SETUP_GUIDE.md
- PUSH_TO_TEAM_REPO.md

### Configuration Files
- .env.example (template for team)
- .env.docker.template
- .gitignore
- .dockerignore

### Docker Files
- docker-compose.yml
- docker-compose.local.yml
- docker-compose.simplified.yml
- Dockerfile.backend
- Dockerfile.frontend

### Source Code
- backend/ (entire folder)
- frontend/ (entire folder)
- infra/ (entire folder)

### Python Files (root level)
- requirements.txt
- server.py
- start_server.py
- system_check.py
- test_api.py
- test_frontend.py
- test_llm.py

### Documentation Archive
- docs/ (entire folder with API docs and archive)

## ❌ FILES TO EXCLUDE (DO NOT ADD)

### Sensitive Files (NEVER commit these!)
- .env (contains your actual API keys)
- .env.local
- .env.docker (if it has real keys)

### Build Artifacts
- frontend/web/node_modules/
- frontend/web/.next/
- venv/
- __pycache__/
- *.pyc
- *.pyo

### Database & Logs
- weathergpt.db (your local database)
- *.log
- server.log

### IDE & System Files
- .vscode/
- .idea/
- *.swp
- *.swo
- .DS_Store
- Thumbs.db

### Claude Config (optional - your choice)
- .claude/ (your local Claude settings)

## Quick Command

To add ONLY the safe files:

```bash
# Add documentation
git add *.md

# Add config templates (not .env!)
git add .env.example .env.docker.template .gitignore .dockerignore

# Add Docker files
git add docker-compose*.yml Dockerfile.*

# Add source code directories
git add backend/ frontend/ infra/

# Add Python files
git add requirements.txt *.py

# Add docs
git add docs/

# Check what you're about to commit
git status
```

## Verify Before Committing

Run this to make sure .env is NOT being added:
```bash
git status | grep -E "\.env$|\.env\.local|weathergpt\.db|\.log$"
```

If you see any of these files, DON'T commit! They should be ignored.

## Safe One-Command Add

This adds everything except ignored files:
```bash
git add .
```

This is safe because your .gitignore already excludes:
- .env files (except .env.example)
- node_modules/
- venv/
- __pycache__/
- *.log files
- .next/

But double-check with `git status` to be sure!
