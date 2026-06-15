import json
import os
import glob

# Find all existing skills
skill_dirs = glob.glob('skills/*/*')
existing_skills = [d.replace('\', '/') for d in skill_dirs if os.path.isdir(d)]
# Get just the skill name (last part of path)
existing_skill_names = [s.split('/')[-1] for s in existing_skills]

# Read stacks.json
with open('config/stacks.json', 'r') as f:
    stacks = json.load(f)

# Update skills lists
for stack_name, stack_data in stacks.items():
    if 'resources' in stack_data and 'skills' in stack_data['resources']:
        # Filter to only include existing skills
        current_skills = stack_data['resources']['skills']
        valid_skills = []
        for s in current_skills:
            if s in existing_skill_names:
                valid_skills.append(s)
            elif s == "migration-flow" and "migration-workflow" in existing_skill_names:
                valid_skills.append("migration-workflow")
                
        stack_data['resources']['skills'] = valid_skills

# Write back
with open('config/stacks.json', 'w') as f:
    json.dump(stacks, f, indent=2)
print("stacks.json updated")
