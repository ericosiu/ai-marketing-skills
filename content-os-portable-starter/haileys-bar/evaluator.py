#!/usr/bin/env python3
"""
Hailey's Bar v1.1 — Content Draft Evaluation
Three-layer quality gate for Content OS drafts.

Layer 1: Programmatic checks (Tier A: quality, Tier B: mechanical)
Layer 1B: Batch diversity checks (for bulk generation)
Layer 2: LLM judge rubric (6 criteria, weighted)
Layer 3: Human calibration (golden set)

A draft clears to scale when:
- Tier A passes in full
- Batch diversity check passes (when in batch)
- Tier B is fixed
- Judge score >= 8
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import Counter


@dataclass
class AIPhrasingMatch:
    """Detected AI-phrasing pattern instance"""
    sentence: str
    pattern_description: str
    line_number: int


@dataclass
class TierAResult:
    """Layer 1 Tier A check results"""
    passed: bool
    failures: List[str] = field(default_factory=list)
    
    # A1: Internal links
    internal_link_count: int = 0
    internal_links: List[str] = field(default_factory=list)
    
    # A2: External links
    external_link_count: int = 0
    external_links: List[str] = field(default_factory=list)
    
    # A3: Link resolution
    unresolved_links: List[str] = field(default_factory=list)
    
    # A4: SEO-proof intro
    keyword_in_first_para: bool = False
    has_preview: bool = False
    has_hook: bool = False
    
    # A5: Definitional H2
    has_definitional_h2: bool = False
    definitional_h2: Optional[str] = None
    
    # A6: Readability
    readability_grade: Optional[float] = None
    readability_passed: bool = False


@dataclass
class TierBResult:
    """Layer 1 Tier B check results (mechanical, auto-fixable)"""
    passed: bool
    issues: List[str] = field(default_factory=list)
    
    # B1: Section lead-ins
    sections_without_leadins: List[str] = field(default_factory=list)
    
    # B2: Bullet capitalization
    uncapitalized_bullets: List[str] = field(default_factory=list)
    
    # B3: Semicolons in bullets
    bullets_with_semicolons: List[str] = field(default_factory=list)
    
    # B4: Title case headings
    non_titlecase_headings: List[str] = field(default_factory=list)


@dataclass
class BatchDiversityResult:
    """Layer 1B batch diversity check results"""
    passed: bool
    issues: List[str] = field(default_factory=list)
    
    # Structural sameness
    outline_overlap_ratios: Dict[str, float] = field(default_factory=dict)
    
    # Verbatim reuse
    shingle_overlap_ratios: Dict[str, float] = field(default_factory=dict)
    
    # Opening-move sameness
    intro_similarity_ratios: Dict[str, float] = field(default_factory=dict)
    
    # Repeated structures/phrases
    repeated_structures: List[str] = field(default_factory=list)
    repeated_phrases: List[str] = field(default_factory=list)


@dataclass
class JudgeScore:
    """Layer 2 LLM judge rubric scores"""
    c1_link_quality: float = 0.0
    c2_human_voice: float = 0.0
    c3_defines_concepts: float = 0.0
    c4_section_transitions: float = 0.0
    c5_keyword_clarity: float = 0.0
    c6_heading_architecture: float = 0.0
    
    weighted_score: float = 0.0
    passed: bool = False


@dataclass
class EvaluationResult:
    """Complete evaluation result"""
    draft_id: str
    primary_keyword: str
    
    # Layer 1 results
    tier_a: TierAResult
    tier_b: TierBResult
    ai_phrasing_matches: List[AIPhrasingMatch] = field(default_factory=list)
    
    # Layer 1B results (optional, for batch mode)
    batch_diversity: Optional[BatchDiversityResult] = None
    
    # Layer 2 results (optional, requires LLM)
    judge_score: Optional[JudgeScore] = None
    
    # Final decision
    scale_clear: bool = False
    final_score: float = 0.0
    reasons: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict"""
        return asdict(self)


