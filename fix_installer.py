import re

with open('marketplace/installer.py', 'r') as f:
    content = f.read()

if 'import hashlib' not in content:
    content = content.replace('import json', 'import json\nimport hashlib')

# Add validation logic to install
old_install = """        # Download mock or real. If network fails, handle gracefully
        req = urllib.request.Request(skill['install_url'], headers={'User-Agent': 'VEX-Installer/1.0'})
        try:
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                with open(manifest_path, "w") as f:
                    f.write(content)
            print(f"Success! {args.skill_name} installed to {target_dir}")"""

new_install = """        # Security validation: URL allowlist
        if not skill['install_url'].startswith('https://raw.githubusercontent.com/rapoii/vex/'):
            print(f"SECURITY BLOCKED: URL not in allowlist: {skill['install_url']}")
            return
            
        req = urllib.request.Request(skill['install_url'], headers={'User-Agent': 'VEX-Installer/1.0'})
        try:
            with urllib.request.urlopen(req) as response:
                # Security validation: Content-Type
                content_type = response.headers.get('Content-Type', '')
                if 'text/plain' not in content_type and 'application/json' not in content_type:
                    print(f"SECURITY BLOCKED: Invalid Content-Type: {content_type}")
                    return
                    
                # Security validation: Max size (1MB) and Hash check
                MAX_SIZE = 1024 * 1024
                downloaded_data = bytearray()
                hasher = hashlib.sha256()
                
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    downloaded_data.extend(chunk)
                    hasher.update(chunk)
                    if len(downloaded_data) > MAX_SIZE:
                        print(f"SECURITY BLOCKED: File exceeds {MAX_SIZE} bytes")
                        return
                
                # Check hash if provided
                expected_hash = skill.get('hash')
                if expected_hash and hasher.hexdigest() != expected_hash:
                    print(f"SECURITY BLOCKED: Hash mismatch. Expected {expected_hash}, got {hasher.hexdigest()}")
                    return
                    
                content = downloaded_data.decode('utf-8')
                with open(manifest_path, "w") as f:
                    f.write(content)
            print(f"Success! {args.skill_name} installed to {target_dir}")"""

content = content.replace(old_install, new_install)

with open('marketplace/installer.py', 'w') as f:
    f.write(content)
print("Installer updated")
