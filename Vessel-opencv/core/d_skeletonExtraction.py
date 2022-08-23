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


def skeleton_demo(img):
    img[img == 255] = 1
    skeleton0 = morphology.skeletonize(img)  # 骨架提取
    skeleton = skeleton0.astype(np.uint8) * 255
    return skeleton
    # print(skeleton)


def store_demo(contours):
    contourLine = [len(contours)]
    for index in range(len(contours)):
        temp = []
        for line in contours[index]:
            temp.append(line[0].tolist())
            # print(line)
        contourLine.append(temp)
    # print(contourLine)
    filename = '../json/skeleton.json'
    with open(filename, 'w') as file_obj:
        json.dump(contourLine, file_obj)


def mouse(event, x, y, flags, param):
    global root, father, tree

    # 左键在截面绘制标记点并存入当前血管关键点集
    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        cv2.circle(img_contour, (x, y), 1, (0, 255, 0), thickness=-1)
        cv2.putText(img_contour, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                    1.0, (0, 255, 0), thickness=1)
        pos.append([x, y])
        print(pos)
        cv2.imshow("img_contour", img_contour)

    # 右键表示当前血管关键点提取完毕，新建一个树节点存储该段血管，并开始一段新血管
    if event == cv2.EVENT_RBUTTONDOWN:
        lines.append(pos.copy())
        node = VesselTree('node')
        node.setRootLine(pos.copy())
        tree.append(node)
        # if root is None:
        #     root = node
        #     node.setRootData(25)
        # else:
        #     root.insertChild(node)
        pos.clear()
        print(lines)
        print(tree)

    # # 滚轮表示切换血管树的根(失败)
    # if event == cv2.EVENT_MBUTTONDOWN:
    #     if father is None:
    #         father = root
    #     else:
    #         if father.ind < len(father.children):
    #             root = father.children[father.ind]
    #             father.ind = father.ind + 1
    #         else:
    #             father = father.children[0]
    #             root = father.children[0]


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


#   搜索交叉点算法
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


# 对于交叉点和起始点
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
    # 平滑图像
    img_smooth = smooth_demo(img)

    # 提取骨架
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
    f = '../json/skeleton_1.json'
    with open(f, 'w') as file_obj:
        json.dump(pos, file_obj)

    # 交叉点、起始点、结束点提取
    intersec = []  # 存储交叉点
    se = []  # 存储开始和结束点
    findIntersection(pos, img_skeleton, intersec, se)

    # 血管分段
    # keyP中包含起始点和交叉点，se中包含结束点
    allKey = intersec.copy()
    allKey.extend(se)
    print(allKey)
    keyP = intersec.copy()
    se.sort(key=lambda x: x[1])
    keyP.append(se[0])
    keyP.sort(key=lambda x: x[1])
    se.remove(se[0])
    # 对于交叉点和起始点计算分支
    branch = []
    visited = [[False for col in range(size[1])] for row in range(size[0])]
    for item in keyP:
        procP(item, branch, allKey, visited)

    fb = '../json/branchs.json'
    with open(fb, 'w') as file_obj:
        json.dump(allBranch, file_obj)

    preImage, skeletons, hierarchy = cv2.findContours(img_skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    background = np.zeros((img.shape[0], img.shape[1], 3))
    background.fill(255)
    img_contour = cv2.drawContours(background, skeletons, -1, (0, 0, 255), 1, 8)
    # print(img_contour)

    cv2.imwrite("../image/skeleton.png", img_contour)

    store_demo(skeletons)

    # 鼠标监听
    # cv2.namedWindow("img_contour")
    # cv2.imshow('img_contour', img_contour)
    # cv2.setMouseCallback("img_contour", mouse)

    # 多条轴线
    lines = []
    # 单条轴线
    pos = []

    # q将所有血管关键点数据存入json文件中
    while True:
        k = cv2.waitKey(10) & 0xFF
        if k == ord('q') or k == ord('Q'):
            filename = '../json/keyPoint.json'
            with open(filename, 'w') as file_obj:
                json.dump(lines, file_obj)
            # break
            cv2.destroyAllWindows()

    cv2.destroyAllWindows()