class HaileysBarEvaluator:
    """Main evaluator for Hailey's Bar v1.1"""
    
    def __init__(self, config_path: Optional[Path] = None, link_resolver=None):
        """
        Initialize evaluator with config.
        
        Args:
            config_path: Path to config.yaml (default: config.yaml in same dir)
            link_resolver: Optional callable to check link resolution (for testing)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.link_resolver = link_resolver
    
    def evaluate(
        self,
        markdown_text: str,
        primary_keyword: str,
        draft_id: str = "draft",
        batch_drafts: Optional[List[Tuple[str, str]]] = None,
        judge_criterion_scores: Optional[Dict[str, float]] = None
    ) -> EvaluationResult:
        """
        Evaluate a draft against Hailey's Bar.
        
        Args:
            markdown_text: The draft content in markdown
            primary_keyword: Primary SEO keyword for this draft
            draft_id: Identifier for this draft
            batch_drafts: Optional list of (id, text) tuples for batch diversity check
            judge_criterion_scores: Optional dict of criterion scores (C1-C6) for Layer 2
        
        Returns:
            EvaluationResult with all checks and final decision
        """
        result = EvaluationResult(
            draft_id=draft_id,
            primary_keyword=primary_keyword,
            tier_a=TierAResult(passed=False),
            tier_b=TierBResult(passed=False)
        )
        
        # Layer 1 Tier A
        result.tier_a = self._check_tier_a(markdown_text, primary_keyword)
        
        # Layer 1 Tier B
        result.tier_b = self._check_tier_b(markdown_text)
        
        # AI-phrasing scanner
        result.ai_phrasing_matches = self._scan_ai_phrasing(markdown_text)
        
        # Layer 1B: Batch diversity (if batch provided)
        if batch_drafts:
            result.batch_diversity = self._check_batch_diversity(
                draft_id, markdown_text, batch_drafts
            )
        
        # Layer 2: Judge rubric (if scores provided)
        if judge_criterion_scores:
            result.judge_score = self._calculate_judge_score(
                judge_criterion_scores,
                len(result.ai_phrasing_matches)
            )
        
        # Final scale gate decision
        result.scale_clear, result.final_score, result.reasons = self._evaluate_scale_gate(
            result
        )
        
        return result
    
    def _check_tier_a(self, markdown_text: str, primary_keyword: str) -> TierAResult:
        """Run all Tier A checks"""
        result = TierAResult(passed=False)
        config = self.config["layer_1"]["tier_a"]
        
        # A1 & A2: Count internal and external links
        result.internal_links, result.external_links = self._extract_links(markdown_text)
        result.internal_link_count = len(result.internal_links)
        result.external_link_count = len(result.external_links)
        
        if result.internal_link_count < config["internal_links_min"]:
            result.failures.append(
                f"A1: Only {result.internal_link_count} internal links "
                f"(need {config['internal_links_min']})"
            )
        
        if result.external_link_count < config["external_links_min"]:
            result.failures.append(
                f"A2: Only {result.external_link_count} external links "
                f"(need {config['external_links_min']})"
            )
        
        # A3: Link resolution (only if resolver provided)
        if self.link_resolver and config["check_link_resolution"]:
            all_links = result.internal_links + result.external_links
            for link in all_links:
                if not self.link_resolver(link):
                    result.unresolved_links.append(link)
            
            if result.unresolved_links:
                result.failures.append(
                    f"A3: {len(result.unresolved_links)} unresolved links"
                )
        
        # A4: SEO-proof intro
        intro_checks = self._check_seo_proof_intro(markdown_text, primary_keyword)
        result.keyword_in_first_para = intro_checks["keyword_in_first_para"]
        result.has_preview = intro_checks["has_preview"]
        result.has_hook = intro_checks["has_hook"]
        
        if not result.keyword_in_first_para:
            result.failures.append(
                f"A4a: Primary keyword '{primary_keyword}' not in first paragraph"
            )
        if not result.has_preview:
            result.failures.append("A4b: Intro missing preview of guide content")
        if not result.has_hook:
            result.failures.append("A4c: Intro missing hook/why-it-matters")
        
        # A5: Definitional H2
        def_h2 = self._find_definitional_h2(markdown_text, primary_keyword)
        result.has_definitional_h2 = def_h2 is not None
        result.definitional_h2 = def_h2
        
        if not result.has_definitional_h2:
            result.failures.append(
                f"A5: Missing 'What Is {primary_keyword}' definitional H2"
            )
        
        # A6: Readability
        grade = self._calculate_readability_grade(markdown_text)
        result.readability_grade = grade
        min_grade = config["readability"]["min_grade"]
        max_grade = config["readability"]["max_grade"]
        result.readability_passed = min_grade <= grade <= max_grade
        
        if not result.readability_passed:
            result.failures.append(
                f"A6: Readability grade {grade:.1f} outside target range "
                f"({min_grade}-{max_grade})"
            )
        
        result.passed = len(result.failures) == 0
        return result
    
    def _check_tier_b(self, markdown_text: str) -> TierBResult:
        """Run all Tier B checks (mechanical, auto-fixable)"""
        result = TierBResult(passed=False)
        
        # B1: Section lead-ins
        result.sections_without_leadins = self._check_section_leadins(markdown_text)
        if result.sections_without_leadins:
            result.issues.append(
                f"B1: {len(result.sections_without_leadins)} sections without lead-in sentences"
            )
        
        # B2: Bullet capitalization
        result.uncapitalized_bullets = self._check_bullet_capitalization(markdown_text)
        if result.uncapitalized_bullets:
            result.issues.append(
                f"B2: {len(result.uncapitalized_bullets)} bullets not capitalized"
            )
        
        # B3: Semicolons in bullets
        result.bullets_with_semicolons = self._check_bullet_semicolons(markdown_text)
        if result.bullets_with_semicolons:
            result.issues.append(
                f"B3: {len(result.bullets_with_semicolons)} bullets end with semicolons"
            )
        
        # B4: Title case headings
        result.non_titlecase_headings = self._check_titlecase_headings(markdown_text)
        if result.non_titlecase_headings:
            result.issues.append(
                f"B4: {len(result.non_titlecase_headings)} headings not in Title Case"
            )
        
        result.passed = len(result.issues) == 0
        return result
    
    def _scan_ai_phrasing(self, markdown_text: str) -> List[AIPhrasingMatch]:
        """Scan for AI-phrasing patterns (negation-antithesis constructions)"""
        matches = []
        patterns = self.config["ai_phrasing"]["patterns"]
        
        # Remove markdown formatting but keep line structure for line numbers
        lines = markdown_text.split('\n')
        
        # Process full text for pattern matching
        full_text = re.sub(r'[#*`]', '', markdown_text)
        full_text = re.sub(r'\n+', ' ', full_text)
        
        for pattern_def in patterns:
            pattern = pattern_def["pattern"]
            description = pattern_def["description"]
            
            for match in re.finditer(pattern, full_text):
                matched_text = match.group(0)
                
                # Find approximate line number by searching original text
                # This is a heuristic for reporting purposes
                line_num = 1
                search_text = matched_text[:50]  # First 50 chars
                for i, line in enumerate(lines, 1):
                    if search_text[:20] in line:
                        line_num = i
                        break
                
                matches.append(AIPhrasingMatch(
                    sentence=matched_text,
                    pattern_description=description,
                    line_number=line_num
                ))
        
        return matches
    
    def _check_batch_diversity(
        self,
        draft_id: str,
        markdown_text: str,
        batch_drafts: List[Tuple[str, str]]
    ) -> BatchDiversityResult:
        """Check batch diversity (Layer 1B)"""
        result = BatchDiversityResult(passed=True)
        config = self.config["batch_diversity"]
        
        if not config["enabled"]:
            return result
        
        # Extract structural elements for current draft
        current_outline = self._extract_outline(markdown_text)
        current_shingles = self._extract_shingles(
            markdown_text,
            config["shingle_size"],
            config["allowlist"]
        )
        current_intro = self._extract_intro_structure(markdown_text)
        
        # Compare against each draft in batch
        for other_id, other_text in batch_drafts:
            if other_id == draft_id:
                continue
            
            # Structural overlap
            other_outline = self._extract_outline(other_text)
            overlap_ratio = self._calculate_outline_overlap(current_outline, other_outline)
            result.outline_overlap_ratios[other_id] = overlap_ratio
            
            if overlap_ratio > config["max_outline_overlap_ratio"]:
                result.passed = False
                result.issues.append(
                    f"Structural overlap with {other_id}: {overlap_ratio:.1%}"
                )
            
            # Verbatim shingle overlap
            other_shingles = self._extract_shingles(
                other_text,
                config["shingle_size"],
                config["allowlist"]
            )
            shingle_ratio = self._calculate_shingle_overlap(current_shingles, other_shingles)
            result.shingle_overlap_ratios[other_id] = shingle_ratio
            
            if shingle_ratio > config["max_shingle_overlap_ratio"]:
                result.passed = False
                result.issues.append(
                    f"Verbatim reuse with {other_id}: {shingle_ratio:.1%}"
                )
            
            # Intro similarity
            other_intro = self._extract_intro_structure(other_text)
            intro_ratio = self._calculate_intro_similarity(current_intro, other_intro)
            result.intro_similarity_ratios[other_id] = intro_ratio
            
            if intro_ratio > config["max_intro_similarity_ratio"]:
                result.passed = False
                result.issues.append(
                    f"Intro similarity with {other_id}: {intro_ratio:.1%}"
                )
        
        return result
    
    def _calculate_judge_score(
        self,
        criterion_scores: Dict[str, float],
        ai_phrasing_count: int
    ) -> JudgeScore:
        """Calculate weighted judge score from criterion scores"""
        rubric = self.config["layer_2"]["judge_rubric"]
        criteria = rubric["criteria"]
        min_score = self.config["layer_2"]["min_judge_score"]
        
        # Apply AI-phrasing penalty to C2 (human voice)
        c2_score = criterion_scores.get("C2", 0.0)
        if ai_phrasing_count > 0:
            # Each AI-phrasing instance reduces C2 score
            penalty_per_instance = 0.5
            c2_score = max(1.0, c2_score - (ai_phrasing_count * penalty_per_instance))
            criterion_scores = {**criterion_scores, "C2": c2_score}
        
        # Calculate weighted average
        weighted_sum = 0.0
        for criterion, config_data in criteria.items():
            score = criterion_scores.get(criterion, 0.0)
            weight = config_data["weight"]
            weighted_sum += score * weight
        
        result = JudgeScore(
            c1_link_quality=criterion_scores.get("C1", 0.0),
            c2_human_voice=criterion_scores.get("C2", 0.0),
            c3_defines_concepts=criterion_scores.get("C3", 0.0),
            c4_section_transitions=criterion_scores.get("C4", 0.0),
            c5_keyword_clarity=criterion_scores.get("C5", 0.0),
            c6_heading_architecture=criterion_scores.get("C6", 0.0),
            weighted_score=weighted_sum,
            passed=weighted_sum >= min_score
        )
        
        return result
    
    def _evaluate_scale_gate(
        self,
        result: EvaluationResult
    ) -> Tuple[bool, float, List[str]]:
        """Determine if draft clears to scale"""
        reasons = []
        
        # Check Tier A
        if not result.tier_a.passed:
            reasons.append("Tier A FAILED: " + "; ".join(result.tier_a.failures))
        
        # Check Tier B
        if not result.tier_b.passed:
            reasons.append("Tier B needs fixes: " + "; ".join(result.tier_b.issues))
        
        # Check batch diversity (if applicable)
        if result.batch_diversity and not result.batch_diversity.passed:
            reasons.append("Batch diversity FAILED: " + "; ".join(result.batch_diversity.issues))
        
        # Check judge score
        judge_score = 0.0
        if result.judge_score:
            judge_score = result.judge_score.weighted_score
            if not result.judge_score.passed:
                min_score = self.config["layer_2"]["min_judge_score"]
                reasons.append(
                    f"Judge score {judge_score:.1f} below minimum {min_score}"
                )
        
        # Tier A failure caps score at 5
        final_score = judge_score
        if not result.tier_a.passed:
            final_score = min(5.0, judge_score)
            if judge_score > 5.0:
                reasons.append("Score capped at 5 due to Tier A failures")
        
        # Scale clear only if all conditions met
        scale_clear = (
            result.tier_a.passed
            and result.tier_b.passed
            and (result.batch_diversity is None or result.batch_diversity.passed)
            and (result.judge_score is None or result.judge_score.passed)
        )
        
        if scale_clear:
            reasons = ["All gates passed - CLEAR TO SCALE"]
        
        return scale_clear, final_score, reasons
    
    # Helper methods for specific checks
    
    def _extract_links(self, markdown_text: str) -> Tuple[List[str], List[str]]:
        """Extract internal and external links from markdown"""
        # Match markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.findall(link_pattern, markdown_text)
        
        internal_links = []
        external_links = []
        
        for text, url in matches:
            # Consider relative links and same-domain as internal
            if url.startswith('/') or url.startswith('#') or 'singlegrain.com' in url.lower():
                internal_links.append(url)
            elif url.startswith('http'):
                external_links.append(url)
        
        return internal_links, external_links
    
    def _check_seo_proof_intro(
        self,
        markdown_text: str,
        primary_keyword: str
    ) -> Dict[str, bool]:
        """Check SEO-proof intro requirements (A4)"""
        # Extract intro (everything before first H2)
        intro_match = re.search(r'^(.*?)(?=^## )', markdown_text, re.MULTILINE | re.DOTALL)
        intro = intro_match.group(1) if intro_match else markdown_text
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in intro.split('\n\n') if p.strip() and not p.startswith('#')]
        
        # A4a: Keyword in first paragraph
        first_para = paragraphs[0] if paragraphs else ""
        keyword_in_first = primary_keyword.lower() in first_para.lower()
        
        # A4b: Preview of content (heuristic: look for forward-looking language in last para)
        preview_keywords = [
            'will cover', 'will explore', 'will discuss', 'will show',
            'learn how', 'discover', 'find out', 'this guide',
            'we\'ll', 'you\'ll learn', 'you\'ll discover'
        ]
        has_preview = any(
            any(kw in para.lower() for kw in preview_keywords)
            for para in paragraphs[-2:]  # Check last two paragraphs
        )
        
        # A4c: Hook (heuristic: look for why-it-matters language)
        hook_keywords = [
            'why', 'because', 'matters', 'important', 'critical',
            'essential', 'key to', 'crucial', 'need to',
            'without', 'challenge', 'problem', 'opportunity'
        ]
        has_hook = any(
            any(kw in para.lower() for kw in hook_keywords)
            for para in paragraphs[:3]  # Check first three paragraphs
        )
        
        return {
            "keyword_in_first_para": keyword_in_first,
            "has_preview": has_preview,
            "has_hook": has_hook
        }
    
    def _find_definitional_h2(
        self,
        markdown_text: str,
        primary_keyword: str
    ) -> Optional[str]:
        """Find definitional 'What Is X' H2 (A5)"""
        h2_pattern = r'^## (.+)$'
        h2_matches = re.findall(h2_pattern, markdown_text, re.MULTILINE)
        
        # Look for "What Is [keyword]" pattern
        for h2 in h2_matches:
            h2_lower = h2.lower()
            keyword_lower = primary_keyword.lower()
            
            if 'what is' in h2_lower and keyword_lower in h2_lower:
                return h2
        
        return None
    
    def _calculate_readability_grade(self, markdown_text: str) -> float:
        """
        Calculate readability grade (simplified Flesch-Kincaid).
        Target: 8-10 grade level.
        """
        # Remove markdown formatting
        text = re.sub(r'[#*`\[\]()]', '', markdown_text)
        text = re.sub(r'\n+', ' ', text)
        
        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        
        if sentence_count == 0:
            return 8.0  # Default to middle of target range
        
        # Count words
        words = [w for w in text.split() if w.strip()]
        word_count = len(words)
        
        if word_count == 0:
            return 8.0  # Default to middle of target range
        
        # Count syllables (simplified: count vowel groups)
        syllable_count = 0
        for word in words:
            word = re.sub(r'[^a-z]', '', word.lower())
            if not word:
                syllable_count += 1
                continue
            syllables = len(re.findall(r'[aeiou]+', word))
            syllables = max(1, syllables)  # At least 1 syllable per word
            syllable_count += syllables
        
        # Flesch-Kincaid Grade Level
        avg_words_per_sentence = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count
        
        grade = (
            0.39 * avg_words_per_sentence
            + 11.8 * avg_syllables_per_word
            - 15.59
        )
        
        return max(1.0, grade)  # Minimum grade 1
    
    def _check_section_leadins(self, markdown_text: str) -> List[str]:
        """Check for section lead-in sentences (B1)"""
        sections_without_leadins = []
        
        # Find all H2 sections
        h2_pattern = r'^## (.+)$'
        lines = markdown_text.split('\n')
        
        for i, line in enumerate(lines):
            if re.match(h2_pattern, line):
                h2_title = line.strip()
                
                # Check next non-empty line after H2
                next_content = None
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        next_content = lines[j].strip()
                        break
                
                # Fail if next content is a list or another heading
                if next_content:
                    if next_content.startswith(('-', '*', '1.', '#')):
                        sections_without_leadins.append(h2_title)
        
        return sections_without_leadins
    
    def _check_bullet_capitalization(self, markdown_text: str) -> List[str]:
        """Check bullet capitalization (B2)"""
        uncapitalized = []
        
        # Find all bullet points
        bullet_pattern = r'^[\s]*[-*]\s+(.+)$'
        for match in re.finditer(bullet_pattern, markdown_text, re.MULTILINE):
            bullet_text = match.group(1).strip()
            
            # Check if first character is lowercase letter
            if bullet_text and bullet_text[0].islower():
                uncapitalized.append(bullet_text[:50])  # First 50 chars
        
        return uncapitalized
    
    def _check_bullet_semicolons(self, markdown_text: str) -> List[str]:
        """Check for semicolons at end of bullets (B3)"""
        bullets_with_semicolons = []
        
        bullet_pattern = r'^[\s]*[-*]\s+(.+)$'
        for match in re.finditer(bullet_pattern, markdown_text, re.MULTILINE):
            bullet_text = match.group(1).strip()
            
            if bullet_text.endswith(';'):
                bullets_with_semicolons.append(bullet_text[:50])
        
        return bullets_with_semicolons
    
    def _check_titlecase_headings(self, markdown_text: str) -> List[str]:
        """Check if headings are in Title Case (B4)"""
        non_titlecase = []
        
        heading_pattern = r'^(#{2,3})\s+(.+)$'
        for match in re.finditer(heading_pattern, markdown_text, re.MULTILINE):
            heading_text = match.group(2).strip()
            
            # Simple Title Case check: most words should start with capital
            words = heading_text.split()
            
            # Articles, conjunctions, prepositions that can be lowercase
            lowercase_ok = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for',
                           'in', 'of', 'on', 'or', 'the', 'to', 'with'}
            
            capitalized_count = 0
            for i, word in enumerate(words):
                # First word should always be capitalized
                if i == 0:
                    if word[0].isupper():
                        capitalized_count += 1
                else:
                    # Other words: check if it's in lowercase_ok set
                    if word.lower() in lowercase_ok:
                        # These can be lowercase
                        capitalized_count += 1
                    elif word[0].isupper():
                        capitalized_count += 1
            
            # If less than 70% properly capitalized, flag it
            if len(words) > 0 and capitalized_count / len(words) < 0.7:
                non_titlecase.append(heading_text)
        
        return non_titlecase
    
    def _extract_outline(self, markdown_text: str) -> List[str]:
        """Extract H2/H3 outline structure"""
        outline = []
        heading_pattern = r'^(#{2,3})\s+(.+)$'
        
        for match in re.finditer(heading_pattern, markdown_text, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip().lower()
            outline.append(f"H{level}:{title}")
        
        return outline
    
    def _calculate_outline_overlap(
        self,
        outline1: List[str],
        outline2: List[str]
    ) -> float:
        """Calculate structural overlap between two outlines"""
        if not outline1 or not outline2:
            return 0.0
        
        # Convert to sets and calculate Jaccard similarity
        set1 = set(outline1)
        set2 = set(outline2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_shingles(
        self,
        markdown_text: str,
        shingle_size: int,
        allowlist: List[str]
    ) -> set:
        """Extract word shingles for verbatim reuse detection"""
        # Remove markdown formatting
        text = re.sub(r'[#*`\[\]()]', '', markdown_text)
        text = text.lower()
        
        words = text.split()
        shingles = set()
        
        for i in range(len(words) - shingle_size + 1):
            shingle = ' '.join(words[i:i + shingle_size])
            
            # Skip if contains allowlisted phrase
            if not any(allowed.lower() in shingle for allowed in allowlist):
                shingles.add(shingle)
        
        return shingles
    
    def _calculate_shingle_overlap(self, shingles1: set, shingles2: set) -> float:
        """Calculate shingle overlap ratio"""
        if not shingles1 or not shingles2:
            return 0.0
        
        intersection = len(shingles1 & shingles2)
        min_size = min(len(shingles1), len(shingles2))
        
        return intersection / min_size if min_size > 0 else 0.0
    
    def _extract_intro_structure(self, markdown_text: str) -> Dict[str, Any]:
        """Extract intro structural features"""
        # Get intro (before first H2)
        intro_match = re.search(r'^(.*?)(?=^## )', markdown_text, re.MULTILINE | re.DOTALL)
        intro = intro_match.group(1) if intro_match else markdown_text
        
        # Extract features
        sentences = re.split(r'[.!?]+', intro)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Check for negation-antithesis in opening
        has_negation_opening = any(
            re.search(r'\b(?:not|no|never)\b', sent.lower())
            for sent in sentences[:3]
        )
        
        # Count question marks
        question_count = intro.count('?')
        
        return {
            "sentence_count": len(sentences),
            "has_negation_opening": has_negation_opening,
            "question_count": question_count,
            "first_sentence_length": len(sentences[0].split()) if sentences else 0
        }
    
    def _calculate_intro_similarity(
        self,
        intro1: Dict[str, Any],
        intro2: Dict[str, Any]
    ) -> float:
        """Calculate intro structure similarity"""
        # Simple similarity based on structural features
        similarities = []
        
        # Sentence count similarity
        sc1 = intro1["sentence_count"]
        sc2 = intro2["sentence_count"]
        if sc1 > 0 and sc2 > 0:
            similarities.append(1 - abs(sc1 - sc2) / max(sc1, sc2))
        
        # Negation opening match
        if intro1["has_negation_opening"] == intro2["has_negation_opening"]:
            similarities.append(1.0 if intro1["has_negation_opening"] else 0.5)
        
        # Question count similarity
        qc1 = intro1["question_count"]
        qc2 = intro2["question_count"]
        if qc1 == qc2:
            similarities.append(1.0 if qc1 > 0 else 0.5)
        
        return sum(similarities) / len(similarities) if similarities else 0.0


def evaluate_draft(
    markdown_file: Path,
    primary_keyword: str,
    config_path: Optional[Path] = None,
    batch_files: Optional[List[Path]] = None,
    judge_scores: Optional[Dict[str, float]] = None
) -> EvaluationResult:
    """
    Convenience function to evaluate a draft from a file.
    
    Args:
        markdown_file: Path to markdown draft file
        primary_keyword: Primary SEO keyword
        config_path: Optional path to config.yaml
        batch_files: Optional list of other draft files for batch check
        judge_scores: Optional dict of C1-C6 criterion scores
    
    Returns:
        EvaluationResult
    """
    evaluator = HaileysBarEvaluator(config_path)
    
    with open(markdown_file) as f:
        markdown_text = f.read()
    
    batch_drafts = None
    if batch_files:
        batch_drafts = []
        for batch_file in batch_files:
            with open(batch_file) as f:
                batch_drafts.append((batch_file.stem, f.read()))
    
    return evaluator.evaluate(
        markdown_text=markdown_text,
        primary_keyword=primary_keyword,
        draft_id=markdown_file.stem,
        batch_drafts=batch_drafts,
        judge_criterion_scores=judge_scores
    )
