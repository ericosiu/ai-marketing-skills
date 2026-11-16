"""Tests for check_tells.py

Run: python3 -m pytest tests/test_check_tells.py -v
or: python3 -m unittest tests/test_check_tells.py
"""
import os, subprocess, sys
import pytest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from check_tells import find_tells, load_patterns
CLI = [sys.executable, os.path.join(ROOT, 'check_tells.py')]

# Zephyr's own examples, one per category (verbatim from the post), plus the baseline dash
SOURCE_EXAMPLES = [
    ('0', 'We shipped it \u2014 finally.'),
    ('1', 'Claude quietly shipped the best feature of the year.'),
    ('2', "It's not a chatbot, it's a coworker."),
    ('3', 'Set this up before Monday.'),
    ('3', 'Do it this weekend.'),
    ('4', 'Most people use Claude wrong.'),
    ('5', 'Claude can now research like a $150/hour analyst.'),
    ('6', 'Setup is the part everyone skips.'),
    ('6', "That's the whole game."),
    ('7', 'Write. Edit. Ship.'),
    ('8', 'A powerful, seamless, game-changing workflow.'),
    ('9', '\U0001F6A8 BREAKING: new model out \U0001F447'),
]

@pytest.mark.parametrize('cat,text', SOURCE_EXAMPLES)
def test_each_source_example_hits_its_category(cat, text):
    cats = {h['category'] for h in find_tells(text)}
    assert cat in cats, (text, cats)

@pytest.mark.parametrize('text', [
    "It answers my client emails.",
    "The setup takes about 40 minutes.",
    "I use Claude to draft proposals, and I read every one before it goes out.",
    "We ran 12 tests last week. Two broke, and I fixed the parser.",
    "Breaking the job into steps made it faster.",          # lowercase 'breaking' is fine
    "Version 1.2.3 shipped. See e.g. the changelog.",
    "Hi there,\n\nCould we join your list? Our page: https://example.com/\n\nWe make agents for single jobs.",
])
def test_clean_copy_passes(text):
    assert find_tells(text) == [], find_tells(text)

def test_curly_apostrophe_and_case():
    assert find_tells('IT\u2019S NOT a tool, it\u2019s a teammate.')
    assert find_tells('QUIETLY')

def test_line_numbers():
    hits = find_tells('line one is fine.\nThis quietly broke.\nok\nMost people miss it.')
    assert [(h['line'], h['category']) for h in hits] == [(2, '1'), (4, '4')]

def test_rule_of_three_line_number_mid_text():
    hits = [h for h in find_tells('Fine here.\nWe did it. Write. Edit. Ship.') if h['category'] == '7']
    assert hits and hits[0]['line'] == 2

def test_all_nine_source_categories_present():
    cats = {c['id'] for _, _, c in load_patterns()}
    assert {str(i) for i in range(1, 10)} <= cats

def test_cli_exit_codes(tmp_path):
    clean = subprocess.run(CLI, input='It answers my client emails.', capture_output=True, text=True)
    assert clean.returncode == 0 and 'clean' in clean.stdout
    bad = subprocess.run(CLI, input='ok\nClaude quietly shipped it.', capture_output=True, text=True)
    assert bad.returncode == 1 and '<stdin>:2:' in bad.stdout and 'Quietly' in bad.stdout
    f = tmp_path / 'd.md'; f.write_text('Most people use Claude wrong.')
    r = subprocess.run(CLI + [str(f), '--json'], capture_output=True, text=True)
    assert r.returncode == 1 and '"clean": false' in r.stdout
    r = subprocess.run(CLI + [str(tmp_path / 'missing.md')], capture_output=True, text=True)
    assert r.returncode == 2
