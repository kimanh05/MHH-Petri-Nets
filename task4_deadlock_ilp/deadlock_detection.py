"""
Task 4 – Deadlock Detection using ILP and BDD
----------------------------------------------
Description:
    Combines Integer Linear Programming (ILP) and the BDD from Task 3
    to detect a deadlock if it exists. A dead marking is one in which
    no transition is enabled. The program reports one deadlock marking
    if found, or states that none exists.

Input:
    data/reachable_markings.json or data/bdd_result.json

Output:
    data/deadlocks.json

Author:
    Thanh Dat
"""
