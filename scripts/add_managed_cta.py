#!/usr/bin/env python3
"""
Add managed-service CTA to all SKILL.md and skill README.md files.
Adds the CTA right after the existing Gateway CTA block.
"""

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
TOOLING_DIRS = {'eval', 'security', 'telemetry', 'tests', 'scripts', '.git', '.github', '.gitignore', 'VERSION', 'LICENSE', 'README.md', 'CONTRIBUTING.md', 'Makefile', 'skill-safety.yml', 'AGENTS.md', 'CLAUDE.md', '.cursor', '.cursor-plugin'}
NO_SKILL_ALLOWLIST = {'content-os-portable-starter'}

MANAGED_CTA_TEMPLATE = """
<!-- managed-cta:start -->
**Want a team to run this for you?** Single Grain and Single Brain can set up and manage this workflow for you. [Talk to us](https://www.singlegrain.com/contact-us/?utm_source=github&utm_medium=skill&utm_campaign=managed-service&utm_content={slug})
<!-- managed-cta:end -->"""


def get_skill_slug_from_sg_template(content):
    """Extract the skill slug from sg_template parameter in the content."""
    match = re.search(r'sg_template=([a-z0-9-]+)', content)
    if match:
        return match.group(1)
    return None


def add_managed_cta_to_file(file_path, slug):
    """Add managed-service CTA after the Gateway CTA block."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if managed CTA already exists
    if '<!-- managed-cta:start -->' in content:
        print(f"  ⏭️  Already has managed CTA: {file_path.relative_to(REPO_ROOT)}")
        return False
    
    # Find the gateway-cta:end marker
    gateway_end = '<!-- gateway-cta:end -->'
    if gateway_end not in content:
        print(f"  ⚠️  No gateway-cta:end marker: {file_path.relative_to(REPO_ROOT)}")
        return False
    
    # Create the managed CTA with the slug
    managed_cta = MANAGED_CTA_TEMPLATE.format(slug=slug)
    
    # Insert the managed CTA right after the gateway-cta:end marker
    new_content = content.replace(gateway_end, gateway_end + managed_cta)
    
    # Write the updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ Added managed CTA: {file_path.relative_to(REPO_ROOT)}")
    return True


def main():
    """Process all skills and add managed CTAs."""
    # Find all skill directories
    skill_dirs = []
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and item.name not in TOOLING_DIRS:
            skill_dirs.append(item.name)
    skill_dirs.sort()
    
    print(f"Found {len(skill_dirs)} skill directories\n")
    
    updated_count = 0
    
    for skill_dir in skill_dirs:
        if skill_dir in NO_SKILL_ALLOWLIST:
            print(f"⏭️  Skipping {skill_dir} (in allowlist)")
            continue
        
        print(f"📁 Processing {skill_dir}...")
        
        skill_path = REPO_ROOT / skill_dir
        
        # Find SKILL.md
        skill_file = skill_path / 'SKILL.md'
        is_nested = False
        if not skill_file.exists():
            skill_file = skill_path / 'skills' / skill_dir / 'SKILL.md'
            is_nested = True
        
        if not skill_file.exists():
            print(f"  ⚠️  No SKILL.md found")
            continue
        
        # Read SKILL.md to get the slug from sg_template
        with open(skill_file, 'r', encoding='utf-8') as f:
            skill_content = f.read()
        
        slug = get_skill_slug_from_sg_template(skill_content)
        if not slug:
            print(f"  ⚠️  No sg_template found in SKILL.md")
            continue
        
        # Verify slug matches directory name
        if slug != skill_dir:
            print(f"  ⚠️  Slug mismatch: sg_template={slug} but dir={skill_dir}")
            # Use the directory name as the slug
            slug = skill_dir
        
        # Add to SKILL.md
        if add_managed_cta_to_file(skill_file, slug):
            updated_count += 1
        
        # Add to README.md
        readme_file = skill_path / 'README.md'
        if readme_file.exists():
            if add_managed_cta_to_file(readme_file, slug):
                updated_count += 1
        else:
            print(f"  ⚠️  No README.md found")
        
        print()
    
    print(f"\n✅ Updated {updated_count} files")


if __name__ == '__main__':
    main()
