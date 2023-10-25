import numpy as np
#import open3d as o3d
import random
import igl
import scipy
# from meshplot import plot, subplot, interact
import trimesh as tri
from IPython.core.display import display, HTML

# Comment this line out if running in Jupyter
# mp.offline()

# Comment out these functions when running offline, as they are not needed
#def plot_mesh(v, f, colors=None) :
#    data = mp.plot(v,f,c=colors,s=[2,2,0])
#    display(HTML(data.to_html))
#    return data

#def subplot_mesh(v, f, d, colors=None) :
#    display(HTML(mp.subplot(v,f,c=colors,s=[2,2,0],data=d).to_html()))

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

n = int(input("What size geometry image would you like? "))

def display_cut(vertex_positions, indicies, cut):
    # Find the open boundary to map to the square
    #
    initial_cut = igl.cut_to_disk(indicies)

    trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies) 
    scene = tri.Scene(trimesh)
    for cut in initial_cut:
        cut_verticies = vertex_positions[cut]
        range = np.append(np.arange(len(cut)), 0)
        line_range= tri.path.entities.Line(points=range,color=np.array([[255,0,0,255]]))
        path1 = tri.path.path.Path3D(entities=[line_range], vertices=cut_verticies)
        scene.add_geometry(path1)
        #scene.add_geometry(path2)
    scene.show()

meshes = []
for file in files:
    #mesh = o3d.io.read_triangle_mesh( "%s%s"%(data_dir, file) )
    #mesh.compute_vertex_normals()
    #o3d.visualization.draw_geometries([mesh])
    #pcd = mesh.sample_points_uniformly(number_of_points=(n*n))
    #o3d.visualization.draw([pcd])
    #points = np.array(pcd.points)
    #mesh.compute_adjacency_list()
    #meshes.append(mesh)

    # Read in the vertex positions of the geometry
    # Read in the indicies of the triangle mesh 
    vertex_positions, indicies = igl.read_triangle_mesh("%s%s"%(data_dir, file))
    indicies = indicies[1:]

    # Find the open boundary to map to the square
    # 
    # igl.boundary_loop will calculate an ordered list of boundary vertices of the 
    # longest boundary loop
    #boundary = igl.boundary_loop(indicies)
    initial_cut = igl.cut_to_disk(indicies)[0]
    print(initial_cut)
    cut_verticies = vertex_positions[initial_cut]
    print(cut_verticies)
    #cut_indicies = np.array([[initial_cut[i], initial_cut[i+1]] for i in range(len(initial_cut)-1)])

    # plt = plot(vertex_positions, indicies, return_plot=True)
    #plt = plot(np.array([]))
    #subplot(vertex_positions, indicies, data=plt)
    #plt.add_lines(boundary_verticies[:-1], boundary_verticies[1:], shading={"line_color": "red"});
    trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies) 
    range = np.append(np.arange(len(initial_cut)), 0)
    line_range1 = tri.path.entities.Line(points=range,color=np.array([[255,0,0,255]]))
    #line_range2 = tri.path.entities.Line(points=np.arange(len(boundary)), color=np.array([[0,255,0,255]]))
    print("line_range: ", line_range1)
    path1 = tri.path.path.Path3D(entities=[line_range1], vertices=cut_verticies)
    #path2 = tri.path.path.Path3D(entities=[line_range2], vertices=vertex_positions[boundary])
    print("path: ", path1)
    scene = tri.Scene(trimesh)
    scene.add_geometry(path1)
    #scene.add_geometry(path2)

    print("vertex_pos shape: ", vertex_positions.shape) 
    print("vertex_pos head: \n", vertex_positions[:10])
    print("indicies shape: ", indicies.shape)
    print("indicies head: \n", indicies[:10])
    print("boundary head: \n", initial_cut[:10])
    print("boundary points: \n", cut_verticies[:10] )
    print("boundary lines head: \n", np.array(tuple(zip(cut_verticies[:-1][:10], cut_verticies[1:][:10]))))
    
    #boundary_verticies *= 0.90 * np.ones(boundary_verticies.shape)
    #plt.update_object(vertices=boundary_verticies)
    #plt.save("test.html")
    #plt
    #scene.show()

    display_cut(vertex_positions=vertex_positions, indicies=indicies)

    #display(data.to_html())


def cut_and_parameterize(M, p, n):
    values =  np.zeros((n , n, 3))
    normals = np.zeros((n, n, 3))

    #pcd = M.sample_points_uniformly(number_of_points=n*n)

