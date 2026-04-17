import os
import random
import numpy as np
import PO
import test


def read_location_data(filename):
    with open(filename, 'r') as f:
        data = [line.strip() for line in f.readlines()]
    return data


def calculate_pro(m, d, c, G):  # 计算扰动概率
    # 计算求和部分: sum((j-1) * |G(j)|) 从 j=2 到 j=m
    summation = 0
    for j in range(2, m+1):
            # print(len(G[j]))
            summation += (j - 1) * len(G[j-1])

    # 计算min
    denominator = (m - 1) * d * c - summation*(c-1)
    if denominator <= 0:
        raise ValueError("Denominator is zero, division by zero error.")

    min_val = (m - 1) / denominator
    # print(min_val)

    # 计算max
    max_val = min_val * c

    dif = (max_val - min_val) / (m - 1)
    pro = [max_val - i * dif for i in range(m)]
    # print(pro)

    empty = 0
    for i in range(m):
        if len(G[i]) == 0:  # 如果G[i]为空
            pro[i] = 0
            empty += 1

    non_empty_sum = sum(pro)
    if non_empty_sum != 0:  # 防止除以零错误
        # 对于非零的 pro 值，归一化
        pro = [p / non_empty_sum if p != 0 else 0 for p in pro]

    # print(pro)  

    # global procount
    # procount=procount+1
    # print(procount)

    return pro

def calculate_pro_dict(m, d, c, G_list):
    result_dict = {}
    for key, value in G_list.items():
        # print(value)
        pro = calculate_pro(m, d, c, value)
        result_dict[key] = pro

    # for G in G_list:
    #     pro = calculate_pro(m, d, c, G)
    #     result_dict[G] = pro
    return result_dict


def SRR(user, GLCP, probabilities, m):
    r = random.uniform(0, 1)  # 生成一个0到1之间的随机数
    s = 0
    j = 0
    i = 0
    count=0
    psum=0.0
    p=0.0

    # 选择哪个组
    while j < m:
        s += probabilities[j]

        if r <= s:  # 如果随机数落在当前组的概率区间内
            if not GLCP[j]:
                j=j+1
                continue

            sample = random.choice(GLCP[j])  # 从该组中随机选一个位置
            return sample
        else:
            j += 1  # 如果没有选中当前组，继续检查下一个组

    # 如果没有返回，默认返回第一个组的第一个位置
    return GLCP[0][0]


def computer_Qloss(encodetxt,weizhitxt,GLCP,pro_dict):
    data = test.files_to_dict(encodetxt, weizhitxt) #data是编码对应的位置，用于计算distance
    domain = read_location_data(encodetxt)  #domain是全部编码位置
    sum=0.0
    for local in domain:  
        result = test.get_values_by_key(GLCP, local)  
        # probabilities = calculate_pro(m, len(data), c, GLCP[local])
        probabilities=pro_dict.get(local)
        for local_fabu in result: 
            xh = test.get_float_list_from_dict(data, local_fabu) 
            zi = test.get_float_list_from_dict(data, local) 
            distance = test._distance(zi, xh) 
            g_index,g_size=test.find_group(GLCP, local, local_fabu)  
            # print(probabilities[g_index])

            fpro=probabilities[g_index]/g_size 
            res=fpro*distance
            sum = sum + res *0.001
            #sum=sum+res*random.uniform(0.0005, 0.0015)   

    Qloss = sum

    # print("!!!!!!!!!")
    # print(Qloss)
    return Qloss

def computer_Pr(encodetxt,weizhitxt,GLCP,probabilities):
    data = test.files_to_dict(encodetxt, weizhitxt)
    domain = read_location_data(encodetxt)
    sum = 0.0
    Pr_dict= {}
    for local in domain:
        groups_fenzi = test.get_values_by_key(GLCP, local)
        for local_fabu in groups_fenzi:
            g_index, g_size = test.find_group(GLCP, local, local_fabu)
            fpro_fenzi = len(domain) * probabilities[g_index] / g_size

            for key, list in GLCP.items():
                for sublist in list:
                    if local_fabu in sublist and local_fabu not in Pr_dict:
                        index, size = test.find_group(GLCP, key, local_fabu)
                        sum = sum + len(domain) * probabilities[index] / size


            Pr = fpro_fenzi / sum
            Pr_dict.setdefault(local_fabu, Pr)
    return Pr_dict



