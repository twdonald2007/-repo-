from google.cloud import vision
from dotenv import load_dotenv
import os

# 1) Load .env file from the current folder
load_dotenv()

# 2) (Optional) print to confirm it's loaded
print("GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

def test_label_detection(image_path):
    # 3) Now the client can see the credentials
    client = vision.ImageAnnotatorClient()

    with open(image_path, "rb") as f:
        content = f.read()

    image = vision.Image(content=content)
    response = client.label_detection(image=image, max_results=10)

    if response.error.message:
        raise Exception(response.error.message)

    for label in response.label_annotations:
        print(label.description, "=>", label.score)

if __name__ == "__main__":
    # TODO: replace with an actual existing image on your PC
    test_label_detection(r"C:\Users\Stapat\Downloads\images.webp")
