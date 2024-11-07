import base64
import re

def decode_base64_to_image(input_file_path, output_file_path):
    """Decodes a base64 string from a text file to an image file."""
    try:
        # Step 1: Read the base64 string from the text file
        with open(input_file_path, "r") as file:
            base64_string = file.read().strip()
        
        # Step 2: Remove any data URI scheme if present
        base64_string = re.sub(r"^data:image/\w+;base64,", "", base64_string)
        
        # Step 3: Remove any non-base64 characters
        base64_string = re.sub(r"[^A-Za-z0-9+/=]", "", base64_string)

        # Step 4: Ensure length is a multiple of 4 by adding padding if necessary
        missing_padding = len(base64_string) % 4
        if missing_padding:
            base64_string += '=' * (4 - missing_padding)

        # Decode the base64 string
        image_data = base64.b64decode(base64_string)
        
        # Write to output file
        with open(output_file_path, "wb") as output_file:
            output_file.write(image_data)
        print(f"Image saved successfully at {output_file_path}")
        
    except FileNotFoundError:
        print(f"File not found: {input_file_path}")
    except base64.binascii.Error as e:
        print("Failed to decode base64 string. It might be malformed. Error:", e)
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")

# Hardcoded file paths
input_text_path_1 = "first_img.txt"  
output_image_path_1 = "img1.jpeg"    

input_text_path_2 = "second_img.txt"  
output_image_path_2 = "img2.jpeg"     

# Decode both images
decode_base64_to_image(input_text_path_1, output_image_path_1)
decode_base64_to_image(input_text_path_2, output_image_path_2)
