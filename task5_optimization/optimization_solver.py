"""
Task 5 – Optimization over Reachable Markings
----------------------------------------------
Description:
    Given a linear objective function maximize c^T M, where M belongs
    to the set of reachable markings Reach(M0), determines the marking
    that maximizes the objective function. If no marking satisfies
    the condition, the program reports none.

Input:
    data/reachable_markings.json

Output:
    data/optimization_result.json

Author:
    Thanh Binh
"""
import time
import numpy as np
import json
def read(path):
    f=open(path,"r")
    arr=json.load(f)
    f.close()
    return arr
def write(ans,path):
    f=open(path,"w")
    f.write(json.dumps(ans))
    f.close()
def optimization(markingArr,c):
    ans=float("-inf")
    ansArr=[]
    for markingItem in markingArr:
        tmp=0
        i=0
        for p in markingItem:
            tmp=tmp+c[i]*markingItem[p]
            i=i+1
        if(tmp>ans):
            ansArr.clear()
            ans=tmp
            ansArr.append(markingItem)
        else:
            if(tmp==ans): ansArr.append(markingItem)

    return ans,ansArr
def main():
    markingArr=read("./data/reachable_markings.json")
    #c=list(np.random.randn(len(markingArr[0])))
    #write(c,"./data/CArr.json")
    c=read("./data/CArr.json")
    start=time.perf_counter()
    bestVal,bestMarking=optimization(markingArr,c)
    end=time.perf_counter()
    ans={
        "best_marking":bestMarking,
        "max_value":bestVal,
        "time_seconds:":end-start
    }
    write(ans,"./data/optimization_result.json")

main()