def calculate_f(x_fabu, x, GLCP,probabilities):
    result = test.get_values_by_key(GLCP,x)
    if x_fabu not in result:
        return 0
    else:
        # probabilities = calculate_pro(m, len(data), c, GLCP[x])
        g_index, g_size = test.find_group(GLCP, x, x_fabu)
        return probabilities[g_index] / g_size
    # probabilities = calculate_pro(m, len(data), c, GLCP[x])
    # if test.find_group(GLCP, x, x_fabu)==-1:
    #     return 0
    # else:
    #     g_index, g_size = test.find_group(GLCP, x, x_fabu)
    #     return probabilities[g_index] / g_size

def calculate_posterior_probs(local_fabu, local, domain,GLCP,pro_dict):
    probabilities = pro_dict[local]
    denominator = sum([calculate_f(local_fabu, x, GLCP, probabilities) for x in domain])
    if denominator != 0:
        fpro = calculate_f(local_fabu, local, GLCP, probabilities)
        return fpro/denominator
    else:
        return 0

def get_posterior_dict(domain ,GLCP,pro_dict):
    posterior_dict = {}
    i=0
    for local_fabu in domain:
        for local in domain:
            posterior=calculate_posterior_probs(local_fabu, local, domain,GLCP,pro_dict)
            posterior_dict[(local_fabu, local)]=posterior
        print(i)
        i=i+1
    return posterior_dict


# 执行SRR扰动
def main(input_file, output_file, epsilon, m, c):
    # 假设的GLCP
    # GLCP = {
    #     '0111100100000110010001010100101001110000110011': [['0111100100000110010001010100101001110000110011'], ['0000000100000100111011111111000110101001010100','0111100100000100111011111100100011111010001111'], ['0111100100000100111011111100100011111010000010']],
    #     '0111100100000100111011111100100011111010000010': [['0111100100000100111011111100100011111010000010'], ['0000000100000100111011111111000110101001010100','0111100100000100111011111100100011111010001111'], ['0111100100000110010001010100101001110000110011']],
    #     '0000000100000100111011111111000110101001010100': [['0000000100000100111011111111000110101001010100'], ['0000000100000100111011111111000110101001010100'], ['0000000100000100111011111111000110101001010100','0111100100000100111011111100100011111010001111']],
    #     '0111100100000100111011111100100011111010001111': [['0111100100000100111011111100100011111010001111'], ['0000000100000100111011111111000110101001010100'], ['0000000100000100111011111111000110101001010100','0111100100000100111011111100100011111010001111']]
    # }

    # 读取数据集文件,得到完成分组后的GLCP
    with open('data_gowalla_encode.txt') as f:
        lines = f.readlines()
    # 数据预处理：将数据转换为位置编码
    data = [[line.strip().split(',')[0]] for line in lines]  # 假设每个位置信息只有一行，且以逗号分隔
    # 使用 Optgroup 函数进行位置分组
    GLCP = dict(PO.Optgroup(data))
    # print("GGGGGGGGGGGGGGG:")
    # print(GLCP)
    # 读取位置数据
    data = read_location_data(input_file)

    # 计算每个组的扰动概率
    # probabilities = compute_probabilities(epsilon, m, c)
    # print("PPPPPPPPPPPPPPP")
    # print(probabilities)

    # 存储扰动后的位置
    perturbed_locations = []

    pro_dict=calculate_pro_dict(m, len(data), c, GLCP)


    # 对每个位置执行SRR扰动
    for location in data:
        if location in GLCP:
            # pro=calculate_pro(m,len(data),c,GLCP[location])
            perturbed_location = SRR(location, GLCP[location], pro_dict.get(location), m)
            perturbed_locations.append(perturbed_location)  # 存储扰动后的结果

    # 将扰动后的结果写入输出文件
    with open(output_file, 'w') as f:
        for location in perturbed_locations:
            f.write(location + '\n')



# 运行主函数
if __name__ == '__main__':
    input_file = 'data_gowalla_encode.txt'  # 输入文件路径
    output_file = 'SRR_result.txt'  # 输出文件路径
    epsilon = 1.0  # 隐私预算
    m = 3  # 组数
    c = np.e ** epsilon  # 概率比率

    procount=0

    # 计算组数m的公式
    d = 1000
    # d = 3000
    print("m:",(2*(np.e**epsilon*d-np.e**(epsilon+1)))/((np.e**epsilon-1)*d))


    main(input_file, output_file, epsilon, m, c)
