#!/usr/bin/env python3
"""
Repository contract tests for AI Marketing Skills.
Tests skill structure, frontmatter, Gateway CTAs, and installer files.
"""

import os
import re
import sys
import json
import unittest
from pathlib import Path


# Allowed imports: os, re, sys, json, pathlib, unittest
# No network calls, no external dependencies


REPO_ROOT = Path(__file__).parent.parent.resolve()
TOOLING_DIRS = {'eval', 'security', 'telemetry', 'tests', 'scripts', '.git', '.github', '.gitignore', 'VERSION', 'LICENSE', 'README.md', 'CONTRIBUTING.md', 'Makefile', 'skill-safety.yml', 'AGENTS.md', 'CLAUDE.md', '.cursor', '.cursor-plugin', 'brand', 'automations'}
NO_SKILL_ALLOWLIST = {'content-os-portable-starter'}
SLUG_REGEX = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')

# Allowed service names for CTA blocks
ALLOWED_SERVICES = {
    'Google Analytics and Search Console',
    'Google Ads',
    'Google Workspace',
    'YouTube',
    'Slack',
    'HubSpot CRM',
    'Asana',
    'Coda',
    'Gong',
    'ClickFlow',
    'Instantly',
    'GitHub',
    'Sume',
    'Mixpanel',
    'Stripe',
    'Meta Ads',
    'LinkedIn Ads',
    'Microsoft Ads',
    'SEO research',
    'embeddings',
    'B2B prospecting',
    'Perplexity Sonar',
    'web search',
    'social profile search',
    'Apify',
    'email finder',
    'ElevenLabs',
    'music',
    'Jev',
    'Grok X Search',
    'Model Rail',
    'account tools',
}

FALLBACK_SERVICES = 'see the full list in the setup file'

# Hero slugs that must come first in README tables
HERO_SLUGS = [
    'seo-ops',
    'outbound-engine',
    'lead-dossier',
    'sales-pipeline',
    'conversion-ops',
    'revenue-intelligence',
    'growth-engine',
]

# Skills in other groups (for ordering check)
VIDEO_AUDIO_SLUGS = [
    'podcast-ops',
    'leveling-up-content-engine',
    'yt-competitive-analysis',
    'packaging-youtube-thumbnails',
    'video-content-engine',
    'video-analysis',
    'agentic-video-understanding',
    'show-and-tell-video-slate',
    'shortform-production',
    'shortform-idea-grill',
    'shortform-format-library',
    'short-form-pipeline',
    'net-new-video-editor',
    'video-caption-generator',
    'video-clip-pipeline',
    'trial-reel-distribution',
]

FINANCE_TEAM_FACTORY_SLUGS = [
    'finance-ops',
    'team-ops',
    'commenter-talent-scan',
    'software-factory',
    'reimagine-work',
    'sidebar-prioritizer',
]

STARTER_SLUGS = ['content-os-portable-starter']


