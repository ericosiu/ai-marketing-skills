#!/usr/bin/env python3
"""Check copy for the banned AI tells in banned-ai-tells.txt.

Usage:
  python3 check_tells.py draft.md [more files]
  echo "text" | python3 check_tells.py
  ... --json        machine-readable hits
Exit 0 = clean, 1 = hits (listed with line numbers), 2 = usage or pattern-file error.

Import: from check_tells import find_tells; find_tells(text) -> list of dicts.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PATTERNS = os.path.join(HERE, 'banned-ai-tells.txt')


def _decode(p):
    # allow \uXXXX / \UXXXXXXXX escapes in the txt for invisible or emoji characters
    return re.sub(r'\\U([0-9A-Fa-f]{8})|\\u([0-9A-Fa-f]{4})',
                  lambda m: re.escape(chr(int(m.group(1) or m.group(2), 16))), p)


def load_patterns(path=DEFAULT_PATTERNS):
    rules, cat = [], {'id': '?', 'label': 'uncategorized', 'fix': ''}
    with open(path, encoding='utf8') as f:
        for n, raw in enumerate(f, 1):
            line = raw.rstrip('\n')
            if line.startswith('#@'):
                parts = [x.strip() for x in line[2:].split('|')]
                cat = {'id': parts[0], 'label': parts[1] if len(parts) > 1 else parts[0],
                       'fix': parts[2] if len(parts) > 2 else ''}
                continue
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            try:
                rx = re.compile(_decode(line.strip()), re.I | re.M)
            except re.error as e:
                raise ValueError(f'{path}:{n}: bad pattern {line!r}: {e}')
            rules.append((rx, line.strip(), dict(cat)))
    return rules


_CACHE = {}

def find_tells(text, patterns_path=DEFAULT_PATTERNS):
    if patterns_path not in _CACHE:
        _CACHE[patterns_path] = load_patterns(patterns_path)
    hits = []
    text = text or ''
    starts = [0] + [m.end() for m in re.finditer('\n', text)]
    import bisect
    for rx, src, cat in _CACHE[patterns_path]:
        for m in rx.finditer(text):
            pos = m.start()
            if m.group(0)[:1] in '.!? \t\n':   # pattern 7 anchors on the previous sentence end
                pos += len(m.group(0)) - len(m.group(0).lstrip('.!? \t\n'))
            ln = bisect.bisect_right(starts, pos)
            line = text[starts[ln - 1]:].split('\n', 1)[0]
            hits.append({'line': ln, 'category': cat['id'], 'label': cat['label'], 'fix': cat['fix'],
                         'match': m.group(0).lstrip('.!? \t\n').strip(), 'text': line.strip()[:160]})
    hits.sort(key=lambda h: (h['line'], h['category']))
    return hits


def main(argv=None):
    ap = argparse.ArgumentParser(description='Flag banned AI tells (exit 1 on any hit).')
    ap.add_argument('files', nargs='*', help='files to check (default: stdin)')
    ap.add_argument('--patterns', default=DEFAULT_PATTERNS)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    try:
        sources = [(f, open(f, encoding='utf8').read()) for f in a.files] or [('<stdin>', sys.stdin.read())]
        allhits = []
        for name, text in sources:
            for h in find_tells(text, a.patterns):
                h['file'] = name
                allhits.append(h)
    except (OSError, ValueError) as e:
        print(f'check_tells: {e}', file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps({'clean': not allhits, 'hits': allhits}, ensure_ascii=False, indent=1))
    elif allhits:
        for h in allhits:
            print(f"{h['file']}:{h['line']}: [{h['category']}] {h['label']}: {h['match']!r}  -> fix: {h['fix']}")
        print(f'{len(allhits)} banned tell(s). Rewrite the line as what actually happened, not a synonym.')
    else:
        print('clean')
    return 1 if allhits else 0


if __name__ == '__main__':
    sys.exit(main())
