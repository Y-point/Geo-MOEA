# /usr/bin/env python
# --*--coding:utf-8--*--

import math
import numpy as np
import random

class SC():
    def __init__(self,location_set,first_pro,epsilon,Em):
        self.loc_set = location_set
        self.fir_pro = first_pro
        self.epsilon = epsilon
        self.Em=Em
        self.b=0.5# 噪声尺度

    def distance(self,zi, xh):
        return math.sqrt((zi[0] - xh[0]) ** 2 + (zi[1] - xh[1]) ** 2)

    #指数机制计算发布概率
    def computer_pro(self,loc, sens, epsilon):
        temp = []
        for temp_loc in self.loc_set:
            temp.append(math.exp((epsilon * self.distance(temp_loc, loc)) / (-2 * sens)))
        sum_ = sum(temp)
        rel_pro = [i / sum_ for i in temp]
        return rel_pro

    # 区域外接圆直径
    def _min_cycle(self,set):
        if len(set) <= 1:
            return 0
        elif len(set) == 2:
            return self.distance(set[0], set[1])
        else:
            cur_max = 0
            for i in range(len(set)):
                for j in range(i + 1, len(set)):
                    if self.distance(set[i], set[j]) > cur_max:
                        cur_max = self.distance(set[i], set[j])
            return cur_max

    # 根据划分结构获取区域直径和隐私预算
    def get_sens_ep(self,set, epsilon, Em):
        sens_list = [0 for i in range(len(self.loc_set))]
        ep_list = [0 for i in range(len(self.loc_set))]
        for i in range(len(set)):
            index=[self.loc_set.index(loc) for loc in set[i]]
            # 找到对应的先验概率
            pro = []
            for j in index:
                pro.append(self.fir_pro[j])
            E_fi = self.compute_E_Phi(set[i], pro)
            if E_fi >= math.exp(epsilon) * Em:
                eps_g = epsilon
            else:
                eps_g = epsilon
            D = self._min_cycle(set[i])
            for j in index:
                sens_list[j] = D
                ep_list[j] = eps_g
        return sens_list, ep_list

    #计算后验概率
    def gen_sed_pro(self,x, rel_pro_set):
        temp_list = []
        for i in range(len(self.loc_set)):
            cur_pro = self.fir_pro[i] * rel_pro_set[i][x]
            temp_list.append(cur_pro)
        sum_ = sum(temp_list)
        sed_pro = [i / sum_ for i in temp_list]
        return sed_pro

    #贝叶斯攻击
    def bayesian_gongji(self,sed_pro):
        min_ = self._pro_dis(self.loc_set[0], self.loc_set, sed_pro)
        min_index = 0
        for i in range(len(self.loc_set)):
            cur_min = self._pro_dis(self.loc_set[i], self.loc_set, sed_pro)
            if cur_min < min_:
                min_ = cur_min
                min_index = i
        return self.loc_set[min_index]

    #计算E_fi
    def compute_E_Phi(self,temp_loc_set, temp_fir_pro):
        temp_min = None
        guiyihua_pro = self._guiyihua(temp_fir_pro)
        for loc in self.loc_set:
            cur_min = 0.
            temp_index = self.loc_set.index(loc)
            for i in range(len(temp_loc_set)):
                # if i != temp_index:
                cur_min += guiyihua_pro[i] * self.distance(loc, temp_loc_set[i])
            if temp_min is None:
                temp_min = cur_min
            elif cur_min < temp_min:
                temp_min = cur_min
        return temp_min
    #概率单位化
    def _guiyihua(self,temp_fir_pro):
        sum_ = sum(temp_fir_pro)
        return [i / sum_ for i in temp_fir_pro]
    def _pro_dis(self,cur_loc, location_set, sed_pro):
        sum_ = 0.
        for i in range(len(location_set)):
            sum_ += (sed_pro[i] * self.distance(cur_loc, location_set[i]))
        return sum_
    def global_distace(self,loc, set):
        sum = 0
        for w in set:
            sum += self.distance(loc, w)
        return sum / len(set)

    #Kmeans根据中心点聚类
    def kmeans_once(self,loc_set, mid_array):
        n = len(loc_set)
        k = len(mid_array)
        bag_list = [[] for i in range(k)]
        # 每个位置加入到离他最近的簇中
        # 给每个中心先找两个点进去
        remain_locs = []
        for loc in loc_set:
            remain_locs.append(loc)
        for i in range(k):
            for j in range(2):
                index = np.argmin([self.distance(mid_array[i], remain_loc) for remain_loc in remain_locs])
                bag_list[i].append(remain_locs[index])
                del remain_locs[index]
        for i in range(len(remain_locs)):
            global_distance = []
            for mid in mid_array:
                global_distance.append(self.distance(remain_locs[i], mid))  # 计算出每个点与中心点的距离
            x = np.argmin(global_distance)  # 计算出每个点与中心点的距离的最小值下标
            bag_list[x].append(remain_locs[i])  # 把离中心点距离最小的点加入簇中
        # 更新均值向量
        for i in range(k):
            if len(bag_list[i]) > 0:
                x_bar = 0
                y_bar = 0
                for loc in bag_list[i]:
                    x_bar += loc[0]
                    y_bar += loc[1]
                x_bar /= len(bag_list[i])
                y_bar /= len(bag_list[i])
                mid_array[i] = [x_bar, y_bar]  # 更新中心点
        return bag_list, mid_array  # 返回聚类的结果
    def DPPC(self):#单目标方案
        sens_list,bag_list,center_list=self.QKmeans()
        release_pro_set = []
        for l in range(len(self.loc_set)):
            loc = self.loc_set[l]
            release_pro_set.append(self.computer_pro(loc, sens_list[l], self.epsilon))
        return self.compute_Error(release_pro_set),self.compute_QLoss(release_pro_set),len(bag_list),bag_list,center_list


    # 计算预期推断误差
    def compute_Error(self, release_pro_set):
        # 贝叶斯攻击
        bys_avg = []
        att_bay_loc_list = []
        for i in range(len(self.loc_set)):
            # 计算后验概率
            sed_pro = self.gen_sed_pro(i, release_pro_set)
            # 攻击的位置
            att_bay_loc = self.bayesian_gongji(sed_pro)
            att_bay_loc_list.append(att_bay_loc)

        for loc in self.loc_set:
            loc_index = self.loc_set.index(loc)
            release_pro = release_pro_set[loc_index]
            sum_ = 0
            for i in range(len(self.loc_set)):
                # 计算误差
                sum_ += release_pro[i] * self.distance(loc, att_bay_loc_list[i])
            bys_avg.append(sum_)
        bys_error = 0.
        for i in range(len(self.fir_pro)):
            bys_error += (self.fir_pro[i] * bys_avg[i])
        return bys_error

    # 计算效用损失
    def compute_QLoss(self,release_pro_set):
        # 效用损失
        u_list = []
        for k in range(len(self.loc_set)):  # 真实位置x
            ult_loss = 0
            for i in range(len(self.loc_set)):  # x'
                ult_loss += release_pro_set[k][i] * self.distance(self.loc_set[k], self.loc_set[i])
            u_list.append(ult_loss)
        utility_loss = 0.
        for i in range(len(self.fir_pro)):
            utility_loss += (self.fir_pro[i] * u_list[i])
        return utility_loss

    def judge_EPI(self,set):
        pro=[]
        for loc in set:
            pro.append(self.fir_pro[self.loc_set.index(loc)])
        E_fi=self.compute_E_Phi(set,pro)
        if E_fi>=math.exp(self.epsilon)*self.Em:
            return True
        else:
            return False
    def compute_Sparsity(self,set):#剩余点的稀疏度
        Sparsity=[]
        for i in range(len(set)):
            _sum=0.
            for j in range(len(set)):
                _sum+=self.distance(set[i],set[j])
            Sparsity.append(_sum)
        Sparsity_index=np.argsort(Sparsity)
        Sparsity_index=Sparsity_index[::-1]
        return Sparsity_index

    def kmeans(self,loc_set,mid_array):
        n=len(self.loc_set)
        k=len(mid_array)
        count=0
        while(1):
            sign = [0 for i in range(k)]
            bag_list = [[] for i in range(k)]
            # 每个位置加入到离他最近的簇中
            # 给每个中心先找两个点进去
            remain_locs = []
            surplus_locs=[]
            for loc in loc_set:
                remain_locs.append(loc)
            for i in range(k):
                for j in range(2):
                    # print(i,j)
                    index = np.argmin([self.distance(mid_array[i], remain_loc) for remain_loc in remain_locs])
                    bag_list[i].append(remain_locs[index])
                    # print(remain_locs)
                    del remain_locs[index]
            for i in range(k):#判断先加入的两个点的E_fi
                flag=self.judge_EPI(bag_list[i])
                if flag==True:
                    sign[i]=1
            # print(sign)
            Sparsity_index=self.compute_Sparsity(remain_locs)#稀疏度排序的下标数组
            for i in range(len(remain_locs)):
                global_distance1 = []
                for mid in mid_array:
                    global_distance1.append(self.distance(remain_locs[Sparsity_index[i]], mid))#计算出每个点与中心点的距离
                # x = np.argmin(global_distance1)#计算出每个点与中心点的距离的最小值下标
                x_index1=np.argsort(global_distance1)
                sign_flag=True
                for x in x_index1:
                    if sign[x]==0:
                        bag_list[x].append(remain_locs[Sparsity_index[i]])#把离中心点距离最小的点加入簇中
                        flag = self.judge_EPI(bag_list[x])
                        if flag == True:
                            sign[x] = 1
                        sign_flag=False
                        break
                if sign_flag==True:
                    surplus_locs.append(remain_locs[Sparsity_index[i]])
            # print(len(surplus_locs),sign)
            for i in range(len(surplus_locs)):
                global_distance2 = []
                for mid in mid_array:
                    global_distance2.append(self.distance(surplus_locs[i], mid))#计算出每个点与中心点的距离
                # x = np.argmin(global_distance2)#计算出每个点与中心点的距离的最小值下标
                x_index2=np.argsort(global_distance2)
                for x in x_index2:
                    bag_list[x].append(surplus_locs[i])#把离中心点距离最小的点加入簇中
                    Flag=self.judge_EPI(bag_list[x])
                    if Flag==False:
                        # print(surplus_locs[i])
                        bag_list[x].remove(surplus_locs[i])
                    else:
                        break
            mid_error=0 #计算均值向量更新的幅度
            # 更新均值向量
            # print('pre:',mid_array)
            for i in range(k):
                if len(bag_list[i])>0:
                    x_bar=0
                    y_bar=0
                    for loc in bag_list[i]:
                        x_bar+=loc[0]
                        y_bar+=loc[1]
                    x_bar/=len(bag_list[i])
                    y_bar/=len(bag_list[i])
                    mid_error+=self.distance(mid_array[i],[x_bar,y_bar])
                    mid_array[i]=[x_bar,y_bar]#更新中心点

            # print('later:',mid_array)
            # print(mid_error)
            if(mid_error<0.5):
                break
            count+=1
            if count>50:
                break
        return bag_list,mid_array,sum(sign)==k#返回聚类的结果
    def kmeans1(self,loc_set,mid_array):
        n=len(self.loc_set)
        k=len(mid_array)
        count=0
        sign = [0 for i in range(k)]
        bag_list = [[] for i in range(k)]
        # 每个位置加入到离他最近的簇中
         # 给每个中心先找两个点进去
        remain_locs = []
        surplus_locs=[]
        for loc in loc_set:
            remain_locs.append(loc)
        for i in range(k):
            for j in range(2):
                # print(i,j)
                index = np.argmin([self.distance(mid_array[i], remain_loc) for remain_loc in remain_locs])
                bag_list[i].append(remain_locs[index])
                # print(remain_locs)
                del remain_locs[index]
        for i in range(k):#判断先加入的两个点的E_fi
            flag=self.judge_EPI(bag_list[i])
            if flag==True:
                sign[i]=1
        # print(sign)
        Sparsity_index=self.compute_Sparsity(remain_locs)#稀疏度排序的下标数组
        for i in range(len(remain_locs)):
            global_distance1 = []
            for mid in mid_array:
                global_distance1.append(self.distance(remain_locs[Sparsity_index[i]], mid))#计算出每个点与中心点的距离
            # x = np.argmin(global_distance1)#计算出每个点与中心点的距离的最小值下标
            x_index1=np.argsort(global_distance1)
            sign_flag=True
            for x in x_index1:
                if sign[x]==0:
                    bag_list[x].append(remain_locs[Sparsity_index[i]])#把离中心点距离最小的点加入簇中
                    flag = self.judge_EPI(bag_list[x])
                    if flag == True:
                        sign[x] = 1
                    sign_flag=False
                    break
            if sign_flag==True:
                surplus_locs.append(remain_locs[Sparsity_index[i]])
        # print(len(surplus_locs),sign)
        for i in range(len(surplus_locs)):
            global_distance2 = []
            for mid in mid_array:
                global_distance2.append(self.distance(surplus_locs[i], mid))#计算出每个点与中心点的距离
            # x = np.argmin(global_distance2)#计算出每个点与中心点的距离的最小值下标
            x_index2=np.argsort(global_distance2)
            for x in x_index2:
                bag_list[x].append(surplus_locs[i])#把离中心点距离最小的点加入簇中
                Flag=self.judge_EPI(bag_list[x])
                if Flag==False:
                    # print(surplus_locs[i])
                    bag_list[x].remove(surplus_locs[i])
                else:
                    break
        # mid_error=0 #计算均值向量更新的幅度
        # # 更新均值向量
        # print('pre:',mid_array)
        for i in range(k):
            if len(bag_list[i])>0:
                x_bar=0
                y_bar=0
                for loc in bag_list[i]:
                    x_bar+=loc[0]
                    y_bar+=loc[1]
                x_bar/=len(bag_list[i])
                y_bar/=len(bag_list[i])
                # mid_error+=self.distance(mid_array[i],[x_bar,y_bar])
                mid_array[i]=[x_bar,y_bar]#更新中心点

        # print('later:',mid_array)
        # print(mid_error)
        # if(mid_error<0.5):
        #     break
        # count+=1
        # if count>50:
        #     break
        return bag_list,mid_array,sum(sign)==k#返回聚类的结果

    # kmeans自适应聚类，聚成k个类
    def Kmeans_adaptive(self):
        work_list = self.loc_set[:]
        work_pro_list = self.fir_pro[:]
        n = len(work_list)
        sens_list = [0 for ii in range(n)]
        bag_list = []
        bag = []
        pro = []
        index = []
        Efi = 0
        while(len(work_list)>0):
            while((len(bag)<2 or (len(bag)>=2 and Efi<math.exp(self.epsilon)*self.Em)) and len(work_list)>0):
                if(len(bag)==0):
                    global_distance = []
                    for w in work_list:
                        global_distance.append(self.global_distace(w, work_list))
                    x = np.argmax(global_distance)
                else:
                    global_distance = []
                    for w in work_list:
                        global_distance.append(self.global_distace(w, bag))
                    x = np.argmin(global_distance)
                bag.append(work_list[x])
                pro.append(work_pro_list[x])
                index.append(self.loc_set.index(work_list[x]))
                del work_list[x]
                del work_pro_list[x]
                if(len(bag)==1):Efi=0
                else:
                    Efi = self.compute_E_Phi(bag, pro)
            if(len(work_list)>0):
                Dfi=self._min_cycle(bag)
                for k in index:
                    sens_list[k] = Dfi
                bag_list.append(index)
                bag = []
                pro = []
                index = []
                Efi=0
            else:
                break
        # 剩余的点逐个加入最近的簇
        if(len(bag)>0):
            remain_bag=[]
            remain_pro=[]
            remain_index=[]
            while (len(bag) > 0):
                cur_loc = bag[0]
                cur_pro = pro[0]
                cur_index = index[0]
                bag_list.sort(key=lambda x: self.global_distace(cur_loc, [self.loc_set[l] for l in x]))
                flag=0
                for bbag in bag_list:
                    temp_bag = [self.loc_set[l] for l in bbag]
                    temp_bag.append(cur_loc)
                    temp_pro = [self.fir_pro[p] for p in bbag]
                    temp_pro.append(cur_pro)
                    temp_index=bbag[:]
                    temp_index.append(cur_index)
                    Efi = self.compute_E_Phi(temp_bag, temp_pro)
                    if (Efi >= math.exp(self.epsilon)*self.Em):
                        flag=1
                        bag_list[bag_list.index(bbag)].append(cur_index)
                        Dfi = self._min_cycle(temp_bag)
                        for k in bag_list[bag_list.index(bbag)]:
                            sens_list[k] = Dfi
                        del bag[0]
                        del pro[0]
                        del index[0]
                        break
                if flag==0:
                    remain_bag.append(cur_loc)
                    remain_pro.append(cur_pro)
                    remain_index.append(cur_index)
                    del bag[0]
                    del pro[0]
                    del index[0]

            #概率极小，某个点加入任何一个簇都会导致不等式不满足，那么融合
            if len(remain_bag)>0:
                cur_loc=[sum(remain_bag[:][0])/len(remain_bag),sum(remain_bag[:][1])/len(remain_bag)]
                bag_list.sort(key=lambda x: self.global_distace(cur_loc, [self.loc_set[l] for l in x]))
                Efi=0
                # print(bag_list
                while (Efi < math.exp(self.epsilon)*self.Em):
                    # print Efi,math.exp(self.epsilon)*self.Em,bag_list
                    for i in range(len(bag_list[0])):
                        x = bag_list[0][i]
                        remain_bag.append(self.loc_set[x])
                        remain_pro.append(self.fir_pro[x])
                        remain_index.append(x)
                    Efi = self.compute_E_Phi(remain_bag, remain_pro)
                    del bag_list[0]
                Dfi = self._min_cycle(remain_bag)
                for k in remain_index:
                    sens_list[k] = Dfi
                bag_list.append(remain_index)
        # print bag_list
        return sens_list,bag_list

    def get_Dji_list(self,remain_loc_list,center_list,full,full_flag):
        k=len(center_list)
        Dji_list = [[] for i in range(len(remain_loc_list))]
        for i in range(len(remain_loc_list)):
            min_d = 999
            min_loc = []
            min_bag_index = 0
            for j in range(k):
                if full[j] == full_flag:
                    # without weight
                    Dji = self.distance(remain_loc_list[i], center_list[j])
                    if Dji < min_d:
                        min_d = Dji
                        min_loc = remain_loc_list[i]
                        min_bag_index = j
            Dji_list[i] = [min_loc, min_bag_index, min_d]
        # sort by min_d
        Dji_list.sort(key=lambda x: x[2])
        return Dji_list


    def QKmeans(self):
        useless,index_list=self.Kmeans_adaptive()
        n=len(self.loc_set)
        k=len(index_list)
        old_bag_list = [[] for i in range(k)]
        for i in range(k):
            for index in index_list[i]:
                old_bag_list[i].append(self.loc_set[index])
        satisfied_fi=old_bag_list
        del old_bag_list
        satisfied_fi_D=0
        for i in range(k):
            satisfied_fi_D+=self._min_cycle(satisfied_fi[i])
        satisfied_fi_D=satisfied_fi_D/k
        satisfied_fi_list = [satisfied_fi]
        satisfied_fi_D_list = [satisfied_fi_D]
        # init center_list and sparse_list
        # print 'init',k,satisfied_fi_D,satisfied_fi
        flag=1 # represent find a satisfied fi or not under k
        last_flag = 0 # represent the last circle, circle_num change to the largest
        max_sampling_num=100
        while(last_flag==1 or (last_flag==0 and flag==1)):
            flag = 0
            # print "k",k
            sampling_num=0
            while(sampling_num<max_sampling_num):
                circle_num=0 # the repeat num of ths algorithm
                # init the center_list
                center_list = []
                r = np.random.choice(len(self.loc_set))
                temp=self.loc_set[:]
                center_list.append(self.loc_set[r])
                del temp[r]
                while (len(center_list) < k):
                    temp.sort(key=lambda x:self.distance(center_list[-1],x))
                    temp_dis=[self.distance(center_list[-1],temp[item]) for item in range(len(temp))]
                    temp_pro=[temp_dis[item]/sum(temp_dis) for item in range(len(temp))]
                    r=np.random.random()
                    pro_sum=0
                    for i in range(len(temp)):
                        pro_sum+=temp_pro[i]
                        if pro_sum>=r:break
                    center_list.append(temp[i-1])
                    del temp[i-1]
                while circle_num<50:
                    # input bag_list,pro_list,remain_loc_list,sparse_list,center_list
                    remain_loc_list = self.loc_set[:]
                    remain_index_list=[i for i in range(n)]
                    bag_list = [[] for i in range(k)]
                    pro_list = [[] for i in range(k)]
                    index_list = [[] for i in range(k)]
                    # the ith bag is full or not
                    full = [0 for f in range(k)]
                    # add the closest loc to each bag
                    for ss in range(k):
                        index=np.argmin([self.distance(center_list[ss],remain_loc_list[item]) for item in range(len(remain_loc_list))])
                        closest_loc=remain_loc_list[index]
                        bag_list[ss].append(closest_loc)
                        pro_list[ss].append(self.fir_pro[remain_index_list[index]])
                        index_list[ss].append(remain_index_list[index])
                        del remain_loc_list[index]
                        del remain_index_list[index]
                    # print 'circle_num',circle_num
                    # print 'center_list',center_list
                    # print 'bag_list',bag_list
                    # print 'pro_list',pro_list
                    # print 'remain_loc_list',len(remain_loc_list),remain_loc_list
                    # print 'sparse_list',sparse_list
                    # closest_list=center_list
                    while(1==1):
                        # compute Dji,j is the loc, i is the bag
                        Dji_list=self.get_Dji_list(remain_loc_list,center_list,full,0)

                        while(len(remain_loc_list)>0):
                            # the bag is not full, then add
                            if full[Dji_list[0][1]]==0:
                                bag_list[Dji_list[0][1]].append(Dji_list[0][0])
                                pro_list[Dji_list[0][1]].append(self.fir_pro[self.loc_set.index(Dji_list[0][0])])
                                index_list[Dji_list[0][1]].append(self.loc_set.index(Dji_list[0][0]))
                                remain_loc_list.remove(Dji_list[0][0])
                                remain_index_list.remove(self.loc_set.index(Dji_list[0][0]))
                                Efi = self.compute_E_Phi(bag_list[Dji_list[0][1]], pro_list[Dji_list[0][1]])
                                if Efi >= math.exp(self.epsilon)*self.Em:
                                    full[Dji_list[0][1]] = 1
                                del Dji_list[0]
                            # the bag is full
                            elif sum(full)==k: # the all bag is full, then add all
                                Dji_list = self.get_Dji_list(remain_loc_list, center_list, full,1)
                                while len(Dji_list)>0:
                                    bag_list[Dji_list[0][1]].append(Dji_list[0][0])
                                    pro_list[Dji_list[0][1]].append(self.fir_pro[self.loc_set.index(Dji_list[0][0])])
                                    index_list[Dji_list[0][1]].append(self.loc_set.index(Dji_list[0][0]))
                                    remain_loc_list.remove(Dji_list[0][0])
                                    remain_index_list.remove(self.loc_set.index(Dji_list[0][0]))
                                    del Dji_list[0]
                                for i in range(k):
                                    Efi = self.compute_E_Phi(bag_list[i], pro_list[i])
                                    if Efi >= math.exp(self.epsilon)*self.Em:
                                        full[i] = 1
                                    else:
                                        full[i] = 0
                                if sum(full) == k:
                                    flag = 1

                            else: # then break and update Dji_list
                                break

                        if len(remain_loc_list)==0 and sum(full)==k:
                            bag_D = 0
                            for i in range(k):
                                bag_D += self._min_cycle(bag_list[i])
                            bag_D = bag_D / k
                            if bag_D < satisfied_fi_D:
                                satisfied_fi = bag_list
                                satisfied_fi_D = bag_D
                            # print 'find it', bag_D, bag_list
                        if len(remain_loc_list)==0:break
                    center_list = []
                    for bag in bag_list:
                        if len(bag)==0:
                            x,y=0,0
                        else:
                            x = sum([bag[i][0] for i in range(len(bag))]) / len(bag)
                            y = sum([bag[i][1] for i in range(len(bag))]) / len(bag)
                        center_list.append([x, y])

                    circle_num+=1
                sampling_num += 1
            if satisfied_fi_D>satisfied_fi_D_list[-1]: flag=0
            satisfied_fi_list.append(satisfied_fi)
            satisfied_fi_D_list.append(satisfied_fi_D)
            satisfied_fi_D=99
            if last_flag==1:break
            if flag == 0 and last_flag==0:
                k-=1
                max_sampling_num=100
                last_flag=1
            if flag == 1:
                k+=1
        res_index=np.argmin(satisfied_fi_D_list)
        # print 'satisfied_fi_D_list',satisfied_fi_D_list
        # print 'satisfied_fi_list',satisfied_fi_list
        # print 'k=',len(satisfied_fi_list[res_index]),'result:',satisfied_fi_D_list[res_index],satisfied_fi_list[res_index]
        sens_list=[0 for i in range(n)]
        for bag in satisfied_fi_list[res_index]:
            sens=self._min_cycle(bag)
            for loc in bag:
                sens_list[self.loc_set.index(loc)]=sens
        return sens_list,satisfied_fi_list[res_index],center_list