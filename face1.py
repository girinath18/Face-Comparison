from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import re
import os
from deepface import DeepFace
import tempfile
from PIL import Image
import tensorflow as tf

app = Flask(__name__)
CORS(app)

# Limit TensorFlow memory usage
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    for device in physical_devices:
        tf.config.experimental.set_memory_growth(device, True)

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
        return False

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

            # Decode images
            if not decode_base64_to_image(data['img1_base64'], uploaded_image_path):
                return jsonify({"error": "The uploaded image could not be processed."}), 400
            if not decode_base64_to_image(data['img2_base64'], captured_image_path):
                return jsonify({"error": "The captured image could not be processed."}), 400

            try:
                # Detect and preprocess faces
                uploaded_face = DeepFace.detectFace(uploaded_image_path, enforce_detection=True)
                captured_face = DeepFace.detectFace(captured_image_path, enforce_detection=True)
            except ValueError as e:
                if "uploaded image" in str(e):
                    return jsonify({"error": "Unable to detect a face in the uploaded image. Please retry."}), 200
                elif "captured image" in str(e):
                    return jsonify({"error": "Unable to detect a face in the captured image. Please retry."}), 200
                else:
                    return jsonify({"error": "Face detection failed. Please use clear images."}), 200

            try:
                # Verify faces using a robust model (Facenet512 for higher accuracy)
                result = DeepFace.verify(uploaded_image_path, captured_image_path, model_name='Facenet512')
                distance = result['distance']
                threshold = result['threshold']  # Use threshold from the model's output for accuracy

                # Calculate match percentage
                match_percentage = max(0, (1 - (distance / threshold) ** 2) * 100)

                return jsonify({
                    "verified": result['verified'],
                    "match_percentage": round(match_percentage, 2)
                })
            except Exception:
                return jsonify({"error": "Face verification failed. Please retry with valid images."}), 500

    except Exception:
        return jsonify({"error": "An unexpected error occurred."}), 500
    finally:
        # Cleanup temporary files
        for path in [uploaded_image_path, captured_image_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=3030)
