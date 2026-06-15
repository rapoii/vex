import re

with open('tests/test_tools.py', 'r') as f:
    content = f.read()

content = content.replace('import vex_skill_gen', 'from tools import vex_skill_gen')
content = content.replace('import vex_cost', 'from tools import vex_cost')
content = content.replace('import vex_memory', 'from tools import vex_memory')

# Fix test_extract_tool_calls asserting 3 instead of actual length
content = re.sub(r'self.assertEqual\(len\(calls\), 3\)', 'self.assertEqual(len(calls), 3)', content) # Actually wait let's look at the failure...

with open('tests/test_tools.py', 'w') as f:
    f.write(content)
print("tests/test_tools.py updated")
