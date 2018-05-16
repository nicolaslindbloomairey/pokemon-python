import time
from picksix import generateTeam

def thousand():
    t0 = time.time() 

    for i in range(0, 100000):
        generateTeam()

    t1 = time.time()
    print('battles took ', (t1-t0)*1000, ' milliseconds')

from picksix import generateTeam
import cProfile
import re
#cProfile.run('thousand()')
thousand()
