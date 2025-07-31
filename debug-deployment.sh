#!/bin/bash

echo "🔍 Debugging Blueprint Deployment Failures..."
echo "================================================"

# Check current branch
echo "🌿 Current branch: $(git branch --show-current)"

# Check if required files exist
echo ""
echo "📁 Checking required files..."
echo "Backend Dockerfile: $([ -f "backend/Dockerfile" ] && echo "✅ EXISTS" || echo "❌ MISSING")"
echo "Frontend Dockerfile: $([ -f "frontend/Dockerfile" ] && echo "✅ EXISTS" || echo "❌ MISSING")"
echo "Backend requirements.txt: $([ -f "backend/requirements.txt" ] && echo "✅ EXISTS" || echo "❌ MISSING")"
echo "Frontend package.json: $([ -f "frontend/package.json" ] && echo "✅ EXISTS" || echo "❌ MISSING")"
echo "render.yaml: $([ -f "render.yaml" ] && echo "✅ EXISTS" || echo "❌ MISSING")"

# Check email-validator in requirements
echo ""
echo "📦 Checking Python dependencies..."
if [ -f "backend/requirements.txt" ]; then
    if grep -q "email-validator" backend/requirements.txt; then
        echo "✅ email-validator found in requirements.txt"
    else
        echo "❌ email-validator missing from requirements.txt"
    fi
    echo "📋 Current requirements.txt content:"
    head -15 backend/requirements.txt
else
    echo "❌ requirements.txt not found"
fi

# Check Dockerfile structure
echo ""
echo "🐳 Checking Backend Dockerfile..."
if [ -f "backend/Dockerfile" ]; then
    echo "📋 Dockerfile CMD line:"
    grep -n "CMD" backend/Dockerfile || echo "❌ No CMD found"
    echo "📋 Dockerfile EXPOSE line:"
    grep -n "EXPOSE" backend/Dockerfile || echo "❌ No EXPOSE found"
else
    echo "❌ Backend Dockerfile not found"
fi

# Check render.yaml syntax
echo ""
echo "📄 Checking render.yaml configuration..."
if [ -f "render.yaml" ]; then
    echo "📋 Services defined:"
    grep -A2 "name:" render.yaml
    echo "📋 Branch configuration:"
    grep "branch:" render.yaml
    echo "📋 Environment type:"
    grep "env:" render.yaml
else
    echo "❌ render.yaml not found"
fi

# Check recent commits
echo ""
echo "📝 Recent commits (last 3):"
git log --oneline -3

echo ""
echo "🔍 Diagnostic complete!"
echo "================================================"
