# -*- coding: gbk -*-
#lyx_2014-12-26

import math
import datetime
from numpy import *

def Init_graph(options):
    print "Initing the user_item graph G................."
    G = [[0 for i in range(NUM_USERS + NUM_ITEMS)] for i in range(NUM_USERS + NUM_ITEMS)]
    fileReader = open(options.csvfile,'r')
    for line in fileReader.readlines():
        line = line.replace("\n","")
        line = line.replace("\r","")
        line = line.split()
        user = int(line[0])
        item = int(line[1]) + NUM_USERS
        score = float(line[2])
        #score = 1
        G[user-1][item-1] = score
        G[item-1][user-1] = score
    fileReader.close()
    print
    return G

def Init_graph2(options):
    print "Initing the score graph R2................."
    R2 = [[0 for i in range(NUM_USERS)] for i in range(NUM_USERS)]   #用户信任评分矩阵
 
    r = open(options.csvfile2,'r')
    for line in r.readlines():
        line = line.replace("\n","")
        line = line.replace("\r","")
        info = line.split(" ")
        user_score = info[0]
        fan_score = info[1]
		score = info[2]    
        R2[user_score-1][fan_score-1] = score
    r.close()
    
    print
    return G2

def Hammock(G,uw):
    print "Start to add edges via Hammock..............."
    print "User Hammock width is " + str(uw)
    G_hammock = G
    u2u = [[[0,0] for i in range(NUM_USERS)] for i in range(NUM_USERS)]
    for i in range(NUM_USERS,NUM_USERS + NUM_ITEMS):
        for j in range(NUM_USERS):
            if G[i][j] == 0:
                continue
            for k in range(NUM_USERS):
                if k == j or G[i][k] == 0:
                    continue
                if u2u[k][j][1] > 0:
                    u2u[k][j][1] += G[i][j]
                    u2u[k][j][0] += 1
                    continue
                u2u[j][k][1] += G[i][j]
                u2u[j][k][0] += 1
    nrofU2U = 0
    w = open("hammock.csv",'w')
    for i in range(NUM_USERS):
        for j in range(NUM_USERS):
            if u2u[i][j][0] >= uw:
                nrofU2U += 1
                G_hammock[i][j] = float(u2u[i][j][1]) / u2u[i][j][0]
                G_hammock[j][i] = G_hammock[i][j]
                w.write(str(i+1) + " " + str(j-NUM_USERS+1) + " 1" + "\n")
    w.close()
    nrofU2U = float(nrofU2U)
    print "nrofU2U via Hammock: " + str(nrofU2U)
    print
    return G_hammock

def PersonalRank(G,alpha,steps,trasMatrix,G2, G3, gamma):
    print "Start to Rank..............."
    #user_rank每一列代表该列第一个元素下的rank值
    #r0是单位矩阵e
    r0 = eye(NUM_USERS + NUM_ITEMS)
    user_rank = r0
    M = mat(trasMatrix)
    MT = M.T
    for step in range(steps):
        print "SETP " + str(step+1) + " personal rank....."
        user_rank = (1 - alpha) * r0 + alpha * MT * user_rank
        '''
        #打印每次迭代的部分结果，确定收敛步数
        temp = user_rank.tolist()
        p = 0
        print "step: " + str(step)
        for k in range(NUM_USERS + NUM_ITEMS):
            print "number " + str(k) + ": " + str(temp[k][0])
            p += 1
            if p >= 10:
                break
        print
        '''
       # user_attention_rank = PR_attention(G2, G3, user_rank,step)         ########
       # user_rank = user_attention_rank * (1 - gamma) + user_rank * gamma
	   
        
    user_rank = user_rank.tolist()
	
	
    return user_rank

def PR_attention(G2, G3, user_rank,step):
    print "SETP " + str(step+1) + " attention rank....."
    energy = zeros([NUM_USERS + NUM_ITEMS,NUM_USERS + NUM_ITEMS])
    for i in range(NUM_USERS):
        for j in range(len(G2[i])):
            if G2[i][j] > 0:
                energy[:,i:i+1] = energy[:,i:i+1] + user_rank[:,j:j+1] * G2[i][j]
    return energy + G3
    
