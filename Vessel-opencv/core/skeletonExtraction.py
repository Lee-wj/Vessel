import cv2
from skimage import morphology
import numpy as np
import json
import sys

sys.path.append('')
from core.d_treeStorage import *


# 膨胀
def dilate_demo(img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))  # 定义结构元素的形状和大小
    dst = cv2.dilate(img, kernel)  # 膨胀操作
    return dst

# 腐蚀
def erode_demo(img):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))  # 定义结构元素的形状和大小
    dst = cv2.erode(img, kernel)  # 腐蚀操作
    return dst

# 图像预处理
def smooth_demo(img):
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # cv2.threshold (源图片, 阈值, 填充色, 阈值类型)灰度值大于50赋值255，反之0
    # 返回值：输入的thresh值，处理后的图像
    ret, thresh = cv2.threshold(imgray, 80, 255, 0)  # 阈值参数要根据情况调整

    dilateDst = dilate_demo(thresh)  # 先膨胀消除噪声点
    erodeDst = erode_demo(dilateDst)  # 再腐蚀连接断掉的血管
    # 均值滤波+二值化抗锯齿
    img_mean = cv2.blur(erodeDst, (7, 7))  # 核大小要根据情况调整
    ret, img_smooth = cv2.threshold(img_mean, 150, 255, 0)  # 阈值参数要根据情况调整

    dst = 255 - img_smooth  # 图像黑白翻转
    return dst

# 提取骨架
def skeleton_demo(img):
    img[img == 255] = 1
    skeleton0 = morphology.skeletonize(img)  # 骨架提取
    skeleton = skeleton0.astype(np.uint8) * 255
    return skeleton
    # print(skeleton)

# 计算邻接点
def compNeighs(point):
    top = [point[0], point[1] - 1]
    top_left = [point[0] - 1, point[1] - 1]
    top_right = [point[0] + 1, point[1] - 1]
    left = [point[0] - 1, point[1]]
    right = [point[0] + 1, point[1]]
    bottom = [point[0], point[1] + 1]
    bottom_left = [point[0] - 1, point[1] + 1]
    bottom_right = [point[0] + 1, point[1] + 1]
    neighs = [top, top_left, top_right, left, right, bottom, bottom_left, bottom_right]
    return neighs

#   搜索交叉点，起始点，结束点算法
def findIntersection(pos, img_skeleton, intersec, se):
    for point in pos:
        # count用来记录每个点的邻接点有几个
        count = 0
        neighs = compNeighs(point)
        for item in neighs:
            if img_skeleton[item[0]][item[1]] == 255:
                count += 1
        # 交叉点存储
        if count >= 3:
            intersec.append(point)
        # 删除冗余
        for i in range(len(intersec)):
            for j in range(i + 1, len(intersec)):
                if ((intersec[i][0] - 10) <= intersec[j][0] <= (intersec[i][0] + 10)) and ((intersec[i][1] - 10) <=
                                                                                           intersec[j][1] <= (
                                                                                                   intersec[i][
                                                                                                       1] + 10)):
                    intersec.remove(intersec[j])

        # 存储开始和结束点
        if count == 1:
            se.append(point)


allBranch = []
# 血管分段算法
def procP(point, branch, allKey, visited):
    branch.append(point)
    visited[point[0]][point[1]] = True
    neighs = compNeighs(point)
    for item in neighs:
        if (img_skeleton[item[0]][item[1]] == 255) and (visited[item[0]][item[1]] == False):
            if item in allKey:
                branch.append(item)
                visited[item[0]][item[1]] = True
                allBranch.append(branch.copy())
                branch.clear()
            else:
                procP(item, branch, allKey, visited)


if __name__ == '__main__':
    img = cv2.imread("../image/vessel.jpg")
    img_smooth = smooth_demo(img)
    img_skeleton = skeleton_demo(img_smooth)

    # 将骨架上所有点保存在数组中
    pos = []
    size = img_skeleton.shape
    for i in range(0, size[0]):
        for j in range(0, size[1]):
            if (img_skeleton[i][j] == 255):
                pos.append([i, j])
    pos.sort(key=lambda x: x[1])
    # 保存骨架文件
    f = '../json/skeletonFinal.json'
    with open(f, 'w') as file_obj:
        json.dump(pos, file_obj)

    # 交叉点、起始点、结束点提取
    intersec = []  # 交叉点
    se = []  # 开始和结束点
    findIntersection(pos, img_skeleton, intersec, se)

    # 血管分段
    # keyP中包含起始点和交叉点，se中包含结束点
    # allKey包含所有交叉点，起始点，结束点
    allKey = intersec.copy()
    allKey.extend(se)
    keyP = intersec.copy()
    # key=lambda x: x[1]按第二维排序，则第一个点为开始点
    se.sort(key=lambda x: x[1])
    keyP.append(se[0])
    keyP.sort(key=lambda x: x[1])
    se.remove(se[0])
    # 对于交叉点和起始点计算分支
    branch = []
    # 初始化一个图片大小的数组，初始值为false
    visited = [[False for col in range(size[1])] for row in range(size[0])]
    for item in keyP:
        procP(item, branch, allKey, visited)

    # 保存所有分支
    fb = '../json/branches.json'
    with open(fb, 'w') as file_obj:
        json.dump(allBranch, file_obj)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
