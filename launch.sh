#!/bin/bash
# SynapseVibe Labs — LAUNCH AUTOMATION SCRIPT
# Run this to prepare everything for deployment

set -e

echo "=========================================="
echo "  SynapseVibe Labs — Launch Prep"
echo "=========================================="
echo ""

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "📁 Project directory: $PROJECT_DIR"
echo ""

# Step 1: Initialize Git repo
echo "🔄 Step 1: Initializing Git repository..."
if [ ! -d ".git" ]; then
    git init
    git branch -m main
    echo "✅ Git repo initialized"
else
    echo "✅ Git repo already exists"
fi

# Step 2: Create .gitignore
echo "🔄 Step 2: Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# Docker
*.log
EOF
echo "✅ .gitignore created"

# Step 3: Stage all files
echo "🔄 Step 3: Staging files..."
git add -A
echo "✅ Files staged"

# Step 4: Initial commit
echo "🔄 Step 4: Creating initial commit..."
git commit -m "🚀 Initial commit: SynapseVibe Labs foundation

- Brand identity and website
- AgentStack open-source project
- Newsletter Issue #0
- Playbook chapters 1-2
- SEO articles and outreach templates
- Twitter threads and content calendar

Built with ⚡ and way too much caffeine."
echo "✅ Initial commit created"

# Step 5: Prepare GitHub remote (user needs to create repo first)
echo ""
echo "=========================================="
echo "  NEXT STEPS (Manual)"
echo "=========================================="
echo ""
echo "1. Create GitHub repository:"
echo "   → Go to https://github.com/new"
echo "   → Owner: synapsevibe-labs (create org first)"
echo "   → Repo name: agentstack"
echo "   → Visibility: Public"
echo "   → DO NOT initialize with README"
echo ""
echo "2. Then run these commands:"
echo "   git remote add origin https://github.com/synapsevibe-labs/agentstack.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

