import re

with open('dashboard/server.py', 'r') as f:
    content = f.read()

# Add imports if missing
if 'import secrets' not in content:
    content = content.replace('import os', 'import os\nimport secrets')

# Add token generation and auth check
auth_code = """
# Generate auth token
AUTH_TOKEN = secrets.token_urlsafe(16)
print(f"\n{'='*50}")
print(f"VEX Dashboard running!")
print(f"Access token: {AUTH_TOKEN}")
print(f"Use ?token={AUTH_TOKEN} or Authorization header")
print(f"{'='*50}\n")

def check_auth():
    # Allow static files without auth
    if request.path.startswith('/static/'):
        return None
        
    token = request.args.get('token')
    auth_header = request.headers.get('Authorization')
    
    if token == AUTH_TOKEN:
        return None
    
    if auth_header and auth_header.startswith('Bearer ') and auth_header.split(' ')[1] == AUTH_TOKEN:
        return None
        
    return jsonify({"error": "Unauthorized"}), 401

@app.before_request
def enforce_auth():
    return check_auth()
"""

if 'AUTH_TOKEN' not in content:
    content = content.replace('app = Flask(__name__)', f'app = Flask(__name__)\n{auth_code}')

# Add threaded=True
content = content.replace('app.run(port=8080)', 'app.run(port=8080, threaded=True)')
content = content.replace('app.run(host="0.0.0.0", port=8080)', 'app.run(host="0.0.0.0", port=8080, threaded=True)')
content = content.replace('app.run(host=\'0.0.0.0\', port=8080)', 'app.run(host=\'0.0.0.0\', port=8080, threaded=True)')

with open('dashboard/server.py', 'w') as f:
    f.write(content)
print("Server updated")
