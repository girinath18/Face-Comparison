# main.py

from deepface import DeepFace
import cv2
import matplotlib.pyplot as plt

def show_image(img_path):
    # Read and display the image
    img = cv2.imread(img_path)
    plt.imshow(img[:, :, ::-1])
    plt.show()
    return img

def main():
    # Load and display the first image
    img1_path = r'V:\Simplfin\face_comparision\navi_id1.png'
    img2_path = r'V:\Simplfin\face_comparision\navi_00.png'

    print("Displaying Image 1:")
    img1 = show_image(img1_path)

    print("Displaying Image 2:")
    img2 = show_image(img2_path)

    # Verify if images belong to the same person
    result = DeepFace.verify(img1, img2)
    print("Is same face: ", result['verified'])

if __name__ == "__main__":
    main()
