import os

path = r'd:\CoraBlood-Ultimat-main\templates\donors\workflow.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add {% load static %} if missing
if '{% load static %}' not in content:
    content = '{% load static %}\n' + content

# 2. Config script
config_script = """
{% load static %}
<script src="{% static 'js/workflow-engine.js' %}"></script>
<script>
    const workflowConfig = {
        donorDetails: {
            full_name: '{{ donor.full_name|escapejs }}',
            national_id: '{{ donor.national_id|escapejs }}',
            mobile: '{{ donor.mobile|escapejs }}',
            nationality: '{{ donor.nationality|escapejs }}',
            blood_group: '{{ donor.blood_group|default:""|escapejs }}',
            date_of_birth: '{{ donor.date_of_birth|date:"Y-m-d" }}',
            gender: '{{ donor.gender|escapejs }}'
        },
        donationId: "{{ active_workflow.id|default:'' }}",
        activeStatus: "{{ active_workflow.status|default:'' }}",
        workflowType: "{{ active_workflow.workflow_type|default:'WHOLE_BLOOD' }}",
        csrfToken: "{{ csrf_token }}",
        donationCode: "{{ active_workflow.donation_code|default:'' }}"
    };
</script>
"""

# Replace the block at line 13 roughly
if '<script>' in content and 'window.workflowModules' in content:
    # Find the script tag containing window.workflowModules
    start = content.find('<script>')
    end = content.find('</script>', start) + 9
    content = content[:start] + config_script + content[end:]

# 3. Update x-data
content = content.replace('x-data="donationWorkflow()"', 'x-data="donationWorkflow(workflowConfig)"')

# 4. Remove extra_js massive block
extra_js_marker = '{% block extra_js %}'
endblock_marker = '{% endblock %}'

parts = content.split(extra_js_marker)
if len(parts) > 1:
    # We found the block
    rest = parts[1].split(endblock_marker)
    # rest[0] is the old JS script
    # rest[1] is anything after the endblock
    content = parts[0] + extra_js_marker + '\n<!-- Workflow Engine v1.0 Loaded -->\n' + endblock_marker + rest[1]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Modularization complete.")
