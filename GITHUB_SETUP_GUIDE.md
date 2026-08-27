# How to Share WeatherGPT on GitHub

This guide will help you push your WeatherGPT project to GitHub so your team can access it.

## Prerequisites

- GitHub account (create one at https://github.com if you don't have one)
- Git installed on your system (already available in WSL)

## Step-by-Step Guide

### Step 1: Create a New Repository on GitHub

1. Go to https://github.com
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `weather-gpt` (or any name you prefer)
   - **Description**: "AI-powered weather forecasting assistant with multilingual support"
   - **Visibility**: Choose **Private** (for your team only) or **Public** (for everyone)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

### Step 2: Initialize Git in Your Project

Open your terminal in the project directory and run:

```bash
cd /home/piyushxdev/SIH/weather-gpt

# Initialize git repository
git init

# Add all files to staging
git add .

# Create your first commit
git commit -m "Initial commit: WeatherGPT - AI Weather Assistant

- Multi-language support (English, Hindi, Tamil, Telugu, Kannada, Bengali, Marathi)
- Role-based responses (Citizen, Farmer, Pilot, Emergency)
- Voice input/output support
- SMS alerts integration
- Docker deployment ready
- Comprehensive API documentation

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 3: Connect to GitHub and Push

After creating the repository on GitHub, you'll see a page with commands. Copy your repository URL (it will look like `https://github.com/YOUR_USERNAME/weather-gpt.git`).

Then run:

```bash
# Add the GitHub repository as remote origin
git remote add origin https://github.com/YOUR_USERNAME/weather-gpt.git

# Rename the default branch to main (GitHub standard)
git branch -M main

# Push your code to GitHub
git push -u origin main
```

**Note:** GitHub will prompt you to authenticate. You have two options:

#### Option A: Personal Access Token (Recommended)
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "WeatherGPT"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)
7. When prompted for password during `git push`, paste the token

#### Option B: SSH Key (For Advanced Users)
Follow GitHub's SSH setup guide: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Step 4: Verify Your Upload

1. Refresh your GitHub repository page
2. You should see all your files uploaded
3. The README.md will be displayed automatically

### Step 5: Share with Your Team

Send your teammates the repository URL. They can clone it with:

```bash
git clone https://github.com/YOUR_USERNAME/weather-gpt.git
cd weather-gpt
```

Then they follow the setup instructions in `HOW_TO_RUN.md` or `SETUP.md`.

## Important Security Check ✅

Before pushing, verify that sensitive files are ignored:

```bash
# Check that .env is in .gitignore
grep "^\.env$" .gitignore

# Verify .env is not tracked
git status | grep ".env"
```

If `.env` appears in git status, remove it:

```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```

## Quick Team Setup Instructions

After your team clones the repository, they need to:

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Add their API keys to .env:**
   - Groq API key (free): https://console.groq.com
   - Gemini API key (free): https://aistudio.google.com/app/apikey

3. **Start with Docker:**
   ```bash
   docker-compose up -d
   ```

4. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Common Issues & Solutions

### Issue: "Permission denied (publickey)"
**Solution:** Use HTTPS URL instead of SSH, or set up SSH keys (see Option B above)

### Issue: "Authentication failed"
**Solution:** Use a Personal Access Token instead of your GitHub password (see Option A above)

### Issue: Large files causing slow upload
**Solution:** The `.dockerignore` and `.gitignore` should prevent this. If issues persist:
```bash
# Check large files
du -sh * | sort -h | tail -5

# If node_modules or venv are being tracked:
git rm -r --cached frontend/web/node_modules
git rm -r --cached venv
git commit -m "Remove large directories"
```

### Issue: Accidentally committed .env file
**Solution:** Remove it immediately:
```bash
git rm --cached .env
git commit -m "Remove .env file"
git push origin main

# Then rotate all API keys in the exposed .env file!
```

## Next Steps After Pushing

1. **Add collaborators:**
   - Go to your repository on GitHub
   - Settings → Collaborators → Add people
   - Enter your teammates' GitHub usernames

2. **Set up branch protection:**
   - Settings → Branches → Add rule
   - Protect the `main` branch
   - Require pull request reviews

3. **Create issues for features:**
   - Use GitHub Issues to track tasks
   - Assign team members to specific features

4. **Set up a project board:**
   - Projects tab → New project
   - Track progress visually

## Alternative: Using GitHub Desktop (GUI)

If you prefer a graphical interface:

1. Download GitHub Desktop: https://desktop.github.com
2. File → Add local repository → Select your project folder
3. Publish repository to GitHub
4. Fill in details and click Publish

## Need Help?

- GitHub Documentation: https://docs.github.com
- Git Basics: https://git-scm.com/book/en/v2/Getting-Started-Git-Basics
- GitHub CLI (alternative): https://cli.github.com

---

**Remember:** Never commit API keys, passwords, or `.env` files to GitHub! Always use `.env.example` as a template.
