import json


class VesselTree:
    def __init__(self, rootObj):
        self.key = rootObj  # 随便的名字
        self.data = 0  # 血管半径
        self.children = []  # 所有孩子血管
        self.line = []  # 血管关键点数据
        self.ind = 0  # 指向孩子的下标

    def insertChild(self, newChild):
        self.children.append(newChild)
        length = len(self.children)
        for item in self.children:
            item.data = self.data / length

    def getRootVal(self):
        return self.key

    def getRootLine(self):
        return self.line

    def getChild(self):
        return self.children

    def getRootData(self):
        return self.data

    def setRootVal(self, obj):
        self.key = obj

    def setRootData(self, num):
        self.data = num

    def setRootLine(self, array):
        self.line = array


# 定义一个转换函数，将Tree类换成json可以接受的类型
def tree2dict(t):
    return {
        # 'key': t.rootObj,
        'data': t.data,
        'children': t.children.copy(),
        'line': t.line.copy(),
        'ind': t.ind
    }


if __name__ == '__main__':
    f = open('../json/keyPoint.json')
    # 将json格式的数据映射成list的形式
    t = json.load(f)
    print(t[0])

    # 将所有的线条数据转换成血管对象
    tree = []
    for item in t:
        node = VesselTree('node')
        node.setRootLine(item)
        tree.append(node)
    print(len(tree))

    # 设置血管总支的半径
    tree[0].data = 20
    for pre in tree:
        for item in tree:
            # 检测血管段首尾相接的状况
            # 如果a段血管尾部与b段血管首部位置相同，则将a设为b的子血管
            if item.line[0] == pre.line[len(pre.line) - 1]:
                pre.children.append(item)

    for item in tree:
        for kid in item.children:
            # 设置血管半径为父血管均值
            kid.data = item.data / len(item.children)


