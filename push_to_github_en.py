#!/usr/bin/env python3
"""
GitHub Push Helper Script
"""
import subprocess
import os
import sys

def run_command(cmd, description):
    """Run command and show result"""
    print(f"\nExecuting: {description}")
    print(f"Command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"Success: {description}")
            if result.stdout:
                print(f"Output: {result.stdout}")
        else:
            print(f"Failed: {description}")
            if result.stderr:
                print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    """Main function"""
    print("GitHub Push Helper")
    print("=" * 50)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check if it's a Git repository
    if not os.path.exists('.git'):
        print("Current directory is not a Git repository")
        return
    
    print("Current directory is a Git repository")
    
    # Check Git status
    if not run_command("git status", "Check Git status"):
        return
    
    # Add all files
    if not run_command("git add .", "Add all files to staging area"):
        return
    
    # Commit changes
    if not run_command('git commit -m "Update for Railway deployment"', "Commit changes"):
        return
    
    print("\n" + "=" * 50)
    print("Git operations completed!")
    print("\nNow please manually execute the following steps:")
    print("\n1. Create a new repository on GitHub:")
    print("   - Visit https://github.com")
    print("   - Click 'New repository'")
    print("   - Repository name: block-trade-dt")
    print("   - Set as public repository")
    print("   - Click 'Create repository'")
    
    print("\n2. Add remote repository and push:")
    print("   git remote add origin https://github.com/YOUR_USERNAME/block-trade-dt.git")
    print("   git branch -M main")
    print("   git push -u origin main")
    
    print("\nNote: Replace YOUR_USERNAME with your GitHub username")

if __name__ == "__main__":
    main()

