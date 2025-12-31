# Git & GitHub Workflow Guide
## Complete Guide for Your Mental Health AI Research Project

---

## 🎯 MAIN PRINCIPLES

### 1. **Version Control = Time Machine for Your Code**
- Save snapshots of your work at different points
- Go back to any previous version if something breaks
- Track what changed, when, and why

### 2. **Branches = Parallel Universes**
- Main branch = stable, working code
- Feature branches = experimental work
- Keep experiments separate from working code

### 3. **Commits = Save Points**
- Like saving a game at checkpoints
- Small, frequent commits are better than big ones
- Each commit has a message explaining what changed

### 4. **Remote Repository = Backup + Collaboration**
- GitHub stores your code in the cloud
- Backup if your laptop dies
- Share with supervisors/team

---

## 📋 COMPLETE WORKFLOW FROM START TO FINISH

### **PHASE 1: Initial Setup (Day 1)**

#### Step 1: Install Git
```bash
# Check if git is installed
git --version

# If not installed:
# Windows: Download from git-scm.com
# Mac: brew install git
# Linux: sudo apt-get install git
```

#### Step 2: Configure Git (First Time Only)
```bash
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Check configuration
git config --list
```

#### Step 3: Create GitHub Account
1. Go to github.com
2. Sign up (free account)
3. Verify your email

#### Step 4: Create Repository on GitHub
1. Click "New Repository" button
2. Name: `mental-health-ai-research`
3. Description: "BSc Research Project: AI-based Mental Health Screening"
4. Choose: Public or Private
5. ✅ Check "Add README"
6. ✅ Add .gitignore (Python template)
7. Click "Create Repository"

#### Step 5: Clone Repository to Your Computer
```bash
# Navigate to where you want the project
cd ~/Documents/Projects

# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/mental-health-ai-research.git

# Enter the project folder
cd mental-health-ai-research

# Verify you're in a git repository
git status
```

**✅ CHECKPOINT: You now have a local copy connected to GitHub**

---

### **PHASE 2: Basic Git Workflow (Daily Work)**

#### The Basic Cycle (You'll do this 100+ times):

```bash
# 1. CHECK STATUS - See what changed
git status

# 2. ADD FILES - Stage changes for commit
git add filename.py                    # Add specific file
git add frontend/src/Chat.jsx          # Add specific file
git add .                              # Add ALL changes (use carefully)

# 3. COMMIT - Save snapshot with message
git commit -m "Add chat interface component"

# 4. PUSH - Upload to GitHub
git push origin main
```

#### Commit Message Best Practices:
```bash
# ✅ GOOD commit messages (clear, specific)
git commit -m "Add PHQ-9 assessment questions"
git commit -m "Fix sentiment analysis bug in feature extraction"
git commit -m "Implement baseline creation algorithm"
git commit -m "Update README with setup instructions"

# ❌ BAD commit messages (vague, useless)
git commit -m "updates"
git commit -m "fixed stuff"
git commit -m "asdf"
git commit -m "more changes"
```

#### Example Real Workflow:

```bash
# Morning: Start working
cd mental-health-ai-research
git status                             # Check if anything changed

# Work on feature extraction for 2 hours
# Created: backend/analysis/feature_extraction.py

git status                             # See new file appears
git add backend/analysis/feature_extraction.py
git commit -m "Implement sentiment and word frequency extraction"
git push origin main

# Work on tests for 1 hour
# Modified: backend/analysis/feature_extraction.py
# Created: backend/tests/test_features.py

git status                             # See both files
git add .
git commit -m "Add unit tests for feature extraction"
git push origin main

# End of day: Everything saved and backed up
```

---

### **PHASE 3: Branch Strategy**

#### Main Branch Structure:

```
main (or master)
├── Always working, stable code
├── What you deploy/demonstrate
└── Protected - only merge tested features

feature branches
├── sprint-1-setup
├── sprint-2-ai-integration
├── sprint-3-assessments
├── sprint-4-anomaly-detection
└── Each sprint gets its own branch
```

#### Creating and Using Branches:

```bash
# CHECK which branch you're on
git branch                             # Shows all branches, * = current

# CREATE new branch for Sprint 1
git branch sprint-1-setup
git checkout sprint-1-setup           # Switch to new branch

# OR create and switch in one command
git checkout -b sprint-1-setup

# Now work on Sprint 1 tasks
# ... edit files, add features ...

# Commit work on this branch
git add .
git commit -m "Set up FastAPI backend structure"
git push origin sprint-1-setup        # Push branch to GitHub

# When Sprint 1 is complete and TESTED:
git checkout main                      # Switch back to main
git merge sprint-1-setup              # Merge sprint work into main
git push origin main                   # Push updated main to GitHub

# Delete branch (optional, if done)
git branch -d sprint-1-setup
```

#### Real Example for Your Project:

