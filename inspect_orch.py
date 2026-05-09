#!/usr/bin/env python3
import re

with open('/workspace/biofish-ai/src/orchestrator.py') as f:
    c = f.read()

# Find all patterns: return "", ["item1", "item2"]
# These need to become: return "", ["item1"], ["item2"]
# But we need to handle f-strings properly (with quotes inside)

# Simple approach: replace ], [\n  pattern
# The broken pattern: return "", [f"..."]],\n
# The fix: put each list item on its own line

# Find positions of all return "", [ that are followed by a list with comma inside
results = []
for m in re.finditer(r'return "", \[([^\]]+)\]', c):
    pos = m.start()
    snippet = c[pos:pos+200]
    results.append((pos, snippet[:100]))

print(f"Found {len(results)} return '', [...] patterns")
for pos, s in results[:5]:
    print(f"  pos {pos}: {repr(s)}")
