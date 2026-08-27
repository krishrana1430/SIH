# Push WeatherGPT to Your Team's GitHub Repository

## Quick Steps

### 1. Initialize Git (if not already initialized)
```bash
cd /home/piyushxdev/SIH/weather-gpt
git init
```

### 2. Add Your Team's Repository as Remote
```bash
# Replace YOUR_TEAM_REPO_URL with your actual team repository URL
git remote add origin YOUR_TEAM_REPO_URL

# Example:
# git remote add origin https://github.com/your-team/sih-2026.git
```

### 3. Check What Branch Your Team Uses
Your team might be using `main` or `master`. Check with them, or:
```bash
# Fetch remote branches
git fetch origin

# See what branches exist
git branch -r
```

### 4. Stage All Files
```bash
# Add all files
git add .

# Check what will be committed (make sure .env is NOT in the list)
git status
```

### 5. Create Your First Commit
```bash
git commit -m "Add WeatherGPT - AI Weather Forecasting Assistant

Features:
- Multi-language support (7 Indian languages)
- Role-based responses (Citizen, Farmer, Pilot, Emergency)
- Voice input/output
- SMS alerts
- Real-time weather data
- Docker deployment ready

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 6. Push to Team Repository

**Option A: Push to main branch**
```bash
git branch -M main
git push -u origin main
```

**Option B: Push to a feature branch (safer for team collaboration)**
```bash
git checkout -b feature/weather-gpt
git push -u origin feature/weather-gpt
```

Then create a Pull Request on GitHub for your team to review.

## If Repository Already Has Code

If your team's repo already has files:

```bash
# Fetch existing code first
git fetch origin main

# Try to merge (resolve conflicts if any)
git merge origin/main --allow-unrelated-histories

# Or rebase
git rebase origin/main

# Then push
git push origin main
```

**Better approach:** Create your own directory:
```bash
# Create a weather-gpt folder for your module
mkdir -p weather-gpt
mv backend frontend docker-compose.yml Dockerfile.* .env.example README.md SETUP.md weather-gpt/

# Commit and push
git add .
git commit -m "Add WeatherGPT module in weather-gpt/ directory"
git push origin main
```

## Authentication

When prompted for credentials:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (NOT your GitHub password)

Get a token: GitHub → Settings → Developer settings → Personal access tokens → Generate new token → Select `repo` scope

## Common Issues

### "Updates were rejected because the remote contains work"
```bash
# Pull first
git pull origin main --rebase

# Then push
git push origin main
```

### "Permission denied"
- Make sure your team added you as a collaborator
- Check if you're using the correct authentication (token, not password)

### "Fatal: remote origin already exists"
```bash
# Remove old remote
git remote remove origin

# Add correct remote
git remote add origin YOUR_TEAM_REPO_URL
```

### Accidentally included .env file
```bash
# Remove from staging
git rm --cached .env

# Commit the removal
git commit -m "Remove .env file"
```

## Verify Before Pushing

Always check:
```bash
# See what files will be pushed
git status

# Make sure these are NOT in the list:
# - .env (should only see .env.example)
# - node_modules/ (should be in .gitignore)
# - venv/ (should be in .gitignore)
# - __pycache__/ (should be in .gitignore)
# - *.log files (should be in .gitignore)
```

## After Pushing

1. **Notify your team** - Let them know you've pushed WeatherGPT
2. **Share setup instructions** - Point them to `SETUP.md` or `HOW_TO_RUN.md`
3. **Create issues** - Use GitHub Issues for any pending tasks
4. **Coordinate** - Make sure everyone pulls the latest code:
   ```bash
   git pull origin main
   ```

---

**Ready to push?** Just replace `YOUR_TEAM_REPO_URL` with your actual repository URL and run the commands!
