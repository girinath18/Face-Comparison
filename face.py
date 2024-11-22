from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import re
import os
from deepface import DeepFace
import tempfile

app = Flask(__name__)
CORS(app)

def decode_base64_to_image(base64_string, output_file_path):
    try:
        base64_string = re.sub(r"^data:image/\w+;base64,", "", base64_string)
        base64_string = re.sub(r"[^A-Za-z0-9+/=]", "", base64_string)
        missing_padding = len(base64_string) % 4
        if missing_padding:
            base64_string += '=' * (4 - missing_padding)
        with open(output_file_path, "wb") as output_file:
            output_file.write(base64.b64decode(base64_string))
        return True
    except Exception:
        return False  # Avoid exposing exception details

@app.route('/compare_faces', methods=['POST'])
def compare_faces():
    data = request.get_json()
    if not data or 'img1_base64' not in data or 'img2_base64' not in data:
        return jsonify({"error": "Both 'uploaded image' and 'captured image' fields are required."}), 400

    try:
        with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as uploaded_image_file, \
             tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as captured_image_file:
            uploaded_image_path = uploaded_image_file.name
            captured_image_path = captured_image_file.name

            # Decode uploaded image
            uploaded_image_decoded = decode_base64_to_image(data['img1_base64'], uploaded_image_path)
            if not uploaded_image_decoded:
                return jsonify({
                    "error": "The uploaded image could not be processed. Please ensure it is a valid Base64-encoded image."
                }), 400

            # Decode captured image
            captured_image_decoded = decode_base64_to_image(data['img2_base64'], captured_image_path)
            if not captured_image_decoded:
                return jsonify({
                    "error": "The captured image could not be processed. Please ensure it is a valid Base64-encoded image."
                }), 400

            # Check if images exist
            if not (os.path.exists(uploaded_image_path) and os.path.exists(captured_image_path)):
                return jsonify({
                    "error": "One or both images could not be saved. Please try again with valid images."
                }), 500

            try:
                # Verify faces individually
                uploaded_face_detected = DeepFace.detectFace(uploaded_image_path, enforce_detection=True)
            except ValueError:
                return jsonify({
                    "error": "Unable to detect a face in the uploaded image. Please retry."
                }), 200

            try:
                captured_face_detected = DeepFace.detectFace(captured_image_path, enforce_detection=True)
            except ValueError:
                return jsonify({
                    "error": "Unable to detect a face in the captured image. Please retry."
                }), 200

            try:
                # Face verification
                result = DeepFace.verify(uploaded_image_path, captured_image_path)
                distance = result['distance']
                threshold = 0.4  # Adjust based on the model you're using

                # Calculate match percentage using an exponential decay model
                match_percentage = max(0, (1 - (distance / threshold) ** 2) * 100)

                return jsonify({
                    "verified": result['verified'],
                    "match_percentage": round(match_percentage, 2)
                })
            except Exception:
                return jsonify({
                    "error": "An error occurred during face verification. Please retry with valid images."
                }), 500

    except Exception:
        return jsonify({
            "error": "An unexpected error occurred during the process. Please try again."
        }), 500
    finally:
        # Cleanup temporary files
        for path in [uploaded_image_path, captured_image_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3030)
