import igl
import scipy as sp
import numpy as np

import os
root_folder = os.getcwd()

from scipy.sparse.linalg import spsolve

v, f = igl.read_triangle_mesh(os.path.join(root_folder, "data", "Foot.obj"))

#plot(v, f)
def combine_cut(full_cut):
    paths = [] 
    loops = []
    for i in range(len(full_cut)) :
        if full_cut[i][0] != full_cut[i][-1] :
            paths.append(full_cut[i])
            paths.append(list(reversed(full_cut[i])))
        else :
            loops.append(full_cut[i])

    t = loops[0]
    del loops[0]
    #print("first loop: ", t)
    c = 0
    # Circulate the current loop
    while c < len(t):
        # Choose a path that can be taken out of current loop circulatoin
        idx = -1
        for i, p in enumerate(paths):
            if paths[i][0] == t[c]: 
                del paths[i]
                idx = i

        c += 1
        if(idx!=-1):
            #print("Located path out of loop circulation at ", c)
            # Add that path
            t[c:c] = p[1:]
            #print("path: ", p)
            c += len(p) - 1
            # Choose a loop to begin circulating if there are more loops that need to be circulated.  
            if (len(loops) > 0):
                for i, l in enumerate(loops):
                    if l[0] == p[-1]:
                        del loops[i]
                        break
                t[c:c] = l[1:]
                #print("New loop circulation started at: ", c)
                #print("new loop: ", l)

    return np.array(t)

import random
boundary = igl.boundary_loop(f)
rand = random.randint(0, len(f))
seed_triangle_1 = f[rand] 
seed_removed_indicies = np.delete(f, rand, axis=0)
seed_triangle_2 = None
if len(boundary) == 0:
    rand = random.randint(0, len(f))
    seed_triangle_2 = f[rand] 
    seed_removed_indicies = np.delete(seed_removed_indicies, random.randint(0, len(seed_removed_indicies)), axis=0)

#cut = igl.cut_to_disk(seed_removed_indicies)
cut = igl.cut_to_disk(seed_removed_indicies)
cut2 = combine_cut(cut)
cut2
cuts=[]
cut=np.zeros((len(f),3), dtype=int)
i=0
k=0
for j in range((len(cut2)-1)):
    j1=cut2[j]
    j2=cut2[j+1]
    cuts.append((j1,j2))
    i=0
    for index1, face in enumerate(f):
        if (j1 in face and j2 in face):
            k+=1
            #print(j1,j2,face)
            y=0
            for index2, x in enumerate(face):
                if j1==x or j2==x:
                    cut[index1][index2]=1
                    #print(index1,index2)
                y+=1
            
        i+=1


vc,fc=igl.cut_mesh(v,f,cut)
print("ori",len(v),len(f))
print("cut",len(vc),len(fc))
