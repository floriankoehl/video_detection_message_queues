import cv2





img = cv2.imread("../data/image_0.jpg")


if img is None: 
    print("Image could not be loaded")
else: 
    print("image shape: ", img.shape)
    print("image data type: ", img.dtype)



