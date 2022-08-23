import numpy as np
import cv2
import sys

sys.path.append('')
from core.d_writeJson import *


# 膨胀
def dilate_demo(thresh):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))  # 定义结构元素的形状和大小
    dst = cv2.dilate(thresh, kernel)  # 膨胀操作
    return dst


# 腐蚀
def erode_demo(thresh):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))  # 定义结构元素的形状和大小
    dst = cv2.erode(thresh, kernel)  # 腐蚀操作
    return dst


img = cv2.imread("../image/vessel.jpg")
imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# cv2.threshold (源图片, 阈值, 填充色, 阈值类型)灰度值大于50赋值255，反之0
# 返回值：输入的thresh值，处理后的图像
ret, thresh = cv2.threshold(imgray, 80, 255, 0)# 阈值参数要根据情况调整

dilateDst = dilate_demo(thresh)  # 先膨胀消除噪声点
erodeDst = erode_demo(dilateDst)  # 再腐蚀连接断掉的血管
# 均值滤波+二值化抗锯齿
img_mean = cv2.blur(erodeDst, (7, 7))# 核大小要根据情况调整
ret, img_smooth = cv2.threshold(img_mean, 150, 255, 0)# 阈值参数要根据情况调整

# cv2.findContours返回三个值：①处理的图像(image)②轮廓的点集(contours)③各层轮廓的索引(hierarchy)
# contours:存储图片中的轮廓信息，是一个向量，
# 其中每个元素保存了一组由连续的Point点构成的点的集合的向量,
# 每一组Point点集就是一个轮廓，有多少轮廓，向量contours就有多少元素
preImage, contours, hierarchy = cv2.findContours(img_smooth, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# preImage, contours, hierarchy = cv2.findContours(img_smooth, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# 创建显示轮廓的背景
background = np.zeros((img.shape[0], img.shape[1], 3))
background.fill(255)

# 绘制独立轮廓cv2.drawContour()
# 第一个参数是指明在哪幅图像上绘制轮廓；image为三通道才能显示轮廓
# 第二个参数是轮廓本身，在Python中是一个list;
# 第三个参数指定绘制轮廓list中的哪条轮廓，如果是-1，则绘制其中的所有轮廓。
# 后面的参数很简单。其中thickness表明轮廓线的宽度，如果是-1（cv2.FILLED），则为填充模式。
# img_contours = cv2.drawContour(img,contours,-1,(0,255,0),3)
# 但是大多数时候，下面方法更有用
img_contour = cv2.drawContours(background, contours, 1, (255, 0, 0), 1)
print(len(contours))

cv2.imshow('thresh', thresh)
# cv2.imshow('dilateDst', dilateDst)
# cv2.imshow('erodeDst', erodeDst)
cv2.imshow('img_smooth', img_smooth)
cv2.imshow('img_contour', img_contour)
points = []
# print(contours[1])
# 这里contours[1]是轮廓，index参数要根据情况调整
for item in contours[1]:
    points.append(item[0].tolist())
    # print(item[0])
print(points)
writePoints(points)


cv2.waitKey(0)  # 等待键盘输入，不输入 则无限等待
cv2.destroyAllWindows()  # 清除所有窗口
