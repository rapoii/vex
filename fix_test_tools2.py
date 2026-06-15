import re

with open('tests/test_tools.py', 'r') as f:
    content = f.read()

# Fix 1: vex-cost.py to vex_cost.py in subprocess calls
content = content.replace('tools/vex-cost.py', 'tools/vex_cost.py')
content = content.replace('tools/vex-skill-gen.py', 'tools/vex_skill_gen.py')
content = content.replace('tools/vex-memory.py', 'tools/vex_memory.py')

# Fix 2: Patch correct module path for mocks
content = content.replace('@patch(\'vex_cost.ensure_vex_dir\')', '@patch(\'tools.vex_cost.ensure_vex_dir\')')
content = content.replace('@patch(\'vex_cost.find_session_files\')', '@patch(\'tools.vex_cost.find_session_files\')')
content = content.replace('@patch(\'vex_memory.ensure_vex_dir\')', '@patch(\'tools.vex_memory.ensure_vex_dir\')')
content = content.replace('@patch(\'vex_memory.find_session_files\')', '@patch(\'tools.vex_memory.find_session_files\')')

# Fix 3: extract_tool_calls failing because input is old Claude format?
# Let's fix vex_skill_gen.py instead

with open('tests/test_tools.py', 'w') as f:
    f.write(content)
print("tests/test_tools.py updated again")
