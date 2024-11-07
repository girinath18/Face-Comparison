import base64
import re

def encode_image_to_base64(image_path):
    """Encodes an image to a base64 string."""
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_string

def save_base64_to_file(base64_string, file_path):
    """Saves the base64 string to a text file."""
    try:
        with open(file_path, "w") as file:
            file.write(base64_string)
        print(f"Base64 string saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving base64 string to file: {e}")

def read_base64_from_file(file_path):
    """Reads the base64 string from a text file."""
    try:
        with open(file_path, "r") as file:
            base64_string = file.read()
        print(f"Base64 string read from {file_path}")
        return base64_string
    except Exception as e:
        print(f"An error occurred while reading base64 string from file: {e}")
        return ""

def decode_base64_to_image(base64_string, output_file_path):
    """Decodes a base64 string to an image file."""
    base64_string = base64_string.strip()
    base64_string = re.sub(r"^data:image/\w+;base64,", "", base64_string)
    base64_string += '=' * ((4 - len(base64_string) % 4) % 4)

    try:
        image_data = base64.b64decode(base64_string)
        with open(output_file_path, "wb") as output_file:
            output_file.write(image_data)
        print(f"Image saved successfully at {output_file_path}")
    except base64.binascii.Error as e:
        print("Failed to decode base64 string. It might be malformed. Error:", e)
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")

# Example usage
input_image_path = r"V:\Simplfin\face_comparision\Sam (3).jpg"  
encoded_file_path = "encoded_image.txt"  # File to save the base64 string
output_image_path = "output_image.jpeg"  # Replace with desired output file path

# Encode the image and save the base64 string to a file
base64_string = encode_image_to_base64(input_image_path)
save_base64_to_file(base64_string, encoded_file_path)

# Read the base64 string from the file and decode it back to an image
base64_string_from_file = read_base64_from_file(encoded_file_path)
decode_base64_to_image(base64_string_from_file, output_image_path)
