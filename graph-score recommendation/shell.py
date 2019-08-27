# -*- coding: utf-8 -*-
import subprocess
import sys
print 'run'
#subprocess.call('python graph_trust.py -c epinion_train.csv -e trust_friends.csv -l epinion_test.csv -o T_eva.csv', shell = True,stdout=sys.stdout)
subprocess.call('python graph_trust.py -c 55smallCiao_train.csv -e small_Ciao_trust.csv -l 55smallCIao_test.csv -o T_eva.csv', shell = True,stdout=sys.stdout)
#input("Prease <enter>")