from flask import Flask, jsonify, request
from functions import generate_api_key, validate_api_key

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the Flask API!"})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email is required!"}), 400
    response = generate_api_key(email, 'user')
    if response is not None:
        return jsonify({"message": "Successfully created key",
                        "apiKey": response["key"],
                        "expiryTill": response["exp"]}), 200
    return jsonify({"message": "Error in creating API key. Please try again"}), 500

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    api_key = data.get('apiKey')
    if not api_key:
        return jsonify({"error": "API key is required!"}), 400
    response = validate_api_key(api_key)
    status_code = 200 if response["valid"] else 400
    return jsonify(response), status_code

if __name__ == "__main__":
    app.run(debug=True)