```bash
# Week 1: Start Sprint 1
git checkout -b sprint-1-setup

# Day 1: Setup backend
# ... create backend files ...
git add backend/
git commit -m "Initialize FastAPI project structure"

# Day 2: Setup frontend  
# ... create frontend files ...
git add frontend/
git commit -m "Initialize React project with Vite"

# Day 3: Add authentication
# ... create auth endpoints ...
git add backend/routes/auth.py backend/models/user.py
git commit -m "Add user registration and login endpoints"

# Push branch regularly
git push origin sprint-1-setup

# End of Week 2: Sprint 1 complete
# Test everything works
git checkout main
git merge sprint-1-setup
git push origin main

# Week 3: Start Sprint 2
git checkout -b sprint-2-ai-integration
# ... continue ...
```

---

### **PHASE 4: Handling Mistakes & Rollbacks**

#### Scenario 1: Undo Last Commit (Not Pushed Yet)

```bash
# Made a commit but want to undo it
git log                                # See commit history
git reset --soft HEAD~1                # Undo commit, keep changes
# OR
git reset --hard HEAD~1                # Undo commit, DELETE changes (careful!)

# Example:
git commit -m "Add feature"            # Oops, wrong files
git reset --soft HEAD~1                # Undo, files still changed
git add correct_file.py                # Add correct files
git commit -m "Add feature correctly"
```

#### Scenario 2: Undo Changes Before Commit

```bash
# Made changes but want to discard them
git status                             # See what changed
git checkout -- filename.py            # Discard changes to one file
git checkout -- .                      # Discard ALL changes (careful!)

# Example:
# Edited feature_extraction.py but broke everything
git checkout -- backend/analysis/feature_extraction.py
# File reverts to last committed version
```

#### Scenario 3: Revert a Pushed Commit

```bash
# Already pushed a bad commit to GitHub
git log                                # Find commit hash (e.g., abc123)
git revert abc123                      # Creates new commit that undoes it
git push origin main

# Example:
git log
# commit abc123 "Broken anomaly detection"
# commit def456 "Working baseline creation"

git revert abc123                      # Undoes the broken commit
git push origin main                   # Push the fix
```

#### Scenario 4: Go Back to Specific Point in Time

```bash
# Want to see code from 2 weeks ago
git log --oneline                      # See all commits
git checkout abc123                    # Go to that commit (detached state)
# Look around, test code
git checkout main                      # Come back to present

# Want to RESTORE that old version permanently
git log --oneline
git checkout abc123 filename.py        # Bring old version of file to present
git commit -m "Restore previous working version"
git push origin main
```

#### Scenario 5: Merge Conflict Resolution

```bash
# When merging branches, sometimes conflicts occur

git checkout main
git merge sprint-2-ai-integration
# CONFLICT in backend/main.py

# Git marks conflicts in files like this:
<<<<<<< HEAD
# Code from main branch
=======
# Code from sprint-2 branch
>>>>>>> sprint-2-ai-integration

# 1. Open the file
# 2. Manually choose which code to keep
# 3. Remove the markers (<<<, ===, >>>)
# 4. Save file

git add backend/main.py               # Mark as resolved
git commit -m "Resolve merge conflict in main.py"
git push origin main
```

---

### **PHASE 5: Advanced Workflows**

#### Working on Multiple Sprints Simultaneously

```bash
# Working on Sprint 2, but need to fix bug in Sprint 1

# Currently on sprint-2-ai-integration
git status                            # Save or commit current work

# Switch to main, create hotfix branch
git checkout main
git checkout -b hotfix-auth-bug

# Fix the bug
git add backend/routes/auth.py
git commit -m "Fix JWT token expiration bug"

# Merge hotfix to main
git checkout main
git merge hotfix-auth-bug
git push origin main

# Go back to Sprint 2 work
git checkout sprint-2-ai-integration
git merge main                        # Get the hotfix into sprint-2 too
# Continue working
```

#### Stashing (Temporary Save)

```bash
# Need to switch branches but current work isn't ready to commit

git stash                             # Save current changes temporarily
git checkout other-branch             # Switch branches
# ... do other work ...
git checkout original-branch
git stash pop                         # Restore saved changes
```

---

### **PHASE 6: Collaboration with Supervisor**

#### Sharing Your Work:

```bash
# Push your work regularly
git push origin main

# Your supervisor can view on GitHub
# Send them: https://github.com/YOUR_USERNAME/mental-health-ai-research
```

#### Getting Feedback:

```bash
# Supervisor suggests changes

# 1. They can comment on GitHub (no code change)
# 2. They can create an "Issue" on GitHub
# 3. They can fork and create "Pull Request"

# You make changes based on feedback
git add .
git commit -m "Implement supervisor feedback on anomaly threshold"
git push origin main
```

#### Creating a Release (For Thesis Submission):

```bash
# When ready to submit
git tag -a v1.0 -m "Final submission version"
git push origin v1.0

# Or on GitHub:
# Releases → Create new release → Tag: v1.0
# This creates a permanent snapshot
```

---

