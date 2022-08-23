import numpy as np
import cv2
import json
import time


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


# 目标处理
def findTarget(image):
    imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 80, 255, 0)
    dilateDst = dilate_demo(thresh)
    erodeDst = erode_demo(dilateDst)
    img_mean = cv2.blur(erodeDst, (7, 7))
    ret, img_smooth = cv2.threshold(img_mean, 150, 255, 0)
    dst = 255 - img_smooth  # 图像黑白翻转
    return dst


def morph_find(image):
    # cv2.threshold:第一个原图像，第二个进行分类的阈值，第三个是高于（低于）阈值时赋予的新值，第四个是一个方法选择参数
    # 高于0就赋值255：表示不是黑色就赋值为白色
    #  cv2.THRESH_BINARY（黑白二值）
    ret, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY)
    # cv2.getStructuringElement:第一个参数表示内核的形状,第二和第三个参数分别是内核的尺寸以及锚点的位置
    # 交叉形：MORPH_CROSS;
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    finished = False
    size = np.size(binary)
    skeleton = np.zeros(binary.shape, np.uint8)
    while (not finished):
        eroded = cv2.erode(binary, kernel)  # 腐蚀
        temp = cv2.dilate(eroded, kernel)  # 膨胀
        temp = cv2.subtract(binary, temp)  # 相减
        skeleton = cv2.bitwise_or(skeleton, temp)  # 按位或
        binary = eroded.copy()

        # 对二值化图像执行countNonZero。可得到非零像素点数.
        zeros = size - cv2.countNonZero(binary)
        if zeros == size:
            finished = True

    #  cv2.RETR_EXTERNAL     表示只检测外轮廓
    #  cv2.CHAIN_APPROX_NONE 存储所有的轮廓点，相邻的两个点的像素位置差不超过1
    #  cv2.CHAIN_APPROX_SIMPLE 压缩水平方向，垂直方向，对角线方向的元素，只保留该方向的终点坐标，例如一个矩形轮廓只需4个点来保存轮廓信息
    preImage, contours, hierarchy = cv2.findContours(skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # preImage, contours, hierarchy = cv2.findContours(skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # hierarchy后一个轮廓、前一个轮廓、父轮廓、内嵌轮廓的索引编号，如果没有对应项，则该值为负数。
    # print(hierarchy)

    background = np.zeros((img.shape[0], img.shape[1], 3))
    background.fill(255)
    img_contour = cv2.drawContours(background, contours, -1, (0, 0, 255), 1, 8)
    # cv2.imshow("img_contour", img_contour)
    # time.sleep(1)
    # for index in range(1,len(contours)):
    #     img_contour = cv2.drawContours(img_contour, contours, index, (0, 0, 255), 1, 8)
    #     cv2.imshow("img_contour", img_contour)
    #     time.sleep(1)


    contourLine = [len(contours)]
    for index in range(len(contours)):
        temp = []
        for line in contours[index]:
            temp.append(line[0].tolist())
            # print(line)
        contourLine.append(temp)
    # print(contourLine)
    filename = '../json/contourLine.json'
    with open(filename, 'w') as file_obj:
        json.dump(contourLine, file_obj)
    return img_contour

if __name__ == '__main__':
    img = cv2.imread("../image/vessel.jpg")
    target = findTarget(img)
    dstLine = morph_find(target)
    cv2.imshow("dstLine", dstLine)

    cv2.waitKey(0)  # 等待键盘输入，不输入 则无限等待
    cv2.destroyAllWindows()  # 清除所以窗口