class TestRepoContract(unittest.TestCase):
    """Test repository structure and content contracts."""

    def setUp(self):
        """Find all skill directories."""
        self.skill_dirs = []
        for item in REPO_ROOT.iterdir():
            if item.is_dir() and item.name not in TOOLING_DIRS:
                self.skill_dirs.append(item.name)
        self.skill_dirs.sort()

    def test_01_skill_set(self):
        """Test 1: Each skill dir has exactly one SKILL.md at allowed location, or is in allow list."""
        for skill_dir in self.skill_dirs:
            skill_path = REPO_ROOT / skill_dir
            
            # Check for SKILL.md
            direct_skill = skill_path / 'SKILL.md'
            nested_skill = skill_path / 'skills' / skill_dir / 'SKILL.md'
            
            has_direct = direct_skill.exists()
            has_nested = nested_skill.exists()
            
            if skill_dir in NO_SKILL_ALLOWLIST:
                self.assertFalse(has_direct, f"{skill_dir} is in allowlist but has direct SKILL.md")
                self.assertFalse(has_nested, f"{skill_dir} is in allowlist but has nested SKILL.md")
            else:
                # Exactly one SKILL.md at allowed location
                self.assertTrue(
                    has_direct or has_nested,
                    f"{skill_dir} has no SKILL.md at allowed location"
                )
                self.assertFalse(
                    has_direct and has_nested,
                    f"{skill_dir} has both direct and nested SKILL.md"
                )
        
        # No root SKILL.md
        root_skill = REPO_ROOT / 'SKILL.md'
        self.assertFalse(root_skill.exists(), "Root SKILL.md must not exist")

    def test_02_frontmatter_structure(self):
        """Test 2: Frontmatter has --- on line 1 and closing ---, with non-empty name and description."""
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            skill_path = REPO_ROOT / skill_dir
            skill_file = skill_path / 'SKILL.md'
            if not skill_file.exists():
                skill_file = skill_path / 'skills' / skill_dir / 'SKILL.md'
            
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            self.assertTrue(
                len(lines) > 0 and lines[0] == '---',
                f"{skill_dir}/SKILL.md: Line 1 must be '---'"
            )
            
            # Find closing ---
            closing_idx = -1
            for i in range(1, len(lines)):
                if lines[i] == '---':
                    closing_idx = i
                    break
            
            self.assertGreater(
                closing_idx, 0,
                f"{skill_dir}/SKILL.md: No closing '---' found in frontmatter"
            )
            
            frontmatter = '\n'.join(lines[1:closing_idx])
            
            # Check for name and description
            name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
            desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
            
            self.assertIsNotNone(
                name_match,
                f"{skill_dir}/SKILL.md: Missing 'name' in frontmatter"
            )
            self.assertIsNotNone(
                desc_match,
                f"{skill_dir}/SKILL.md: Missing 'description' in frontmatter"
            )
            
            if name_match:
                name = name_match.group(1).strip()
                self.assertTrue(
                    len(name) > 0,
                    f"{skill_dir}/SKILL.md: 'name' is empty"
                )
            
            if desc_match:
                desc = desc_match.group(1).strip()
                self.assertTrue(
                    len(desc) > 0,
                    f"{skill_dir}/SKILL.md: 'description' is empty"
                )

    def test_03_slug_format(self):
        """Test 3: Slug matches regex and length requirements."""
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            self.assertTrue(
                SLUG_REGEX.match(skill_dir),
                f"{skill_dir}: Slug must match ^[a-z0-9]+(-[a-z0-9]+)*$"
            )
            self.assertLessEqual(
                len(skill_dir), 64,
                f"{skill_dir}: Slug must be at most 64 characters"
            )

    def test_04_frontmatter_name_equals_slug(self):
        """Test 4: name equals the directory that directly holds SKILL.md."""
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            skill_path = REPO_ROOT / skill_dir
            skill_file = skill_path / 'SKILL.md'
            is_nested = False
            
            if not skill_file.exists():
                skill_file = skill_path / 'skills' / skill_dir / 'SKILL.md'
                is_nested = True
            
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            closing_idx = -1
            for i in range(1, len(lines)):
                if lines[i] == '---':
                    closing_idx = i
                    break
            
            if closing_idx > 0:
                frontmatter = '\n'.join(lines[1:closing_idx])
                name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
                
                if name_match:
                    name = name_match.group(1).strip()
                    self.assertEqual(
                        name, skill_dir,
                        f"{skill_dir}/SKILL.md: 'name' must equal '{skill_dir}', got '{name}'"
                    )

    def test_05_frontmatter_description_format(self):
        """Test 5: description is one line, not a > or | block, and under 160 characters."""
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            skill_path = REPO_ROOT / skill_dir
            skill_file = skill_path / 'SKILL.md'
            
            if not skill_file.exists():
                skill_file = skill_path / 'skills' / skill_dir / 'SKILL.md'
            
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            closing_idx = -1
            for i in range(1, len(lines)):
                if lines[i] == '---':
                    closing_idx = i
                    break
            
            if closing_idx > 0:
                frontmatter_lines = lines[1:closing_idx]
                
                # Find description line
                for i, line in enumerate(frontmatter_lines):
                    if line.startswith('description:'):
                        # Check if it's a block scalar
                        desc_value = line[len('description:'):].strip()
                        
                        self.assertFalse(
                            desc_value in ['>', '|', '>-', '|-', '>+', '|+'],
                            f"{skill_dir}/SKILL.md: 'description' must be inline, not a block scalar"
                        )
                        
                        # For inline description, value should be on same line
                        if desc_value:
                            self.assertLessEqual(
                                len(desc_value), 160,
                                f"{skill_dir}/SKILL.md: 'description' must be under 160 characters, got {len(desc_value)}"
                            )

    def test_06_gateway_sg_template_in_skill(self):
        """Test 6: Each SKILL.md contains Gateway URLs with correct sg_template."""
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            skill_path = REPO_ROOT / skill_dir
            skill_file = skill_path / 'SKILL.md'
            
            if not skill_file.exists():
                skill_file = skill_path / 'skills' / skill_dir / 'SKILL.md'
            
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for both Gateway URLs
            mcp_url_pattern = rf'https://gateway\.singlebrain\.com/mcp\?sg_template={re.escape(skill_dir)}(&|$|\s)'
            llms_url_pattern = rf'https://gateway\.singlebrain\.com/llms\.txt\?sg_template={re.escape(skill_dir)}'
            
            self.assertIsNotNone(
                re.search(mcp_url_pattern, content),
                f"{skill_dir}/SKILL.md: Missing correct mcp?sg_template={skill_dir} Gateway URL"
            )
            self.assertIsNotNone(
                re.search(llms_url_pattern, content),
                f"{skill_dir}/SKILL.md: Missing correct llms.txt?sg_template={skill_dir} Gateway URL"
            )

    def test_07_gateway_cta_in_readme(self):
        """Test 7: Each skill README contains Gateway CTA and no old singlebrain.com link."""
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            readme_path = REPO_ROOT / skill_dir / 'README.md'
            
            self.assertTrue(
                readme_path.exists(),
                f"{skill_dir}/README.md does not exist"
            )
            
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Gateway URL with correct sg_template
            mcp_url_pattern = rf'https://gateway\.singlebrain\.com/mcp\?sg_template={re.escape(skill_dir)}'
            
            self.assertIsNotNone(
                re.search(mcp_url_pattern, content),
                f"{skill_dir}/README.md: Missing mcp?sg_template={skill_dir} Gateway URL"
            )
            
            # Check for old singlebrain.com link (should not exist)
            old_link_pattern = r'https://singlebrain\.com/\?utm_source=github'
            
            self.assertIsNone(
                re.search(old_link_pattern, content),
                f"{skill_dir}/README.md: Contains old https://singlebrain.com/?utm_source=github link"
            )

    def test_08_gateway_cta_markers(self):
        """Test 8: Each SKILL.md and skill README has exactly one start and one end marker."""
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            # Check SKILL.md
            skill_path = REPO_ROOT / skill_dir
            skill_file = skill_path / 'SKILL.md'
            
            if not skill_file.exists():
                skill_file = skill_path / 'skills' / skill_dir / 'SKILL.md'
            
            with open(skill_file, 'r', encoding='utf-8') as f:
                skill_content = f.read()
            
            start_count = skill_content.count('<!-- gateway-cta:start -->')
            end_count = skill_content.count('<!-- gateway-cta:end -->')
            
            self.assertEqual(
                start_count, 1,
                f"{skill_dir}/SKILL.md: Must have exactly 1 gateway-cta:start marker, found {start_count}"
            )
            self.assertEqual(
                end_count, 1,
                f"{skill_dir}/SKILL.md: Must have exactly 1 gateway-cta:end marker, found {end_count}"
            )
            
            # Check marker order
            start_pos = skill_content.find('<!-- gateway-cta:start -->')
            end_pos = skill_content.find('<!-- gateway-cta:end -->')
            self.assertLess(
                start_pos, end_pos,
                f"{skill_dir}/SKILL.md: gateway-cta:start must come before gateway-cta:end"
            )
            
            # Check README.md
            readme_path = REPO_ROOT / skill_dir / 'README.md'
            
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            start_count = readme_content.count('<!-- gateway-cta:start -->')
            end_count = readme_content.count('<!-- gateway-cta:end -->')
            
            self.assertEqual(
                start_count, 1,
                f"{skill_dir}/README.md: Must have exactly 1 gateway-cta:start marker, found {start_count}"
            )
            self.assertEqual(
                end_count, 1,
                f"{skill_dir}/README.md: Must have exactly 1 gateway-cta:end marker, found {end_count}"
            )
            
            # Check marker order
            start_pos = readme_content.find('<!-- gateway-cta:start -->')
            end_pos = readme_content.find('<!-- gateway-cta:end -->')
            self.assertLess(
                start_pos, end_pos,
                f"{skill_dir}/README.md: gateway-cta:start must come before gateway-cta:end"
            )

    def test_09_live_services_format(self):
        """Test 9: Live services value is fallback sentence or all items are in allowed list."""
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            # Check SKILL.md
            skill_path = REPO_ROOT / skill_dir
            skill_file = skill_path / 'SKILL.md'
            
            if not skill_file.exists():
                skill_file = skill_path / 'skills' / skill_dir / 'SKILL.md'
            
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find Live services line
            services_match = re.search(r'- Live services:\s*(.+)', content)
            
            if services_match:
                services_value = services_match.group(1).strip()
                
                if services_value != FALLBACK_SERVICES:
                    # Split by comma and check each item
                    items = [item.strip() for item in services_value.split(',')]
                    
                    for item in items:
                        self.assertIn(
                            item, ALLOWED_SERVICES,
                            f"{skill_dir}/SKILL.md: '{item}' is not in allowed services list"
                        )

    def test_10_readme_hero_sentence_and_install(self):
        """Test 10: Root README has hero sentence before first ## line, npx command, and Node version."""
        readme_path = REPO_ROOT / 'README.md'
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Find first ## line
        first_h2_idx = -1
        for i, line in enumerate(lines):
            if line.startswith('## '):
                first_h2_idx = i
                break
        
        self.assertGreater(
            first_h2_idx, 0,
            "README.md: No ## heading found"
        )
        
        # Check hero sentence before first ##
        before_h2 = '\n'.join(lines[:first_h2_idx])
        hero_sentence = 'Get found in AI search (AEO/SEO) and turn it into pipeline.'
        
        self.assertIn(
            hero_sentence, before_h2,
            "README.md: Hero sentence must appear before first ## heading"
        )
        
        # Find first fenced code block
        code_block_pattern = r'```[^\n]*\n([^`]+)```'
        code_match = re.search(code_block_pattern, content)
        
        self.assertIsNotNone(
            code_match,
            "README.md: No fenced code block found"
        )
        
        if code_match:
            first_code_block = code_match.group(1)
            npx_command = 'npx skills add ericosiu/ai-marketing-skills'
            
            self.assertIn(
                npx_command, first_code_block,
                f"README.md: First code block must contain '{npx_command}'"
            )
        
        # Check for Node version
        self.assertIn(
            '22.20', content,
            "README.md: Must contain Node version '22.20'"
        )

    def test_11_readme_paths_and_no_old_content(self):
        """Test 11: Root README has required paths and no old content."""
        readme_path = REPO_ROOT / 'README.md'
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Required paths
        required_paths = [
            '.claude/skills/',
            '.agents/skills/',
            '.cursor/skills/',
            '~/.openclaw/skills/',
            'openclaw skills install ./',
        ]
        
        for path in required_paths:
            self.assertIn(
                path, content,
                f"README.md: Must contain '{path}'"
            )
        
        # Forbidden content
        forbidden_growth_engine_path = '.claude/skills/growth-engine.md'
        self.assertNotIn(
            forbidden_growth_engine_path, content,
            f"README.md: Must not contain '{forbidden_growth_engine_path}'"
        )
        
        # Check no setup steps for requirements.txt or .env.example
        # These can be mentioned elsewhere but not in setup/install instructions
        setup_patterns = [
            (r'(cp|copy|install|pip\s+install).*requirements\.txt', 'requirements.txt'),
            (r'(cp|copy).*\.env\.example', '.env.example'),
        ]
        
        for pattern, name in setup_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            self.assertIsNone(
                match,
                f"README.md: Must not have setup steps for {name}"
            )

    def test_12_openclaw_warning_and_git_ericosiu_count(self):
        """Test 12: Root README has OpenClaw warning and git:ericosiu appears exactly once."""
        readme_path = REPO_ROOT / 'README.md'
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # OpenClaw warning (exact text)
        openclaw_warning = 'Do not run `openclaw skills install git:ericosiu/ai-marketing-skills`.'
        
        self.assertIn(
            openclaw_warning, readme_content,
            "README.md: Must contain exact OpenClaw warning"
        )
        
        # git:ericosiu count in README
        git_ericosiu_count = readme_content.count('git:ericosiu')
        self.assertEqual(
            git_ericosiu_count, 1,
            f"README.md: 'git:ericosiu' must appear exactly once, found {git_ericosiu_count}"
        )
        
        # Check other files (AGENTS.md, CLAUDE.md, script, all SKILL.md files)
        files_to_check = [
            REPO_ROOT / 'AGENTS.md',
            REPO_ROOT / 'CLAUDE.md',
            REPO_ROOT / 'scripts' / 'install-openclaw.sh',
        ]
        
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            skill_path = REPO_ROOT / skill_dir
            skill_file = skill_path / 'SKILL.md'
            
            if not skill_file.exists():
                skill_file = skill_path / 'skills' / skill_dir / 'SKILL.md'
            
            files_to_check.append(skill_file)
        
        for file_path in files_to_check:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                count = content.count('git:ericosiu')
                self.assertEqual(
                    count, 0,
                    f"{file_path.relative_to(REPO_ROOT)}: 'git:ericosiu' must not appear, found {count}"
                )

    def test_13_readme_skill_table_rows(self):
        """Test 13: Each skill has a README row with slug and tagged Connect URL."""
        readme_path = REPO_ROOT / 'README.md'
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for skill_dir in self.skill_dirs:
            # All skill directories (including content-os-portable-starter) should have a row
            row_pattern = rf'\|\s*\[{re.escape(skill_dir)}\]\('
            
            self.assertIsNotNone(
                re.search(row_pattern, content),
                f"README.md: Missing table row for '{skill_dir}'"
            )
            
            # Check for tagged Connect URL (not for content-os-portable-starter)
            if skill_dir not in NO_SKILL_ALLOWLIST:
                connect_url_pattern = rf'https://gateway\.singlebrain\.com/mcp\?sg_template={re.escape(skill_dir)}'
                
                self.assertIsNotNone(
                    re.search(connect_url_pattern, content),
                    f"README.md: Missing tagged Connect URL for '{skill_dir}'"
                )

    def test_14_readme_skill_ordering(self):
        """Test 14: Hero slugs come before video/audio, finance/team/factory, and starter slugs."""
        readme_path = REPO_ROOT / 'README.md'
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find positions of each slug in table rows
        positions = {}
        
        for skill_dir in self.skill_dirs:
            row_pattern = rf'\|\s*\[{re.escape(skill_dir)}\]\('
            match = re.search(row_pattern, content)
            
            if match:
                positions[skill_dir] = match.start()
        
        # Check hero slugs come before other groups
        for hero_slug in HERO_SLUGS:
            if hero_slug not in positions:
                continue
            
            hero_pos = positions[hero_slug]
            
            # Check against video/audio slugs
            for other_slug in VIDEO_AUDIO_SLUGS + FINANCE_TEAM_FACTORY_SLUGS + STARTER_SLUGS:
                if other_slug not in positions:
                    continue
                
                other_pos = positions[other_slug]
                
                self.assertLess(
                    hero_pos, other_pos,
                    f"README.md: Hero slug '{hero_slug}' must come before '{other_slug}'"
                )

    def test_15_installer_files(self):
        """Test 15: Check installer files exist and have required content."""
        # Check AGENTS.md
        agents_md = REPO_ROOT / 'AGENTS.md'
        self.assertTrue(agents_md.exists(), "AGENTS.md must exist")
        
        with open(agents_md, 'r', encoding='utf-8') as f:
            agents_content = f.read()
        
        agents_required = [
            'npx skills add ericosiu/ai-marketing-skills',
            '.claude/skills/',
            '.agents/skills/',
        ]
        
        for required in agents_required:
            self.assertIn(
                required, agents_content,
                f"AGENTS.md: Must contain '{required}'"
            )
        
        # Check CLAUDE.md
        claude_md = REPO_ROOT / 'CLAUDE.md'
        self.assertTrue(claude_md.exists(), "CLAUDE.md must exist")
        
        with open(claude_md, 'r', encoding='utf-8') as f:
            claude_content = f.read()
        
        self.assertIn(
            '@AGENTS.md', claude_content,
            "CLAUDE.md: Must contain '@AGENTS.md'"
        )
        
        # Check .cursor/rules/ai-marketing-skills.mdc
        mdc_file = REPO_ROOT / '.cursor' / 'rules' / 'ai-marketing-skills.mdc'
        self.assertTrue(mdc_file.exists(), ".cursor/rules/ai-marketing-skills.mdc must exist")
        
        with open(mdc_file, 'r', encoding='utf-8') as f:
            mdc_content = f.read()
        
        # Check YAML frontmatter
        self.assertTrue(
            mdc_content.startswith('---'),
            ".cursor/rules/ai-marketing-skills.mdc: Must start with '---'"
        )
        self.assertIn(
            'description:', mdc_content,
            ".cursor/rules/ai-marketing-skills.mdc: Must contain 'description:'"
        )
        self.assertIn(
            'alwaysApply:', mdc_content,
            ".cursor/rules/ai-marketing-skills.mdc: Must contain 'alwaysApply:'"
        )
        
        # Check no .md file in .cursor/rules/
        md_files = list((REPO_ROOT / '.cursor' / 'rules').glob('*.md'))
        self.assertEqual(
            len(md_files), 0,
            f".cursor/rules/ must not contain .md files, found: {[f.name for f in md_files]}"
        )
        
        # Check install-openclaw.sh
        script_file = REPO_ROOT / 'scripts' / 'install-openclaw.sh'
        self.assertTrue(script_file.exists(), "scripts/install-openclaw.sh must exist")
        
        with open(script_file, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        self.assertIn(
            'openclaw skills install', script_content,
            "scripts/install-openclaw.sh: Must contain 'openclaw skills install'"
        )
        
        # Check marketplace.json if it exists
        marketplace_json = REPO_ROOT / '.cursor-plugin' / 'marketplace.json'
        if marketplace_json.exists():
            with open(marketplace_json, 'r', encoding='utf-8') as f:
                try:
                    json.loads(f.read())
                except json.JSONDecodeError as e:
                    self.fail(f".cursor-plugin/marketplace.json: Invalid JSON - {e}")

    def test_16_contributing_no_singlegrain_repo(self):
        """Test 16: CONTRIBUTING.md does not contain github.com/singlegrain/ai-marketing-skills."""
        contributing_path = REPO_ROOT / 'CONTRIBUTING.md'
        
        with open(contributing_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertNotIn(
            'github.com/singlegrain/ai-marketing-skills', content,
            "CONTRIBUTING.md: Must not contain 'github.com/singlegrain/ai-marketing-skills'"
        )

    def test_17_no_old_utm_medium_repo(self):
        """Test 17: No file contains utm_medium=repo."""
        # Check all markdown files except CONTRIBUTING.md
        for md_file in REPO_ROOT.glob('**/*.md'):
            if md_file.name == 'CONTRIBUTING.md':
                continue
            
            # Skip .git directory
            if '.git' in md_file.parts:
                continue
            
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertNotIn(
                'utm_medium=repo', content,
                f"{md_file.relative_to(REPO_ROOT)}: Must not contain 'utm_medium=repo'"
            )

    def test_18_managed_service_cta_in_skills(self):
        """Test 18: Every SKILL.md and skill README with Gateway CTA has managed-service CTA."""
        for skill_dir in self.skill_dirs:
            if skill_dir in NO_SKILL_ALLOWLIST:
                continue
            
            # Check SKILL.md
            skill_path = REPO_ROOT / skill_dir
            skill_file = skill_path / 'SKILL.md'
            
            if not skill_file.exists():
                skill_file = skill_path / 'skills' / skill_dir / 'SKILL.md'
            
            with open(skill_file, 'r', encoding='utf-8') as f:
                skill_content = f.read()
            
            # If it has Gateway CTA, it must have managed CTA
            if '<!-- gateway-cta:start -->' in skill_content:
                # Check for managed line
                managed_pattern = r'Single Grain or Single Brain can manage it.*utm_campaign=managed.*utm_content=' + re.escape(skill_dir)
                
                self.assertIsNotNone(
                    re.search(managed_pattern, skill_content),
                    f"{skill_dir}/SKILL.md: Gateway CTA found but missing managed-service CTA with correct utm_content={skill_dir}"
                )
            
            # Check README.md
            readme_path = REPO_ROOT / skill_dir / 'README.md'
            
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                
                # If it has Gateway CTA, it must have managed CTA
                if '<!-- gateway-cta:start -->' in readme_content:
                    # Check for managed line
                    managed_pattern = r'Single Grain or Single Brain can manage it.*utm_campaign=managed.*utm_content=' + re.escape(skill_dir)
                    
                    self.assertIsNotNone(
                        re.search(managed_pattern, readme_content),
                        f"{skill_dir}/README.md: Gateway CTA found but missing managed-service CTA with correct utm_content={skill_dir}"
                    )

    def test_19_managed_service_cta_in_root_readme(self):
        """Test 19: Root README has managed-service CTA with utm_content=readme."""
        readme_path = REPO_ROOT / 'README.md'
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for managed line with utm_content=readme
        managed_pattern = r'Single Grain or Single Brain can manage it.*utm_campaign=managed.*utm_content=readme'
        
        self.assertIsNotNone(
            re.search(managed_pattern, content),
            "README.md: Missing managed-service CTA with utm_content=readme"
        )

    def test_20_contributing_has_gateway_managed_rule(self):
        """Test 20: CONTRIBUTING.md has Gateway and managed service requirement."""
        contributing_path = REPO_ROOT / 'CONTRIBUTING.md'
        
        with open(contributing_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Gateway and managed section
        self.assertIn(
            'Gateway and Managed Service CTAs', content,
            "CONTRIBUTING.md: Missing 'Gateway and Managed Service CTAs' section"
        )
        
        # Check for key requirements
        requirements = [
            'sg_template=<slug>',
            'utm_campaign=managed',
            'utm_content=<slug>',
            'Single Brain Gateway',
        ]
        
        for requirement in requirements:
            self.assertIn(
                requirement, content,
                f"CONTRIBUTING.md: Missing '{requirement}' in Gateway/managed section"
            )

    def test_21_single_brain_two_words(self):
        """Test 21: 'Single Brain' is two words, not 'SingleBrain', excluding URLs."""
        # Check all markdown files
        for md_file in REPO_ROOT.glob('**/*.md'):
            # Skip .git directory
            if '.git' in md_file.parts:
                continue
            
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find 'SingleBrain' outside of URLs/domains
            # Remove URLs first to avoid false positives
            content_without_urls = re.sub(r'https?://[^\s)]+', '', content)
            content_without_urls = re.sub(r'[a-z0-9-]+\.singlebrain\.com', '', content_without_urls)
            
            # Check for 'SingleBrain' (one word) in the cleaned content
            self.assertNotIn(
                'SingleBrain', content_without_urls,
                f"{md_file.relative_to(REPO_ROOT)}: Use 'Single Brain' (two words), not 'SingleBrain' (excluding URLs/domains)"
            )

    def test_22_test_file_imports_and_workflow(self):
        """Test 22: Test file uses only allowed imports and workflow has no installers."""
        # Check this file's imports
        test_file = Path(__file__)
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        allowed_imports = {'os', 're', 'sys', 'json', 'pathlib', 'unittest'}
        
        # Find all import statements
        import_pattern = r'^\s*(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module = match.group(1)
            self.assertIn(
                module, allowed_imports,
                f"test_repo_contract.py: Import '{module}' is not in allowed list"
            )
        
        # Check workflow file
        workflow_file = REPO_ROOT / '.github' / 'workflows' / 'skill-safety.yml'
        self.assertTrue(workflow_file.exists(), ".github/workflows/skill-safety.yml must exist")
        
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_content = f.read()
        
        # Check for skill-contract job/step
        self.assertIn(
            'skill-contract', workflow_content,
            ".github/workflows/skill-safety.yml: Must contain 'skill-contract'"
        )
        
        # Check for test execution
        self.assertIn(
            'test_repo_contract.py', workflow_content,
            ".github/workflows/skill-safety.yml: Must execute test_repo_contract.py"
        )
        
        # Check no installers
        forbidden_tools = ['pip', 'npm', 'npx', 'curl', 'wget']
        
        # Find skill-contract section
        if 'skill-contract' in workflow_content:
            # Extract the job section (rough approximation)
            job_start = workflow_content.find('skill-contract')
            next_job = workflow_content.find('\n  ', job_start + 1)
            if next_job == -1:
                next_job = len(workflow_content)
            
            job_section = workflow_content[job_start:next_job]
            
            for tool in forbidden_tools:
                # Don't check if the line is a comment
                for line in job_section.split('\n'):
                    if line.strip().startswith('#'):
                        continue
                    if tool in line:
                        self.fail(
                            f".github/workflows/skill-safety.yml: skill-contract section must not use '{tool}'"
                        )


def main():
    """Run tests and exit with appropriate code."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRepoContract)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == '__main__':
    main()
