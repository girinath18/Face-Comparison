import base64
import re

def decode_base64_to_image(base64_string, output_file_path):
    # Clean up the base64 string
    base64_string = base64_string.strip()
    
    # Remove header if present
    base64_string = re.sub(r"^data:image/\w+;base64,", "", base64_string)
    
    # Add padding if necessary to make the length a multiple of 4
    base64_string += '=' * ((4 - len(base64_string) % 4) % 4)
    
    try:
        # Decode the base64 string
        image_data = base64.b64decode(base64_string)
        
        # Write the binary image data to a file
        with open(output_file_path, "wb") as output_file:
            output_file.write(image_data)
        print(f"Image saved successfully at {output_file_path}")
    except base64.binascii.Error as e:
        print("Failed to decode base64 string. It might be malformed. Error:", e)
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")

# Get the base64 string from user input for decoding
user_base64_string = input("Enter the base64 string to decode: ")

# Decode the base64 string back to an image
output_file_path = "output_image.jpeg"  # Specify where you want to save the decoded image
decode_base64_to_image(user_base64_string, output_file_path)
