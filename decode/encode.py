import base64

def encode_image_to_base64(image_path):
    """Encodes an image file to a base64 string."""
    # Open the image file in binary mode
    with open(image_path, "rb") as image_file:
        # Read the binary data and encode it as base64
        base64_string = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_string

def save_base64_to_file(base64_string, output_file_path):
    """Saves a base64 string to a text file."""
    try:
        with open(output_file_path, "w") as file:
            file.write(base64_string)
        print(f"Base64 string saved successfully to {output_file_path}")
    except Exception as e:
        print(f"An error occurred while saving the base64 string: {e}")

# Example usage
image_path = r"V:\Simplfin\face_comparision\Nayan (17).jpg"  # Replace with your image file path
output_text_path = "second_base64.txt"  # Path to save the base64-encoded string

# Encode the image and save the base64 string to a text file
base64_string = encode_image_to_base64(image_path)
save_base64_to_file(base64_string, output_text_path)
