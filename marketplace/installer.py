import argparse
import json
import hashlib
import os
import urllib.request
import urllib.error

# Security: Define base directory for installation
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills"))
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "catalog.json")

def browse(args):
    with open(CATALOG_PATH, "r") as f:
        catalog = json.load(f)
    print("VEX Skill Marketplace")
    print("-" * 40)
    for skill in catalog.get("skills", []):
        print(f"{skill['name']} ({skill['category']}) - {skill['rating']} stars, {skill['downloads']} DLs")
        print(f"  {skill['description']}")
        print()

def install(args):
    with open(CATALOG_PATH, "r") as f:
        catalog = json.load(f)
    
    skill = next((s for s in catalog.get("skills", []) if s["name"] == args.skill_name), None)
    if not skill:
        print(f"Error: Skill '{args.skill_name}' not found in catalog.")
        return
        
    print(f"Installing {args.skill_name} from {skill['install_url']}...")
    
    # Path resolution & security check
    target_dir = os.path.abspath(os.path.join(BASE_DIR, skill['category'], args.skill_name))
    
    # SECURITY: Prevent path traversal
    if not target_dir.startswith(BASE_DIR):
        print(f"SECURITY BLOCKED: Path traversal attempt. Target resolves outside {BASE_DIR}")
        return
        
    try:
        # Create directory safely
        os.makedirs(target_dir, exist_ok=True)
        manifest_path = os.path.join(target_dir, "manifest.json")
        
        # Security validation: URL allowlist
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
            print(f"Success! {args.skill_name} installed to {target_dir}")
        except urllib.error.URLError as e:
            # Fallback for testing/offline: just create stub
            print(f"Network error ({e}), writing stub manifest.")
            with open(manifest_path, "w") as f:
                json.dump({"name": args.skill_name, "version": "1.0.0"}, f, indent=2)
            print(f"Created stub for {args.skill_name} at {target_dir}")
            
    except Exception as e:
        print(f"Install failed: {e}")

def rate(args):
    if args.rating < 1 or args.rating > 5:
        print("Rating must be between 1 and 5.")
        return
        
    with open(CATALOG_PATH, "r") as f:
        catalog = json.load(f)
        
    found = False
    for skill in catalog.get("skills", []):
        if skill["name"] == args.skill_name:
            # Simple local update
            skill["rating"] = round((skill["rating"] * skill["downloads"] + args.rating) / (skill["downloads"] + 1), 1)
            skill["downloads"] += 1
            found = True
            break
            
    if not found:
        print(f"Error: Skill '{args.skill_name}' not found.")
        return
        
    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog, f, indent=2)
        
    print(f"Rated {args.skill_name} {args.rating}/5 successfully.")

def publish(args):
    print("Publishing to VEX Marketplace is driven by GitHub Pull Requests.")
    print(f"1. Ensure your skill at '{args.skill_dir}' has a manifest.json and README.md.")
    print("2. Fork the Vareva/VEX repository.")
    print(f"3. Add your skill metadata to marketplace/catalog.json.")
    print("4. Submit a Pull Request with the 'marketplace' label.")

def main():
    parser = argparse.ArgumentParser(description="VEX Marketplace CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # browse
    subparsers.add_parser("browse", help="List available skills")
    
    # install
    install_parser = subparsers.add_parser("install", help="Install a skill")
    install_parser.add_argument("skill_name", help="Name of the skill to install")
    
    # rate
    rate_parser = subparsers.add_parser("rate", help="Rate a skill")
    rate_parser.add_argument("skill_name", help="Name of the skill")
    rate_parser.add_argument("rating", type=int, help="Rating 1-5")
    
    # publish
    publish_parser = subparsers.add_parser("publish", help="Prepare a skill for publishing")
    publish_parser.add_argument("skill_dir", help="Directory of the skill to publish")
    
    args = parser.parse_args()
    
    if args.command == "browse":
        browse(args)
    elif args.command == "install":
        install(args)
    elif args.command == "rate":
        rate(args)
    elif args.command == "publish":
        publish(args)

if __name__ == "__main__":
    main()
