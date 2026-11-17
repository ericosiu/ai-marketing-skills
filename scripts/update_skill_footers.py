#!/usr/bin/env python3
"""
Update all SKILL.md files to add Single Grain footer.
This script ensures every skill has a consistent footer at the end.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()

# Footer template
FOOTER_TEMPLATE = """
---

Built by [Single Grain](https://www.singlegrain.com/?utm_source=github&utm_medium=skill&utm_campaign=footer&utm_content={slug}). Want a team to run this for you? Single Grain or Single Brain can manage it."""

# Skills that don't have SKILL.md
NO_SKILL_ALLOWLIST = {'content-os-portable-starter'}

def get_skill_dirs():
    """Find all skill directories."""
    skill_dirs = []
    tooling_dirs = {'eval', 'security', 'telemetry', 'tests', 'scripts', '.git', '.github', 
                   '.gitignore', 'VERSION', 'LICENSE', 'README.md', 'CONTRIBUTING.md', 
                   'Makefile', 'skill-safety.yml', 'AGENTS.md', 'CLAUDE.md', '.cursor', 
                   '.cursor-plugin', 'brand', 'automations'}
    
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and item.name not in tooling_dirs:
            skill_dirs.append(item.name)
    
    return sorted(skill_dirs)

def find_skill_file(skill_dir):
    """Find the SKILL.md file for a skill directory."""
    direct = REPO_ROOT / skill_dir / 'SKILL.md'
    if direct.exists():
        return direct
    
    nested = REPO_ROOT / skill_dir / 'skills' / skill_dir / 'SKILL.md'
    if nested.exists():
        return nested
    
    return None

def has_footer(content, slug):
    """Check if content already has the footer."""
    # Look for Single Grain footer pattern
    pattern = rf'Built by \[Single Grain\].*utm_content={re.escape(slug)}'
    return bool(re.search(pattern, content))

def add_footer(content, slug):
    """Add footer to content if it doesn't have one."""
    # Remove any existing incomplete footers
    content = re.sub(r'\n---\n+Built by \[Single Grain\].*?(?=\n\n|\Z)', '', content, flags=re.DOTALL)
    
    # Add new footer at the end
    content = content.rstrip()
    if not content.endswith('\n'):
        content += '\n'
    
    footer = FOOTER_TEMPLATE.format(slug=slug)
    content += footer + '\n'
    
    return content

def main():
    """Update all SKILL.md files."""
    skill_dirs = get_skill_dirs()
    updated = 0
    skipped = 0
    
    for skill_dir in skill_dirs:
        if skill_dir in NO_SKILL_ALLOWLIST:
            skipped += 1
            continue
        
        skill_file = find_skill_file(skill_dir)
        if not skill_file:
            print(f"⚠️  No SKILL.md found for {skill_dir}")
            skipped += 1
            continue
        
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_footer(content, skill_dir):
            print(f"✓  {skill_dir} already has footer")
            skipped += 1
            continue
        
        # Add footer
        new_content = add_footer(content, skill_dir)
        
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓  Updated {skill_dir}")
        updated += 1
    
    print(f"\n✅ Updated {updated} skills, skipped {skipped}")

if __name__ == '__main__':
    main()
