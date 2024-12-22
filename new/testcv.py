import numpy as np
import cv2
from matplotlib import pyplot as plt

print("NumPy version:", np.__version__)
print("OpenCV version:", cv2.__version__)

# 创建测试图像
img = np.zeros((100, 100, 3), dtype=np.uint8)

# 使用 Matplotlib 显示
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title("Test Image")
plt.show()
