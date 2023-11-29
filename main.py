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
    "ChineseLion.obj",
    "Femur.obj",
    "Foot.obj",
    #"happy.obj",
    "Hat.obj",
    "HumanBrain.obj",
    "HumanFace.obj",
    "Nefertiti.obj",
    "OldMan.obj",
#    "rocker-arm.obj",
#    "spot_triangulated.obj"
    "StanfordBunny.obj",
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

def display_parameterized_geometry(vertex_positions, indicies, colors) :
    trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies) 
    trimesh.visual.face_colors = colors

    #print(len(trimesh.face_adjacency))
    ## get a Path3D object for the edges we want to highlight
    #d = tri.path.exchange.misc.faces_to_path(trimesh)
    #path = tri.path.path.Path3D(entities=d['entities'], verticies=d['vertices'])

    scene = tri.Scene(trimesh)
    scene.show(flags = {'wireframe':True, 'cull': False}, 
               line_settings={'line_width': 1.5})

if __name__ == '__main__' :
    #n = int(input("What size geometry image would you like? "))

    for file in files:
        # Read in the vertex positions of the geometry
        # Read in the indicies of the triangle mesh 
        vertex_positions, indicies = igl.read_triangle_mesh("%s%s"%(data_dir, file))

        print("filename: ", file)
        print("vertex_pos shape: ", vertex_positions.shape) 
        print("vertex_pos head: \n", vertex_positions[:10])
        print("indicies shape: ", indicies.shape)
        print("indicies head: \n", indicies[:10])
        
        boundary = igl.boundary_loop(indicies)
        #print("boundary length: ", len(boundary))

        seed_removed_indicies = indicies
        #seed_removed_indicies = np.delete(indicies, random.randint(0, len(indicies)), axis=0)
        #if len(boundary) == 0:
        #    seed_removed_indicies = np.delete(seed_removed_indicies, random.randint(0, len(seed_removed_indicies)), axis=0)

        cut = igl.cut_to_disk(seed_removed_indicies)

        #for sub_cut in cut:
        #    cut_verticies = vertex_positions[sub_cut]
        #    print("cut head: \n", sub_cut[:6], sub_cut[-6:])
        #    print("cut points: \n", cut_verticies[:6], cut_verticies[-6:])
        #    print("cut lines head: \n", np.array(tuple(zip(cut_verticies[:-1][:6], cut_verticies[1:][:6]))), np.array(tuple(zip(cut_verticies[:-1][:6], cut_verticies[1:][-6:]))))

        colors = display_cut(vertex_positions=vertex_positions, indicies=indicies, full_cut=cut)

        #cut = np.array(cut[0])
        cut = np.array(boundary)
        # Map the cut verticies to a circle for the parameterization
        cut_uv = igl.map_vertices_to_circle(vertex_positions, cut)

        # Create a harmonic parameterization for the inner verticies of the parameterized representation
        uv = igl.harmonic_weights(vertex_positions, indicies, cut, cut_uv, 1)
        vertex_positions_p = np.hstack([uv, np.zeros((uv.shape[0],1))])

        display_parameterized_geometry(vertex_positions=vertex_positions_p, indicies=indicies, colors=colors)






