import cv2
from scipy.io import loadmat

# -------------------------------------------------
# Image Path
# -------------------------------------------------

image_path = r"C:\Users\hp\Desktop\Crowed Density\Sanghai DataSet\part_A\test_data\images\IMG_1.jpg"

# -------------------------------------------------
# MAT Path
# -------------------------------------------------

mat_path = r"C:\Users\hp\Desktop\Crowed Density\Sanghai DataSet\part_A\test_data\ground-truth\GT_IMG_1.mat"

# -------------------------------------------------
# Load Image
# -------------------------------------------------

image = cv2.imread(image_path)

# -------------------------------------------------
# Load Ground Truth
# -------------------------------------------------

mat = loadmat(mat_path)

points = mat["image_info"][0][0][0][0][0]

print("Actual People :", len(points))

# -------------------------------------------------
# Draw Every Head
# -------------------------------------------------

for point in points:

    x = int(point[0])

    y = int(point[1])

    cv2.circle(
        image,
        (x, y),
        3,
        (0, 0, 255),
        -1
    )

# -------------------------------------------------
# Show
# -------------------------------------------------

cv2.imshow("ShanghaiTech Ground Truth", image)

cv2.waitKey(0)

cv2.destroyAllWindows()