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
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")
        return False

@app.route('/compare_faces', methods=['POST'])
def compare_faces():
    data = request.get_json()
    if not data or 'img1_base64' not in data or 'img2_base64' not in data:
        return jsonify({"error": "Invalid input data. 'img1_base64' and 'img2_base64' fields are required."}), 400

    try:
        with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as img1_file, \
             tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as img2_file:
            img1_path, img2_path = img1_file.name, img2_file.name

            if not decode_base64_to_image(data['img1_base64'], img1_path):
                return jsonify({"error": "Failed to decode img1_base64 to image"}), 400
            if not decode_base64_to_image(data['img2_base64'], img2_path):
                return jsonify({"error": "Failed to decode img2_base64 to image"}), 400

            if not (os.path.exists(img1_path) and os.path.exists(img2_path)):
                return jsonify({"error": "Image files not found after decoding."}), 500

            try:
                result = DeepFace.verify(img1_path, img2_path)
                distance = result['distance']
                threshold = 0.4  # Adjust based on the model you're using

                # Calculate match percentage using an exponential decay model
                match_percentage = max(0, (1 - (distance / threshold) ** 2) * 100)

                return jsonify({
                    "same_face": result['verified'],
                    "match_percentage": round(match_percentage, 2)
                })
            except Exception as e:
                print(f"An error occurred during DeepFace verification: {e}")
                return jsonify({"error": "An error occurred during face verification."}), 500

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred during face comparison."}), 500
    finally:
        if os.path.exists(img1_path):
            os.remove(img1_path)
        if os.path.exists(img2_path):
            os.remove(img2_path)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3030)
