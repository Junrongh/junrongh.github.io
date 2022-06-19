import cv2
import sys

src = sys.argv[1]
size = '512x512'
if len(sys.argv) == 3:
    size = sys.argv[2]

w, h = size.split('x')
w = int(w)
h = int(h)
img = cv2.imread(src)
out = cv2.resize(img, [w, h])
cv2.imwrite(src, out)
