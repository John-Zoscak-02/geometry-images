import os
import numpy as np
import scipy as sp
import random
import trimesh as tri
from IPython.core.display import display, HTML
import igl

SEED = 27
random.seed(SEED)

data_dir = "data/"
#files = [
#    "beetle.obj",
#    "ChineseLion.obj",
#    "Femur.obj",
#    "Foot.obj",
#    "happy.obj",
#    "Hat.obj",
#    "HumanBrain.obj",
#    "HumanFace.obj",
#    "Nefertiti.obj",
#    "OldMan.obj",
#    "rocker-arm.obj",
#    "spot_triangulated.obj"
#    "StanfordBunny.obj",
#    "xyzrgb_dragon.obj"
#]
#files = ["StanfordBunny.obj"]
files = ["spot_triangulated.obj"]
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
    scene.show()

def display_parameterized_geometry(vertex_positions, indicies) :
    trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies) 
    scene = tri.Scene(trimesh)
    # facets are groups of coplanar adjacent faces
    # set each facet to a random color
    # colors are 8 bit RGBA by default (n, 4) np.uint8
    for facet in trimesh.facets:
        trimesh.visual.face_colors[facet] = tri.visual.random_color()
    scene.show()



def cut_and_parameterize(M, p, n):
    values =  np.zeros((n , n, 3))
    normals = np.zeros((n, n, 3))

    #pcd = M.sample_points_uniformly(number_of_points=n*n)

if __name__ == '__main__' :
    #n = int(input("What size geometry image would you like? "))

    for file in files:
        # Read in the vertex positions of the geometry
        # Read in the indicies of the triangle mesh 
        vertex_positions, indicies = igl.read_triangle_mesh("%s%s"%(data_dir, file))

        print("vertex_pos shape: ", vertex_positions.shape) 
        print("vertex_pos head: \n", vertex_positions[:10])
        print("indicies shape: ", indicies.shape)
        print("indicies head: \n", indicies[:10])
        
        boundary = igl.boundary_loop(indicies)
        print("boundary length: ", len(boundary))

        seed_removed_indicies = np.delete(indicies, random.randint(0, len(indicies)), axis=0)
        if len(boundary) == 0:
            seed_removed_indicies = np.delete(seed_removed_indicies, random.randint(0, len(seed_removed_indicies)), axis=0)

        cut = igl.cut_to_disk(seed_removed_indicies)

        for sub_cut in cut:
            cut_verticies = vertex_positions[sub_cut]
            print("cut head: \n", sub_cut[0:12])
            print("cut points: \n", cut_verticies[0:12] )
            print("cut lines head: \n", np.array(tuple(zip(cut_verticies[:-1][0:12], cut_verticies[1:][0:12]))))

        display_cut(vertex_positions=vertex_positions, indicies=indicies, full_cut=cut)

        print(cut)
        # Map the cut verticies to a circle for the parameterization
        cut_uv = igl.map_vertices_to_circle(vertex_positions, np.array(cut[-1]))

        # Create a harmaonic parameterization for the inner verticies of the parameterized representation
        print(igl.harmonic)
        uv = igl.harmonic(vertex_positions, indicies, cut, cut_uv, 1)
        vertex_positions_p = np.hstack([uv, np.zeros((uv.shape[0],1))])




