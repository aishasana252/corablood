
import re

with open(r"d:\CoraBlood-Ultimat-main\templates\donors\workflow.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

stack = []
for i, line in enumerate(lines):
    # Find all opening tags (simplified)
    openings = re.findall(r'<div(?![a-z])', line)
    closings = re.findall(r'</div>', line)
    
    for _ in openings:
        stack.append(i + 1)
    
    for _ in closings:
        if stack:
            stack.pop()
        else:
            print(f"Excess closing div at line {i+1}")

if stack:
    print(f"Unclosed divs starting at lines: {stack}")
