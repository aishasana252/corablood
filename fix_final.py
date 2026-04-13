import os

path = r"C:\Users\Majed\.gemini\antigravity\scratch\CoraBlood-Ultimate\templates\donors\workflow.html"

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check for the broken tag at lines 114-115 (0-indexed)
idx = 114
if 0 <= idx < len(lines)-1:
    line1 = lines[idx]
    line2 = lines[idx+1]
    
    # Check if lines match the broken pattern
    # Line 115: {% if not active_workflow or active_workflow.status == 'COMPLETED' or active_workflow.status ==\n
    # Line 116:                     'DEFERRED' %}\n
    
    if "active_workflow.status ==" in line1 and "'DEFERRED' %}" in line2:
        print("Found broken tag. Fixing...")
        
        # Construct the correct single line
        # Use exact indentation and spacing to match style
        new_line = "                    {% if not active_workflow or active_workflow.status == 'COMPLETED' or active_workflow.status == 'DEFERRED' %}\n"
        
        lines[idx] = new_line
        lines[idx+1] = "" # Mark for deletion
        
        # Remove the marked line
        lines.pop(idx+1)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Fixed syntax error.")
    else:
        print("Tag appears correct or pattern not found.")
        print(f"Line {idx+1}: {line1!r}")
        print(f"Line {idx+2}: {line2!r}")
else:
    print("File too short.")