# Step 6: Prepare Vercel deployment
echo "🔄 Step 5: Preparing Vercel configuration..."
mkdir -p website
cat > website/vercel.json << 'EOF'
{
  "version": 2,
  "name": "synapsevibe-website",
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
EOF
echo "✅ Vercel config created"

# Step 7: Create deploy script
echo "🔄 Step 6: Creating deploy script..."
cat > deploy.sh << 'EOF'
#!/bin/bash
# Quick deploy script

echo "Deploying SynapseVibe Labs..."

# Deploy website
echo "Deploying website to Vercel..."
cd website
vercel --prod
cd ..

echo "✅ Deployment complete!"
EOF
chmod +x deploy.sh
echo "✅ Deploy script created"

# Step 8: Create content ready to copy-paste
echo "🔄 Step 7: Preparing social media content..."
mkdir -p ready-to-post

# Twitter bio
cat > ready-to-post/twitter-bio.txt << 'EOF'
SynapseVibe Labs
@synapsevibe

Building production-grade agentic systems at the speed of vibe coding.

⚡ AgentStack → github.com/synapsevibe-labs/agentstack
📧 Newsletter → synapsevibe.substack.com
🌐 Website → synapsevibe.com

Where agentic infrastructure meets creative velocity.
EOF

# Substack about page
cat > ready-to-post/substack-about.md << 'EOF'
# About The SynapseVibe Dispatch

The SynapseVibe Dispatch is a weekly newsletter about agentic engineering, vibe coding, and the infrastructure that makes AI agents work in production.

Written by SynapseVibe Labs — a collective of platform engineers and vibe coders building the future of agentic software.

## What We Cover

- **Agentic Engineering** — Orchestration, context engineering, multi-agent architectures
- **Vibe Coding** — Rapid prototyping, AI-assisted development, productionization
- **Platform Patterns** — Infrastructure, deployment, observability for agent systems
- **Tool Reviews** — Honest takes on what's worth your time
- **Case Studies** — Real projects, real numbers, real lessons

## Why Subscribe?

- Weekly deep-dives (no fluff, no spam)
- Early access to open-source tools
- Exclusive content not published elsewhere
- Direct replies to every email

## About SynapseVibe Labs

We build production-grade agentic systems and teach others how to do the same — at the speed of vibe coding.

- 🌐 Website: https://synapsevibe.com
- 🐦 Twitter: https://twitter.com/synapsevibe
- 🐙 GitHub: https://github.com/synapsevibe-labs

Built with ⚡ and way too much caffeine.
EOF

# LinkedIn company description
cat > ready-to-post/linkedin-about.txt << 'EOF'
SynapseVibe Labs is a collective of platform engineers and vibe coders building production-grade agentic systems.

We specialize in:
⚡ Agentic Platform Engineering
🚀 Vibe MVP Development
🧠 Multi-Agent Systems
🔧 MCP & Tool Integration
📊 Agent Observability
🎯 Technical Strategy

Our mission: Build the infrastructure for the agentic future — and teach others how to do the same.

Website: https://synapsevibe.com
GitHub: https://github.com/synapsevibe-labs
Newsletter: https://synapsevibe.substack.com

Where agentic infrastructure meets creative velocity.
EOF

# Gumroad product description
cat > ready-to-post/gumroad-playbook.md << 'EOF'
# The Agentic Engineer's Playbook

**A comprehensive guide to building production-grade agentic systems.**

From first prototype to production deployment, this playbook covers everything you need to know about agentic engineering in 2026.

## What's Inside

**Part 1: Foundations**
- The Agentic Paradigm
- From Vibe Coding to Production
- The Agentic SDLC

**Part 2: Architecture**
- Single-Agent Design Patterns
- Multi-Agent Orchestration
- The Agent Control Plane

**Part 3: Implementation**
- Context Engineering
- MCP Servers & Tool Integration
- Memory & State Management

**Part 4: Production**
- Observability for Agents
- Testing & Evaluation
- Governance & Safety
- Deployment Patterns

**Part 5: Case Studies**
- Customer Support Agent Fleet
- Autonomous Data Pipeline
- Code Review Agent

## Who This Is For

- Platform Engineers building infrastructure for AI agents
- Vibe Coders ready to productionize their prototypes
- Engineering Managers evaluating agentic architecture
- Indie Hackers building agent-powered products

## Packages

**🎓 Playbook Only** — $49
- Full PDF
- Lifetime updates

**🚀 Playbook + Templates** — $99
- Everything in Playbook Only
- Notion templates
- Code examples
- Architecture diagrams

**💎 Complete Bundle** — $199
- Everything above
- Video walkthroughs
- Private community access
- 1-on-1 architecture review

## About the Authors

SynapseVibe Labs is a collective of platform engineers and vibe coders who have deployed production agentic systems for the past year. We've made the mistakes so you don't have to.

Website: https://synapsevibe.com
EOF

echo "✅ Social media content prepared"

# Step 9: Create first tweet ready to post
cat > ready-to-post/first-tweet.txt << 'EOF'
🚀 We just launched AgentStack — a production-ready starter kit for building agentic systems.

Built by vibe coders, for vibe coders.

→ Multi-agent orchestration
→ MCP server integration
→ Context engineering toolkit
→ Production observability

Open source. MIT licensed. Ready to use.

⭐ github.com/synapsevibe-labs/agentstack

#AI #AgenticEngineering #OpenSource
EOF

echo ""
echo "=========================================="
echo "  ✅ LAUNCH PREP COMPLETE"
echo "=========================================="
echo ""
echo "Your project is ready! Here's what's prepared:"
echo ""
echo "📦 Git repo initialized and committed"
echo "🚀 Vercel config ready"
echo "📱 Social media bios/content ready to copy-paste"
echo "📝 First tweet ready to post"
echo "📧 Newsletter content ready"
echo ""
echo "📋 YOUR TASKS (with exact steps below):"
echo ""
echo "1. Buy domain → See STEP_BY_STEP.md"
echo "2. Create accounts → See STEP_BY_STEP.md"
echo "3. Push to GitHub → See STEP_BY_STEP.md"
echo "4. Deploy website → See STEP_BY_STEP.md"
echo ""
echo "All instructions are in STEP_BY_STEP.md"
echo ""
