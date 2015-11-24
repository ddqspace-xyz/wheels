# -*-encoding=utf8 -*-
# Author :        Liu Dongqiang
# Email :         1047400998@@qq.com
#
# Created at :    2015-11-23 19:20
#
# Filename :      difftree.py
# Desc :          比较两个目录结构，对于相同部分比较文件内容
#                 <最长公共子序列>
#


import sys
import os

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    @classmethod
    def print_green(self, s):
        print (colors.OKGREEN + s + colors.ENDC)

    @classmethod
    def print_red(self, s):
        print (colors.FAIL + s + colors.ENDC)

    @classmethod
    def print_pink(self, s):
        print (colors.HEADER + s + colors.ENDC)

# longest common list
def lcl(list1, list2, len1, len2):
    def sub_list_indexs(b, list1, len1, len2):
        i = len1
        j = len2
        indexs1 = []
        indexs2 = []
        res = []
        while not (i == 0 or j == 0):
            if b[i][j] == 0:
                indexs1.append(i-1)
                indexs2.append(j-1)
                i -= 1
                j -= 1
            elif b[i][j] == -1:
                j -= 1
            else:
                i -= 1
        # list1的下标
        indexs1.reverse()
        indexs2.reverse()
        return indexs1, indexs2

    rect = [([0] * (len2+1)) for i in range(len1+1)]
    b = [([0] * (len2+1)) for i in range(len1+1)]
    for i in xrange(1, len1+1):
        for j in xrange(1, len2+1):
            if list1[i-1] == list2[j-1]:
                rect[i][j] = rect[i-1][j-1] + 1
                b[i][j] = 0
            elif rect[i-1][j] >= rect[i][j-1]:
                rect[i][j] = rect[i-1][j]
                b[i][j] = 1
            else:
                rect[i][j] = rect[i][j-1]
                b[i][j] = -1

    indexs1, indexs2 = sub_list_indexs(b, list1, len1, len2)
    return indexs1, indexs2

# 遍历
def walk(d):
    res = []
    for root, dirs, files in os.walk(d):
        # 忽略隐藏文件
        # we are replacing the elements in dirs and not the list refer by dirs
        dirs[:] = [d for d in dirs if not d[0] == '.']
        files = [f for f in files if not f[0] == '.']
        for f in files:
            f = os.path.join(root, f)
            res.append(f)
    # 返回路径列表
    return res

# 输出对比结果
def print_res(list1, list2, indexs1, indexs2):
    def myprint(subtr_res, plus_res):
        # 第一个列表独有的行 视为减行
        for line in subtr_res:
            s = '< %s' % line.rstrip()
            colors.print_red(s)

        # 第二个列表独有的行 视为加行
        for line in plus_res:
            s = '> %s' % line.rstrip()
            colors.print_green(s)

    if not indexs1:
        subtr_res = list1
        plus_res = list2
        myprint(subtr_res, plus_res)

    pre_index1 = 0 # list1当前输出子列表的前下标
    pre_index2 = 0 # list2当前输出子列表的前下标

    for index1, index2 in zip(indexs1, indexs2):
        subtr_res = list1[pre_index1:index1]
        plus_res = list2[pre_index2:index2]
        pre_index1 = index1 + 1
        pre_index2 = index2 + 1

        # 最后一个index匹配完后 输出list1, list2剩余的行
        if index1 == indexs1[-1]:
            subtr_res.extend(list1[pre_index1:])
            plus_res.extend(list2[pre_index2:])
            myprint(subtr_res, plus_res)
        else:
            myprint(subtr_res, plus_res)
            print list1[index1].rstrip()

# 将路径始目录（不同）部分去除
def wipe_basic_root(l, root):
    root_len = len(root)
    res = []
    for line in l:
        line = line[root_len:]
        res.append(line)
    return res

def main(argv):
    if not len(argv) == 3:
        print 'usage: python difftree.py <dir1> <dir2>'
        exit(1)

    def format_dir(d):
        # 规范路径字符串
        if d[-1] != '/':
            d += '/'
        return d

    dir1 = argv[1]
    dir1 = format_dir(dir1)
    list1 = walk(dir1)
    list1 = wipe_basic_root(list1, dir1)

    dir2 = argv[2]
    dir2 = format_dir(dir2)
    list2 = walk(dir2)
    list2 = wipe_basic_root(list2, dir2)

    len1 = len(list1)
    len2 = len(list2)

    # 输出目录的相同的以及不同的
    info = '    目录结构差异    '
    colors.print_pink('%s%s%s' % ('='*25, info, '='*25))
    indexs1, indexs2 = lcl(list1, list2, len1, len2)
    print_res(list1, list2, indexs1, indexs2)

    # 取相同部分的文件比较
    for index in indexs1:
        rltv_path = list1[index]
        f1 = os.path.join(dir1, rltv_path)
        f2 = os.path.join(dir2, rltv_path)

        print
        colors.print_pink('='*50)
        colors.print_pink('%s    VS    %s' % (f1, f2))
        print

        f1 = open(f1, 'r')
        content1 = f1.readlines()
        f2 = open(f2, 'r')
        content2 = f2.readlines()
        len1 = len(content1)
        len2 = len(content2)
        indexs1, indexs2 = lcl(content1, content2, len1, len2)

        print_res(content1, content2, indexs1, indexs2)

if __name__ == '__main__':
    main(sys.argv)