def Recommend(nrofRecommendList,user_rank,user_items,options):
    print "Start to recommend................."
    print "nrofRecommendList: " + str(nrofRecommendList)
    if options.outfile3:
        out = "extra_" + options.outfile3
    else:
        out = "extraList.csv"
    w = open(out,'w')
    w.close()
    #user_recommendList是一个矩阵，每行代表这个用户的访问概率分布
    user_recommendList = [[[0 for i in range(2)] for i in range(nrofRecommendList)] for i in range(NUM_USERS)]
    user_rank_t = user_rank
    for user in range(NUM_USERS):
        #print "remcommend the user " + str(user) + "...."
        n = 0
        for i in range(NUM_ITEMS):
            seclected_nodeID = 0
            temp = -1
            for j in range(NUM_USERS,NUM_USERS + NUM_ITEMS):
                #print "j:" + str(j) + " user:" + str(user) + " i:" + str(i)
                if temp < user_rank_t[j][user]:
                    temp = user_rank_t[j][user]
                    seclected_nodeID = j
            #print seclected_nodeID
            #user_rank_t[seclected_nodeID][user] = -1
            if user_items[user][seclected_nodeID] ==0 and seclected_nodeID >= NUM_USERS and seclected_nodeID < (NUM_USERS + NUM_ITEMS):
                user_recommendList[user][n][0] = seclected_nodeID
                user_recommendList[user][n][1] = user_rank_t[seclected_nodeID][user]
                user_rank_t[seclected_nodeID][user] = -1
                n += 1
            else:
                user_rank_t[seclected_nodeID][user] = -1
                w = open(out,'a')
                w.write("u" + str(user+1) + " " + "i" + str(seclected_nodeID+1-NUM_USERS) + ":" + str(user_rank[seclected_nodeID][user]) + "\n")
                w.close()
            if n >= nrofRecommendList:
                break
    return user_recommendList

def Evaluate(user_recommendList, nrofAll_items, test_user_items, options):
    print "Start to evaluate................."
    nrofTu = 0
    nrofRu = 0
    nrofCommonElements = 0
    RecommendedList = set()
    
    for user in range(len(test_user_items)):
        for item in range(len(test_user_items[user])):
            if test_user_items[user][item] == 1:
                nrofTu += 1
    for user in range(len(user_recommendList)):
        for x in range(len(user_recommendList[user])):
            nrofRu += 1
            itemID = user_recommendList[user][x][0]
            RecommendedList.add(itemID)
            if test_user_items[user][itemID] == 1:
                nrofCommonElements += 1
                
    print "nrofCommonElements: " + str(nrofCommonElements)
    print "nrofTu: " + str(nrofTu)
    print "nrofRu: " + str(nrofRu)
    print "nrofAll_items: " + str(nrofAll_items)
    print "RecommendedList: " + str(len(RecommendedList))
    
    #回召率，准确率，覆盖率，流行度
    Recall = float(nrofCommonElements) / nrofTu
    print "Recall: " + str(Recall)
    Recall = str("%.2f"%(Recall * 100)) + "%"
    Precision = float(nrofCommonElements) / nrofRu
    print "Precision: " + str(Precision)
    Precision = str("%.2f"%(Precision * 100)) + "%"
    Coverage = float(len(RecommendedList)) / nrofAll_items
    print "Coverage: " + str(Coverage)
    Coverage = str("%.2f"%(Coverage * 100)) + "%"

    fileWrite = open(options.outfile, 'w')
    fileWrite.write("准确率    召回率    覆盖率" + "\n")
    fileWrite.write(Precision + "    " + Recall + "    " + Coverage + "\n")
    fileWrite.close()

