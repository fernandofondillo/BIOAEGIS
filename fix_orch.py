#!/usr/bin/env python3
import re, py_compile

with open('/workspace/biofish-ai/src/orchestrator.py') as f:
    c = f.read()

print("Before: %d returns" % c.count('return'))

def fix_return(m):
    inner = m.group(1)
    items = []
    depth = 0
    current = ""
    for ch in inner:
        if ch == "[":
            depth += 1
            current += ch
        elif ch == "]":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            if current.strip():
                items.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        items.append(current.strip())
    if len(items) < 2:
        return m.group(0)
    if len(items) == 2:
        return 'return "", [%s], [%s]' % (items[0], items[1])
    concerns = items[0]
    actions = ", ".join(items[1:])
    return 'return "", [%s], [%s]' % (concerns, actions)

pattern = r'return "", \[([^\]]+(?:,[^\]]*)+)\]'
fixed, n = re.subn(pattern, fix_return, c)
print("Fixed %d multi-item list returns" % n)

with open('/workspace/biofish-ai/src/orchestrator.py', 'w') as f:
    f.write(fixed)

try:
    py_compile.compile('/workspace/biofish-ai/src/orchestrator.py', doraise=True)
    print("VALID")
except Exception as e:
    print("Error: %s" % str(e))
