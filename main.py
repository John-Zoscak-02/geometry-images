import numpy as np
import random
import igl
import trimesh as tri
from IPython.core.display import display, HTML

random.seed(42)

data_dir = "data/"
#files = ["ChineseLion.obj",
#         "Femur.obj",
#         "Foot.obj",
#         "Hat.obj",
#         "HumanBrain.obj",
#         "HumanFace.obj",
#         "Nefertiti.obj",
#         "OldMan.obj",
#         "StanfordBunny.obj",
#         "spot_triangulated.obj"]
#files = ["StanfordBunny.obj"]
files = ["spot_triangulated.obj"]

def display_cut(vertex_positions, indicies, full_cut):
    trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies) 
    scene = tri.Scene(trimesh)
    for cut in full_cut:
        if len(cut) == 4:
            continue
        cut_verticies = vertex_positions[cut]
        range = np.arange(2, len(cut))
        line_range= tri.path.entities.Line(points=range,color=np.array([[255,0,0,255]]))
        path1 = tri.path.path.Path3D(entities=[line_range], vertices=cut_verticies)
        scene.add_geometry(path1)
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

        initial_cut = igl.cut_to_disk(seed_removed_indicies)

        for cut in initial_cut:
            cut_verticies = vertex_positions[cut]
            print("cut head: \n", cut[2:12])
            print("cut points: \n", cut_verticies[2:12] )
            print("cut lines head: \n", np.array(tuple(zip(cut_verticies[:-1][2:12], cut_verticies[1:][2:12]))))

        display_cut(vertex_positions=vertex_positions, indicies=indicies, full_cut=initial_cut)

