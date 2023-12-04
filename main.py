import os
import numpy as np
import scipy as sp
import random
import trimesh as tri
import igl
from matplotlib.colors import LinearSegmentedColormap
import pyglet

SEED = 27
random.seed(SEED)

data_dir = "data/"
files = [
#    "beetle.obj",
    #"ChineseLion.obj",
    #"Femur.obj",
    #"Foot.obj",
    #"happy.obj",
    #"Hat.obj",
    "HumanBrain.obj",
    #"HumanFace.obj",
    #"Nefertiti.obj",
    #"OldMan.obj",
#    "rocker-arm.obj",
#    "spot_triangulated.obj"
    #"StanfordBunny.obj",
#    "xyzrgb_dragon.obj"
]
#files = ["StanfordBunny.obj"]
#files = ["spot_triangulated.obj"]
#files = ["rocker-arm.obj"]
#files = ["beetle.obj"]
#files = ["xyzrgb_dragon.obj"]
#files = ["happy.obj"]

def display_cut(vertex_positions, indicies, full_cut):
    trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies) 
    scene = tri.Scene(trimesh)

    for cut in full_cut:
        cut_verticies = vertex_positions[cut]
        range = np.arange(0, len(cut))
        line_range= tri.path.entities.Line(points=range,color=np.array([[255,0,0,255]]))
        path1 = tri.path.path.Path3D(entities=[line_range], vertices=cut_verticies)
        scene.add_geometry(path1)

    M = np.sum(np.mean(vertex_positions[indicies], axis=1), axis=1)
    colors = tri.visual.interpolate(M, color_map='viridis')
    trimesh.visual.face_colors = colors

    scene.show(flags = {'cull': False})

    return colors

def get_edges_from_path(path):
    edges = [] 
    for v in range(len(path)-1):
        edge = [path[v], path[v+1]]
        if (edge[0] > edge[1]): edge = [path[v+1], path[v]]
        edges.append(edge)
    return edges

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

def transform_cut(combined_cut, faces):
    cut2 = combined_cut
    cut2
    cuts=[]
    cut=np.zeros((len(faces),3), dtype=int)
    i=0
    k=0
    for j in range((len(cut2)-1)):
        j1=cut2[j]
        j2=cut2[j+1]
        cuts.append((j1,j2))
        i=0
        for index1, face in enumerate(faces):
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

    return cut



def display_parameterized_geometry(vertex_positions, indicies, colors) :
    trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies) 
    trimesh.visual.face_colors = colors

    #print(len(trimesh.face_adjacency))
    ## get a Path3D object for the edges we want to highlight
    #d = tri.path.exchange.misc.faces_to_path(trimesh)
    #path = tri.path.path.Path3D(entities=d['entities'], verticies=d['vertices'])

    scene = tri.Scene(trimesh)
    scene.show(flags = {'wireframe':True, 'cull': False}, line_settings={'line_width': 1.5} )

if __name__ == '__main__' :
    #n = int(input("What size geometry image would you like? "))

    for file in files:
        # Read in the vertex positions of the geometry
        # Read in the indicies of the triangle mesh 
        vertex_positions, indicies = igl.read_triangle_mesh("%s%s"%(data_dir, file))

        print("filename: ", file)
        print("vertex_pos shape: ", vertex_positions.shape) 
        #print("vertex_pos head: \n", vertex_positions[:10])
        print("indicies shape: ", indicies.shape)
        #print("indicies head: \n", indicies[:10])
        
        boundary = igl.boundary_loop(indicies)
        #print("boundary length: ", len(boundary))

        rand = random.randint(0, len(indicies))
        seed_triangle_1 = indicies[rand] 
        seed_removed_indicies = np.delete(indicies, rand, axis=0)
        seed_triangle_2 = None
        if len(boundary) == 0:
            rand = random.randint(0, len(indicies))
            seed_triangle_2 = indicies[rand] 
            seed_removed_indicies = np.delete(seed_removed_indicies, random.randint(0, len(seed_removed_indicies)), axis=0)

        cut = igl.cut_to_disk(seed_removed_indicies)

        for sub_cut in cut:
            cut_verticies = vertex_positions[sub_cut]
            print("cut head: \n", sub_cut[:1], sub_cut[-1:], "\nlen: ", len(sub_cut))
            #print("cut points: \n", cut_verticies[:1], cut_verticies[-1:])
            #print("cut lines head: \n", np.array(tuple(zi(cut_verticies[:-1][:1], cut_verticies[1:][:1]))), np.array(tuple(zip(cut_verticies[:-1][:1], cut_verticies[1:][-1:])))

        colors = display_cut(vertex_positions=vertex_positions, indicies=indicies, full_cut=cut)

        #combined_cut = combine_cut(cut)
        #print("transforming cut")
        #cut = transform_cut(combined_cut, indicies)

        #vcut, fcut = igl.cut_mesh(vertex_positions, indicies, cut)
        #trimesh = tri.Trimesh(vertices=vcut, faces=fcut)
        #M = np.sum(np.mean(vertex_positions[indicies], axis=1), axis=1)
        #colors = tri.visual.interpolate(M, color_map='viridis')
        #trimesh.visual.face_colors = colors

        #scene = tri.Scene(trimesh)
        #scene.show(flags = {'cull': False})

        trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies)
        for sub_cut in cut:
            if (sub_cut[0] != sub_cut[-1]): 
                rmi = set()
                for i in range(len(sub_cut)):
                    v = sub_cut[i]
                    adjacent_triangle_indicies = np.where(np.sum(indicies==v, axis=1)>0)[0]
                    rmi.update(adjacent_triangle_indicies)
                #print(list(rmi))
                indicies = np.delete(indicies, list(rmi), axis=0)

                #edges = get_edges_from_path(sub_cut)
                #adj_index = trimesh.face_adjacency_edges_tree.query(edges)[1]
                #print(adj_index)

                #faces = trimesh.face_adjacency[adj_index]
                
                #print("indicies before: ", indicies.shape)
                #indicies = np.delete(trimesh.faces, faces, axis=0)
                #print("indicies after: ", indicies.shape)

        trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies)
        M = np.sum(np.mean(vertex_positions[indicies], axis=1), axis=1)
        colors = tri.visual.interpolate(M, color_map='viridis')
        trimesh.visual.face_colors = colors

        scene = tri.Scene(trimesh)
        scene.show(flags = {'cull': False})

        bnd = igl.boundary_loop(indicies)
        display_cut(vertex_positions=vertex_positions, indicies=indicies, full_cut=[bnd])
        bnd_uv = igl.map_vertices_to_circle(vertex_positions, bnd)

        # Create a harmonic parameterization for the inner verticies of the parameterized representation
        uv = igl.harmonic(vertex_positions, indicies, bnd, bnd_uv, 1)
        print("ran harmonic")
        vertex_positions_p = np.hstack([uv, np.zeros((uv.shape[0],1))])

        display_parameterized_geometry(vertex_positions=vertex_positions_p, indicies=indicies, colors=colors)
