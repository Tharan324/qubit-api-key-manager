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
    if response is None:
        return jsonify({"message": "Error in creating API key. Please try again"}), 500
    elif response is False:
        return jsonify({"message": "Incorrect email or role"}), 400

    return jsonify({"message": "Successfully created key",
                    "apiKey": response["key"],
                    "expiryTill": response["exp"]}), 200
    

@app.route('/validate', methods=['POST'])
def validate():
    data = request.get_json()
    api_key = data.get('apiKey')
    if not api_key:
        return jsonify({"error": "API key is required!"}), 400
    response = validate_api_key(api_key)
    status_code = 200 if response["valid"] else 400
    return jsonify(response), status_code

# OAuth endpoints
@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    try:
        data = request.get_json()
        code = data.get('code')
        code_verifier = data.get('code_verifier')

        # Exchange code for token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code_verifier': code_verifier,
            'grant_type': 'authorization_code',
            'redirect_uri': f"{request.headers.get('Origin')}/auth/callback"
        }

        token_response = http_requests.post(token_url, data=token_data)
        if not token_response.ok:
            return jsonify({'error': 'Failed to exchange code'}), 400

        token_json = token_response.json()
        id_token_jwt = token_json['id_token']

        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            id_token_jwt, requests.Request(), GOOGLE_CLIENT_ID)

        user_data = {
            'sub': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture')
        }

        # Save session to MongoDB
        session_token = save_user_session(user_data)
        if not session_token:
            return jsonify({'error': 'Failed to create session'}), 500

        response = jsonify({
            'email': user_data['email'],
            'name': user_data['name'],
            'picture': user_data['picture']
        })
        
        # Set session cookie
        response.set_cookie(
            'session_token',
            session_token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=86400  # 24 hours
        )

        return response

    except Exception as e:
        print(f"Error in /auth/google: {str(e)}")
        return jsonify({'error': 'Authentication failed'}), 401

@app.route('/api/auth/verify', methods=['GET'])
def verify_session():
    try:
        session_token = request.cookies.get('session_token')
        if not session_token:
            return jsonify({'error': 'No session'}), 401

        user_data = get_user_session(session_token)
        if not user_data:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        return jsonify({
            'email': user_data['email'],
            'name': user_data['name'],
            'picture': user_data['picture']
        })

    except Exception as e:
        print(f"Error in /auth/verify: {str(e)}")
        return jsonify({'error': 'Invalid session'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        session_token = request.cookies.get('session_token')
        if session_token:
            delete_user_session(session_token)
        
        response = jsonify({'message': 'Logged out successfully'})
        response.delete_cookie('session_token')
        return response
    except Exception as e:
        print(f"Error in /auth/logout: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)