def Factor(trasMatrix,alpha):
    factor = mat(trasMatrix)
    factor = factor.T
    e = eye(NUM_USERS + NUM_ITEMS)
    factor = e - alpha * factor
    factor = factor.I
    return factor

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-c", "--csvfile", dest="csvfile", default="",
                      action="store", type="string", metavar="FILE",
                      help="CSV file contains imdb top movies' list")
    parser.add_option("-e", "--csvfile2", dest="csvfile2", default="",
                      action="store", type="string", metavar="FILE",
                      help="CSV file contains imdb top movies' list")
    parser.add_option("-n", "--outfile2", dest="outfile2", default="",
                      action="store", type="string", metavar="FILE",
                      help="CSV file contains imdb top movies' list")
    parser.add_option("-l", "--csvfile3", dest="csvfile3", action="store",
                      type="string", default="", metavar="FILE",
                      help="search languages: en--englis, zh-simplified chinese")
    parser.add_option("-o", "--outfile", dest="outfile", default="",
                      action="store", type="string", metavar="FILE",
                      help="search results of given movie list")
    parser.add_option("-p", "--outfile3", dest="outfile3", default="",
                      action="store", type="string", metavar="FILE",
                      help="search results of given movie list")
    (options, args) = parser.parse_args()
    #  -c base -e friends -l test -o eva -n rem (-p list可选)
    if options.csvfile and options.csvfile2 and options.csvfile3 and options.outfile and options.outfile2:
        starttime = datetime.datetime.now()
        trainusers = set()
        trainitems = set()
        allitems = set()
        allusers = set()
                   
        #统计训练集中的人数、物品数
        fileReader = open(options.csvfile,'r')
        for line in fileReader.readlines():
            line = line.replace("\n","")
            line = line.replace("\r","")
            line = line.split()
            user = line[0]
            item = line[1]
            if user not in trainusers:
                trainusers.add(user)
            if item not in trainitems:
                trainitems.add(item)
        fileReader.close()

        allitems = trainitems
        allusers = trainusers
        test_user_items = []
        #统计测试集中的人数、物品数
        fileReader = open(options.csvfile3,'r')
        for line in fileReader.readlines():
            line = line.replace("\n","")
            line = line.replace("\r","")
            line = line.split()
            user = line[0]
            item = line[1]
            if user not in allusers:
                allusers.add(user)
            if item not in allitems:
                allitems.add(item)
        fileReader.close()
        
        global NUM_USERS
        NUM_USERS = len(allusers)
        global NUM_ITEMS
        NUM_ITEMS = len(allitems)
        print "Nrof users in trainning set: " + str(len(trainusers))
        print "Nrof items in trainning set: " + str(len(trainitems))
        print "Nrof users in all set: " + str(len(allusers))
        print "Nrof items in all set: " + str(len(allitems))
                   
        #找出用户在训练集中已经访问过的物品
        user_items = [[0 for i in range(NUM_USERS + NUM_ITEMS)] for i in range(NUM_USERS + NUM_ITEMS)]
        fileReader = open(options.csvfile,'r')
        for line in fileReader.readlines():
            line = line.replace("\n","")
            line = line.replace("\r","")
            line = line.split()
            user = int(line[0])
            item = int(line[1]) + NUM_USERS
            user_items[user-1][item-1] = 1
        fileReader.close()

        #找出用户在测试集中选择的物品
        test_user_items = [[0 for i in range(NUM_USERS + NUM_ITEMS)] for i in range(NUM_USERS + NUM_ITEMS)]
        fileReader = open(options.csvfile3,'r')
        for line in fileReader.readlines():
            line = line.replace("\n","")
            line = line.replace("\r","")
            line = line.split()
            user = int(line[0])
            item = int(line[1]) + NUM_USERS
            test_user_items[user-1][item-1] = 1
        fileReader.close()  
        
        #初始化图G
        starttime1 = datetime.datetime.now()
        G = Init_graph(options)
        print "Graph G has " + str(len(G)) + " nodes"
        endtime1 = datetime.datetime.now()
        print  unicode(endtime1)
        timeUse1 = unicode((endtime1-starttime1).seconds)
        print timeUse1
        #Hammock建图,w通过实测得到，uw是hammock宽度k
        uw = 15
        G = Hammock(G,uw)
        #保留系数retention，即保留每个用户访问度前百分之多少的关注关系
        retention = 0.1
        starttime2 = datetime.datetime.now()
        G2,G3 = Init_graph2(options,retention)
        endtime2 = datetime.datetime.now()
        print  unicode(endtime2)
        timeUse2 = unicode((endtime2-starttime2).seconds)
        print timeUse2
        #参数α，迭代次数指定,训练集训练
        alpha = 0.6
        #结合因子gamma，1.0是PR，小于1.0是AR
        gamma = 0.4
        #通过实测得到迭代次数
        steps = 15
        
        
        #计算G1转移矩阵
        print "Init G1 trasMatrix....."
        trasMatrix = [[0 for i in range(NUM_USERS + NUM_ITEMS)] for i in range(NUM_USERS + NUM_ITEMS)]
        for i in range(NUM_USERS + NUM_ITEMS):
            sum_ij = 0
            for j in range(NUM_USERS + NUM_ITEMS):
                sum_ij += float(G[i][j])
            if sum_ij == 0:
                continue
            for j in range(NUM_USERS + NUM_ITEMS):
                trasMatrix[i][j] = float(G[i][j]) / sum_ij
        #计算(1-alpha*MT)的逆
        #factor = Factor(trasMatrix,alpha)
                   
        #user_rank每一列代表该列第一个元素下的rank值。行可以代表这个点在不同起点开始游走下的被访问值，可以看出重要性。
        user_rank = PersonalRank(G,alpha,steps,trasMatrix,G2, G3, gamma)
        user_rank_list = user_rank

        
        
        #推荐数量指定，开始推荐。并记录推荐结果
        nrofRecommendList = 15
        #user_recommendList是一个 用户数*推荐长度 的矩阵，每行代表这个用户的访问概率分布
        user_recommendList = Recommend(nrofRecommendList,user_rank,user_items,options)
        print "write into rem.csv......."
        fileWrite = open(options.outfile2, 'w')
        for user in range(len(user_recommendList)):
            fileWrite.write("u" + str(user+1) + " ")
            for i in range(len(user_recommendList[user])):
                #print user_recommendList[user][i]
                fileWrite.write("i" + str(user_recommendList[user][i][0]+1-NUM_USERS) + ":" + str(user_recommendList[user][i][1]) + " ")
            fileWrite.write("\n")
        fileWrite.close()

        #测试集测试
        nrofAll_items = len(allitems)
        Evaluate(user_recommendList, nrofAll_items, test_user_items, options)
        print "steps: " + str(steps)
        
        #形成-p list
        if options.outfile3:
            print "Start to list......"
            lenOfList = 200
            user_list = [[[0 for i in range(2)] for i in range(lenOfList)] for i in range(NUM_USERS)]
            for user in range(NUM_USERS):
                print "list the user " + str(user) + "...."
                n = 0
                for i in range(NUM_ITEMS):
                    seclected_nodeID = 0
                    temp = -1
                    for j in range(NUM_USERS,NUM_USERS + NUM_ITEMS):
                        #print "j:" + str(j) + " user:" + str(user) + " i:" + str(i)
                        if temp < user_rank_list[j][user]:
                            temp = user_rank_list[j][user]
                            seclected_nodeID = j
                    #print seclected_nodeID
                    #user_rank_list[seclected_nodeID][user] = -1
                    if seclected_nodeID >= NUM_USERS and seclected_nodeID < (NUM_USERS + NUM_ITEMS):
                        user_list[user][n][0] = seclected_nodeID
                        user_list[user][n][1] = user_rank_list[seclected_nodeID][user]
                        user_rank_list[seclected_nodeID][user] = -1
                        n += 1
                    else:
                        user_rank_list[seclected_nodeID][user] = -1
                    if n >= lenOfList:
                        break
            print "write into list.csv......."
            fileWrite = open(options.outfile3, 'w')
            for user in range(len(user_list)):
                fileWrite.write("u" + str(user+1) + " ")
                for i in range(len(user_list[user])):
                    #print user_list[user][i]
                    fileWrite.write("i" + str(user_list[user][i][0]+1-NUM_USERS) + ":" + str(user_list[user][i][1]) + " ")
                fileWrite.write("\n")
            fileWrite.close()
        

        #记录时间
        endtime = datetime.datetime.now()
        print  unicode(endtime)
        timeUse = unicode((endtime-starttime).seconds)
        print timeUse
        fileWrite = open(options.outfile, 'a')
        fileWrite.write('timeUse :' + unicode(timeUse))
        fileWrite.close()
        
    else:
        parser.error("need to specify -c -e -o parameter")
