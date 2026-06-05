import cv2
from pathlib import Path

img = cv2.imread("../data/image_0.jpg")


if img is None: 
    print("Image could not be loaded")
else: 
    height, width = img.shape[0], img.shape[1]

    print("image shape: ", img.shape)
    print("image data type: ", img.dtype)

    cv2.rectangle(img, (100, 100), (width-100, height-100), (0,0,255), 5)
    cv2.putText(img, "Test My first", (100,50), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255,0,0), 1)


    output_path = Path("../output_tests/result.jpg")
    saved = cv2.imwrite(str(output_path), img)

    print("saved? -> ", saved)
    if saved and output_path.exists():
        print("File safed sucessfully")
    else: 
        print("Save failed")
    
