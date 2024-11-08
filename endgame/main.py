from flask import Flask, request, jsonify
import base64
import re
import os
from deepface import DeepFace
import tempfile

app = Flask(__name__)

def decode_base64_to_image(base64_string, output_file_path):
    try:
        # Remove any data URI scheme if present
        base64_string = re.sub(r"^data:image/\w+;base64,", "", base64_string)
        # Remove any non-base64 characters
        base64_string = re.sub(r"[^A-Za-z0-9+/=]", "", base64_string)
        # Ensure length is a multiple of 4 by adding padding if necessary
        missing_padding = len(base64_string) % 4
        if missing_padding:
            base64_string += '=' * (4 - missing_padding)
        # Decode and write to file
        with open(output_file_path, "wb") as output_file:
            output_file.write(base64.b64decode(base64_string))
        return True
    except base64.binascii.Error as e:
        print("Failed to decode base64 string. It might be malformed. Error:", e)
        return False
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")
        return False

@app.route('/compare_faces', methods=['POST'])
def compare_faces():
    data = request.get_json()
    if not data or 'img1_base64' not in data or 'img2_base64' not in data:
        return jsonify({"error": "Invalid input data. 'img1_base64' and 'img2_base64' fields are required."}), 400

    try:
        # Create temporary files for the images
        with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as img1_file, \
             tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as img2_file:
            img1_path, img2_path = img1_file.name, img2_file.name

            # Decode base64 strings to images
            if not decode_base64_to_image(data['img1_base64'], img1_path):
                return jsonify({"error": "Failed to decode img1_base64 to image"}), 400
            if not decode_base64_to_image(data['img2_base64'], img2_path):
                return jsonify({"error": "Failed to decode img2_base64 to image"}), 400

            # Verify if images belong to the same person
            result = DeepFace.verify(img1_path, img2_path)
            return jsonify({"same_face": result['verified']})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An internal error occurred during face comparison."}), 500
    finally:
        # Clean up temporary files
        if os.path.exists(img1_path):
            os.remove(img1_path)
        if os.path.exists(img2_path):
            os.remove(img2_path)

if __name__ == "__main__":
    app.run(debug=True)
