
import os

file_path = r"c:\Users\Majed\.gemini\antigravity\scratch\CoraBlood-Ultimate\templates\donors\workflow.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The problematic string with the newline and spaces
target = "{% if not active_workflow or active_workflow.status == 'COMPLETED' or active_workflow.status ==\n                    'DEFERRED' %}"
replacement = "{% if not active_workflow or active_workflow.status == 'COMPLETED' or active_workflow.status == 'DEFERRED' %}"

if target in content:
    print("Found target string. Removing newline...")
    new_content = content.replace(target, replacement)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File updated successfully.")
else:
    print("Target string not found.")
    # Fallback: search for generic split tags if any
    import re
    # This regex looks for {% if ... \n ... %}
    pattern = re.compile(r'({% if [^%]+)\n\s+([^%]+%})', re.MULTILINE)
    
    def replacer(match):
        print(f"Found generic split tag: {match.group(0)}")
        return match.group(1) + " " + match.group(2)
        
    new_content_2, count = pattern.subn(replacer, content)
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content_2)
        print(f"Fixed {count} split tags using regex.")
