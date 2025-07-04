#!/usr/bin/env python3
"""
Pre-deployment verification script for Render deployment
Checks that all necessary files and configurations are in place
"""

import os
import json
import yaml
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and return status"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def check_docker_file(dockerfile_path, service_name):
    """Check Dockerfile for production readiness"""
    print(f"\n🐳 Checking {service_name} Dockerfile...")
    
    if not check_file_exists(dockerfile_path, f"{service_name} Dockerfile"):
        return False
    
    with open(dockerfile_path, 'r') as f:
        content = f.read()
    
    checks = {
        "Multi-stage build (Frontend)": "AS base" in content if "frontend" in service_name.lower() else True,
        "Health check": "HEALTHCHECK" in content,
        "Non-root user": "USER" in content,
        "Environment variables": "ENV" in content,
        "Proper CMD": "CMD" in content
    }
    
    for check, passed in checks.items():
        status = "✅" if passed else "⚠️ "
        print(f"  {status} {check}")
    
    return all(checks.values())

def check_render_yaml():
    """Check render.yaml configuration"""
    print(f"\n📋 Checking render.yaml configuration...")
    
    if not check_file_exists("render.yaml", "Render configuration"):
        return False
    
    try:
        with open("render.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        services = config.get('services', [])
        if len(services) != 2:
            print(f"❌ Expected 2 services, found {len(services)}")
            return False
        
        service_names = [s.get('name') for s in services]
        expected_services = ['ocr-invoice-backend', 'ocr-invoice-frontend']
        
        for service in expected_services:
            if service in service_names:
                print(f"✅ Service configured: {service}")
            else:
                print(f"❌ Missing service: {service}")
                return False
        
        # Check for required environment variables
        for service in services:
            name = service.get('name')
            env_vars = service.get('envVars', [])
            env_keys = [var.get('key') for var in env_vars]
            
            if 'backend' in name:
                required_backend_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY', 'JWT_SECRET']
                for var in required_backend_vars:
                    if var in env_keys:
                        print(f"✅ Backend env var configured: {var}")
                    else:
                        print(f"⚠️  Backend env var needs manual setup: {var}")
            
            elif 'frontend' in name:
                required_frontend_vars = ['NEXT_PUBLIC_SUPABASE_URL', 'NEXT_PUBLIC_API_URL']
                for var in required_frontend_vars:
                    if var in env_keys:
                        print(f"✅ Frontend env var configured: {var}")
                    else:
                        print(f"❌ Missing frontend env var: {var}")
        
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML format: {e}")
        return False

def check_next_config():
    """Check Next.js configuration"""
    print(f"\n⚛️  Checking Next.js configuration...")
    
    config_path = "frontend/next.config.js"
    if not check_file_exists(config_path, "Next.js config"):
        return False
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    checks = {
        "Standalone output": "output: 'standalone'" in content,
        "Conditional rewrites": "NODE_ENV" in content and "development" in content,
        "PDF.js config": "canvas: false" in content
    }
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    return all(checks.values())

def check_cors_config():
    """Check CORS configuration in backend"""
    print(f"\n🌐 Checking CORS configuration...")
    
    main_py_path = "backend/main.py"
    if not check_file_exists(main_py_path, "Backend main.py"):
        return False
    
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    production_urls = [
        "ocr-invoice-frontend.onrender.com",
        "ocr-invoice-backend.onrender.com"
    ]
    
    for url in production_urls:
        if url in content:
            print(f"✅ Production URL in CORS: {url}")
        else:
            print(f"❌ Missing production URL in CORS: {url}")
            return False
    
    return True

def main():
    """Run all verification checks"""
    print("🔍 Pre-deployment Verification for Render")
    print("=" * 50)
    
    current_dir = os.getcwd()
    project_name = os.path.basename(current_dir)
    
    if "ocr-invoice-processor" not in project_name:
        print("⚠️  Warning: Run this script from the project root directory")
    
    # Check project structure
    print(f"\n📁 Project: {project_name}")
    print(f"📍 Directory: {current_dir}")
    
    checks = []
    
    # Essential files
    essential_files = [
        ("render.yaml", "Render Blueprint"),
        ("backend/Dockerfile", "Backend Docker config"),
        ("frontend/Dockerfile", "Frontend Docker config"),
        ("backend/main.py", "Backend application"),
        ("frontend/next.config.js", "Frontend config"),
        ("backend/requirements.txt", "Backend dependencies"),
        ("frontend/package.json", "Frontend dependencies")
    ]
    
    for file_path, description in essential_files:
        checks.append(check_file_exists(file_path, description))
    
    # Detailed checks
    checks.append(check_render_yaml())
    checks.append(check_docker_file("backend/Dockerfile", "Backend"))
    checks.append(check_docker_file("frontend/Dockerfile", "Frontend"))
    checks.append(check_next_config())
    checks.append(check_cors_config())
    
    # Summary
    print(f"\n📊 VERIFICATION SUMMARY")
    print("=" * 30)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"🎉 All checks passed! ({passed}/{total})")
        print("✅ Ready for Render deployment!")
        print("\n🚀 Next step: Run ./deploy-to-render.sh")
    else:
        print(f"⚠️  {total - passed} issues found ({passed}/{total} passed)")
        print("❌ Please fix the issues above before deploying")
    
    print(f"\n📚 For detailed instructions, see: RENDER_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main()
