#!/usr/bin/env bash
set -euo pipefail

# OpenClaw batch installer for AI Marketing Skills
# Finds all SKILL.md files and installs each skill directory

# Find repo root from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if openclaw is installed
if ! command -v openclaw &> /dev/null; then
    echo "Error: openclaw command not found. Please install OpenClaw first."
    exit 1
fi

# Function to install a skill
install_skill() {
    local skill_dir="$1"
    echo "Installing skill: $skill_dir"
    openclaw skills install "$skill_dir"
}

# If arguments provided, install only those slugs
if [ $# -gt 0 ]; then
    for slug in "$@"; do
        skill_dir="$REPO_ROOT/$slug"
        if [ -d "$skill_dir" ]; then
            # Check if SKILL.md exists (direct or nested)
            if [ -f "$skill_dir/SKILL.md" ] || [ -f "$skill_dir/skills/$slug/SKILL.md" ]; then
                install_skill "$skill_dir"
            else
                echo "Warning: No SKILL.md found in $slug, skipping"
            fi
        else
            echo "Warning: Directory $slug not found, skipping"
        fi
    done
    exit 0
fi

# No arguments: install all skills
cd "$REPO_ROOT"

# Find all SKILL.md files, excluding .git and node_modules
while IFS= read -r -d '' skill_file; do
    # Get the directory containing SKILL.md
    skill_dir="$(dirname "$skill_file")"
    
    # Make path absolute
    skill_dir="$REPO_ROOT/$skill_dir"
    
    # Install the skill directory that directly contains SKILL.md
    install_skill "$skill_dir"
done < <(find . -name "SKILL.md" -type f \
    -not -path "./.git/*" \
    -not -path "*/node_modules/*" \
    -print0 | sort -z)

echo "All skills installed successfully!"
