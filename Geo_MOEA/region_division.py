#!/usr/bin/env python
import numpy as np
import random
import math
import matplotlib.pyplot as plt
Set = []
def get_data(file):
    f = open(file,'r')
    data = []
    max_x = 0
    max_y = 0
    min_x=10000
    min_y=10000
    for line in f.readlines():
        da = line.strip().split(',')
        n_x = float(da[0])
        n_y = float(da[1])
        # if n_x>2000 and n_x<4000 and n_y>2000 and n_y<4000:
        data.append([n_x,n_y])
    # print(data)
    return data
def draw(dataset):
    x = []
    y = []
    for data in dataset:
        x.append(data[0])
        y.append(data[1])
    plt.scatter(x,y)
    plt.show()

def draw_1(Sets):
    colors = ['red','blue','dimgray','green','darkturquoise','#FF33CC','#9900CC','darkcyan','indigo','goldenrod','slategray','cornflowerblue','black','olive','pink','sienna']
    # colors = ['red','blue','black','green']
    i=0
    max_x = 0
    count = 0
    for dataset in Sets:
        x = []
        y = []

        for data in dataset:
            x.append(data[0])
            y.append(data[1])
            if max_x<data[0]:
                max_x = data[0]
        # temp = random.randint(0,len(colors)-1)
        c=colors[i]
        i+=1
        # if count < 7:
        #     plt.plot([max_x+0.5,max_x+0.5],[0,23],linestyle=':',c='darkcyan',linewidth = 1.5)
        plt.scatter(x, y,color = c,s=40,alpha=0.5,cmap="viridis",edgecolors='white')
        plt.xticks(())
        plt.yticks(())
        # plt.xlim(0,63)
        # plt.ylim(0,23)
        count +=1
    for set in Sets:
        max_y = 0
        max_x = 0
        min_y = 1000
        min_x = 1000
        for data in set:
            x = data[0]
            y = data[1]
            if max_x<x:
                max_x = x
            if max_y <y:
                max_y=y
            if min_y >y:
                min_y = y
            if min_x>x:
                min_x= x
        # if max_x < 148 and min_x < 6:
        #     plt.plot([max_x+0.5,max_x+0.5],[min_y,max_y],c='yellow',linewidth = 2)
        #     plt.plot([0,max_x],[max_y,max_y],c='yellow',linewidth = 2)
        print("min:",min_x,min_y)
        print("max:",max_x,max_y)
    plt.show()
    # pic_save = plt.gcf()
    # pic_save.savefig('./dataset.eps', format='eps', bbox_inches='tight', dpi=1000)

def compute(data):
    max_x = 0
    max_y = 0
    min_x= 10000
    min_y= 10000
    for da in data:
        n_x = float(da[0])
        n_y = float(da[1])
        if n_x < 0 or n_y < 0:
            continue
        if max_x < n_x:
            max_x = n_x
        if min_x > n_x:
            min_x = n_x
        if max_y < n_y:
            max_y = n_y
        if min_y > n_y:
            min_y = n_y
    # print('max_x: ', max_x)
    # print('max_y: ', max_y)
    # print('min_x: ', min_x)
    # print('min_y: ', min_y)
    length = max_x - min_x
    width = max_y - min_y
    return length,width,max_x,max_y,min_x,min_y
def divison(dataset,max1,min1,max2,min2,length,width,flag,count,Deep):
    L = len(dataset)
    Set_1 = []
    Set_2 = []
    if flag == 0:
        mid = (min1 + max1) / 2
        while True:
            j=0
            Set_1 = []
            Set_2 = []
            while True:
                if dataset[j][0] <= mid:
                    Set_1.append(dataset[j])
                else:
                    Set_2.append(dataset[j])
                j+=1
                if j>=L:
                    break
            l1 = len(Set_1)
            l2 = len(Set_2)
            if abs(l1 - l2) <=5:
                break
            if l1>l2:
                mid -= 0.05
            else:
                mid += 0.05
    if flag == 1:
        mid = (min1 + max1) / 2
        while True:
            Set_1 = []
            Set_2 = []
            j=0
            while True:
                if dataset[j][1] <= mid:
                    Set_1.append(dataset[j])
                else:
                    Set_2.append(dataset[j])
                j+=1
                if j>=L:
                    break
            l1 = len(Set_1)
            l2 = len(Set_2)
            if abs(l1-l2)<=5:
                break
            if l1>l2:
                mid -= 0.05
            else:
                mid += 0.05
    # for f in range(min1,max1+1):
    #     for s in range(min2,max2+1):
    #         if count < (L//2):
    #             if flag == 0:
    #                 print(1)
    #                 if [float(f),float(s)] in dataset:
    #                     Set_1.append([float(f),float(s)])
    #                     count +=1
    #             else:
    #                 if [float(s),float(f)] in dataset:
    #                     Set_1.append([float(s),float(f)])
    #                     count +=1
    #         else:
    #             if flag == 0:
    #                 if [float(f), float(s)] in dataset:
    #                     Set_2.append([float(f), float(s)])
    #                     count += 1
    #             else:
    #                 if [float(s), float(f)] in dataset:
    #                     Set_2.append([float(s), float(f)])
    #                     count += 1
    # print(len(Set_1),Set_1)
    # print(len(Set_2), Set_2)
    return Set_1,Set_2
def huafen(dataset,count,Deep):
    if count == Deep:
        Set.append(dataset)
        return
    length, width, max_x, max_y, min_x, min_y = compute(dataset)
    if length > width:
        Set_1, Set_2 = divison(dataset, int(max_x), int(min_x), int(max_y), int(min_y),length, width,0,count,Deep)
    else:
        Set_1, Set_2 = divison(dataset,int(max_x), int(min_x), int(max_y), int(min_y),length, width,1,count,Deep)
    count +=1
    # print('111')
    huafen(Set_1,count,Deep)
    huafen(Set_2,count,Deep)
    return Set
if __name__ == '__main__':
    n = 50
    count = 0
    dataset = get_data('./data_gowalla.txt')
    N = len(dataset)
    print(N,dataset)
    Deep = math.floor(math.log2(N / n))
    print("Deep:",Deep)
    draw(dataset)
    # print(N)
    Set = huafen(dataset,count,Deep)
    print(Set)
    for set in Set:
        print(len(set))
    print(len(Set[0]),Set[0]) #6
    # print(len(Set[0]),Set[0])#没有8 9
    # draw(Set[13])
    # print(len(Set))
    draw_1(Set)
    # for set in Set:
    #     print(SC1._min_cycle(set))