## 🗂️ .gitignore (What NOT to Upload)

Create `.gitignore` file in project root:

```gitignore
# Python
__pycache__/
*.py[cod]
venv/
env/
*.egg-info/

# Node
node_modules/
dist/
build/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Data files (large)
*.csv
*.xlsx
data/raw/

# Model files (very large)
*.bin
*.pt
*.h5
models/pretrained/

# Database
*.db
*.sqlite

# Logs
*.log
logs/
```

---

## 📊 Recommended Branch Strategy for Your Project

```
main
├── Always working, demonstrable code
└── What you show your supervisor

sprint-1-setup (Week 1-2)
├── Basic infrastructure
└── Merge to main when complete

sprint-2-ai-integration (Week 3-4)
├── AI model integration
└── Merge to main when tested

sprint-3-assessments (Week 5-6)
├── PHQ-9 and GAD-7
└── Merge to main when validated

sprint-4-anomaly-detection (Week 7-8)
├── Core research contribution
└── Merge to main when tested

sprint-5-validation (Week 9-10)
├── Testing and validation
└── Merge to main when complete

thesis (Week 11-12)
├── Documentation branch
├── Keep separate from code
└── For thesis writing, figures, etc.
```

---

## 🚀 Daily Workflow Checklist

### Every Morning:
```bash
git status                   # Check current state
git pull origin main         # Get latest from GitHub
git checkout -b today-work   # Create branch for today (optional)
```

### Throughout Day:
```bash
# After completing each small task
git add .
git commit -m "Descriptive message"

# Every hour or two
git push origin current-branch
```

### Every Evening:
```bash
git status                   # Make sure everything is committed
git push origin current-branch   # Backup to GitHub
```

### End of Sprint:
```bash
# Test everything works
git checkout main
git merge sprint-X-name
git push origin main
git tag -a sprint-X -m "Sprint X complete"
git push origin sprint-X
```

---

## ⚠️ Common Mistakes & Solutions

### Mistake 1: "I committed to the wrong branch!"
```bash
# Created commits on main instead of feature branch
git branch feature-branch    # Create branch with current commits
git reset --hard origin/main # Reset main to match GitHub
git checkout feature-branch  # Switch to feature branch
# Your commits are now on feature-branch
```

### Mistake 2: "I have merge conflicts!"
```bash
# Don't panic, read the conflict markers
# Manually edit files to resolve
git add resolved-file.py
git commit -m "Resolve merge conflict"
```

### Mistake 3: "I deleted something important!"
```bash
git log                      # Find commit where file existed
git checkout abc123 -- lost-file.py
git commit -m "Restore lost file"
```

### Mistake 4: "I pushed sensitive data (API key)!"
```bash
# Remove from latest commit
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Remove sensitive file"
git push origin main --force  # Overwrites history

# Change the exposed API key immediately!
```

---

## 📅 Git Timeline for 12-Week Project

### Week 1:
- Day 1: Initial repo setup
- Day 2-7: 5-10 commits (setup work)

### Week 2-10:
- 2-3 commits per day
- Push to GitHub daily
- Merge sprint branches every 2 weeks

### Week 11-12:
- Frequent commits (documentation)
- Final release tag before submission

### Total Expected:
- **150-200 commits** over 12 weeks
- **6-8 branches** (one per sprint)
- **5-6 releases/tags** (sprint milestones + final)

---

## 🎓 For Your Thesis

Include in your thesis:
- GitHub repository link
- Commit history screenshots (shows development process)
- Branch strategy diagram
- Release tags for major milestones

This demonstrates:
- Professional development practices
- Organized workflow
- Iterative development
- Version control proficiency

---

## 📖 Quick Reference Commands

```bash
# BASICS
git status                   # Check status
git add .                    # Stage all changes
git commit -m "message"      # Commit with message
git push origin main         # Upload to GitHub
git pull origin main         # Download from GitHub

# BRANCHES
git branch                   # List branches
git branch name              # Create branch
git checkout name            # Switch branch
git checkout -b name         # Create and switch
git merge branch             # Merge branch into current

# HISTORY
git log                      # Show commits
git log --oneline           # Compact view
git diff                     # Show changes

# UNDO
git checkout -- file         # Discard changes
git reset --soft HEAD~1      # Undo last commit
git revert abc123           # Undo specific commit

# REMOTE
git remote -v               # Show remote URLs
git clone url               # Copy repository
```

---

## 🎯 Summary

**Git = Your project's safety net**
- Commit often (every small completed task)
- Push daily (backup to GitHub)
- Use branches (keep experiments separate)
- Write clear messages (your future self will thank you)

**For your BSc project:**
- Main branch = always working
- Sprint branches = development work
- Commits = progress documentation
- Tags = milestone markers

**Remember:**
- Git is forgiving - almost anything can be undone
- When in doubt, commit and push
- Your commit history tells the story of your research journey

---

*Pro tip: Get comfortable with these commands in Week 1. They'll become second nature by Week 3.*