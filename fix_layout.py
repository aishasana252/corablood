
import os

file_path = r"c:\Users\Majed\.gemini\antigravity\scratch\CoraBlood-Ultimate\templates\donors\workflow.html"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Locate the misplaced closing divs and the start of Lab Tests tab
split_index = -1
lab_test_start_index = -1

for i, line in enumerate(lines):
    if '<!-- 12. Lab Tests Tab -->' in line:
        lab_test_start_index = i
        # Look backwards for the two closing divs
        if i >= 2 and '</div>' in lines[i-1] and '</div>' in lines[i-2]:
            split_index = i - 2
        break

if split_index != -1 and lab_test_start_index != -1:
    print(f"Found split at line {split_index} and Lab Tests start at {lab_test_start_index}")
    
    # Extract the closing divs
    closing_divs = lines[split_index:lab_test_start_index]
    
    # Find the end of Lab Tests tab (it ends before 13. Self Exclusion)
    lab_test_end_index = -1
    for i in range(lab_test_start_index, len(lines)):
        if '<!-- 13. Self Exclusion Tab -->' in lines[i] or '{% endblock %}' in lines[i]:
             lab_test_end_index = i
             break
    
    if lab_test_end_index == -1:
        # If not found, assuming it goes until end of block or similar, but let's be safe and look for the specific end of the tab div
        # Actually in the replacement it was just before {% endblock %} or next tab
        # Let's just grab everything from lab_test_start_index down to just before the next tab or endblock
        pass

    # Actually, simpler approach:
    # 1. Read all lines.
    # 2. Pop the two lines at split_index (the two </div>s).
    # 3. Insert them AFTER the Lab Tests tab content.
    
    # Let's find where to re-insert them.
    # The Lab Tests tab was inserted. It should be closed.
    # I need to find the END of the Lab Tests tab div.
    # In the file view, it ended with a </div> and then {% endblock %} was nearby or next tab.
    
    # Refined strategy:
    # 1. Identify the block of lines for "Lab Tests Tab".
    # 2. Identify the two closing </div> lines immediately preceding it.
    # 3. Move those two </div> lines to *after* the Lab Tests Tab block.
    
    lab_tab_content = []
    # capture lines from lab_test_start_index until next tab or endblock
    current_idx = lab_test_start_index
    while current_idx < len(lines):
        if '<!-- 13. Self Exclusion Tab -->' in lines[current_idx] or '{% endblock %}' in lines[current_idx]:
             break
        lab_tab_content.append(lines[current_idx])
        current_idx += 1
    
    lab_tab_end_line_idx = current_idx
    
    print(f"Lab Tab block is from {lab_test_start_index} to {lab_tab_end_line_idx}")
    
    # Construct new file content
    new_lines = []
    new_lines.extend(lines[:split_index]) # Everything before the closing divs
    new_lines.extend(lab_tab_content)     # The Lab Tab content
    new_lines.extend(lines[split_index:lab_test_start_index]) # The two closing divs (now put AFTER)
    new_lines.extend(lines[lab_tab_end_line_idx:]) # The rest of the file
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("reordered workflow.html successfully")

else:
    print("Could not find the expected structure.")
