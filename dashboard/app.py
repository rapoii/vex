from flask import Flask, jsonify, request

app = Flask(__name__)

# Basic auth token for tests
AUTH_TOKEN = "test-token"

def require_auth(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token != AUTH_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route("/")
def index():
    return "VEX Dashboard", 200

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/agents")
@require_auth
def get_agents():
    return jsonify({"agents": [{"name": "planner"}, {"name": "architect"}]}), 200

if __name__ == "__main__":
    app.run(port=8080)