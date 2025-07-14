import cv2

# Load the image
image = cv2.imread(r'D:\identityOG\identity_theft\identity_theft\samplalph1a.png')

blurred = cv2.medianBlur(image, 31)  # Kernel size 15
cv2.imwrite('median_blur.jpg', blurred)

# Apply Gaussian Blur

# Display the images
cv2.imshow('Original', image)
cv2.imshow('Blurred', blurred)
cv2.waitKey(0)
cv2.destroyAllWindows()
