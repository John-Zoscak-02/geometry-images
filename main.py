import numpy as np
import random
import trimesh as tri
import igl
from itertools import repeat

SEED = 42
random.seed(SEED)

data_dir = "data/"
files = [
#    "beetle.obj",
    "ChineseLion.obj",
    #"Femur.obj",
    #"Foot.obj",
    #"happy.obj",
    #"Hat.obj",
    "HumanBrain.obj",
    #"HumanFace.obj",
    #"Nefertiti.obj",
    "OldMan.obj",
    #"rocker-arm.obj",
    "spot_triangulated.obj"
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
        cut_vertices = vertex_positions[cut]
        range = np.arange(0, len(cut))
        line_range= tri.path.entities.Line(points=range,color=np.array([[255,0,0,255]]))
        path1 = tri.path.path.Path3D(entities=[line_range], vertices=cut_vertices)
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

def remove_triangles_adjacent_to_path(indicies, cut):
    #trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies)
    for sub_cut in cut:
        if (sub_cut[0] != sub_cut[-1]): 
            rmi = set()
            for i in range(len(sub_cut)):
                v = sub_cut[i]
                adjacent_triangle_indicies = np.where(np.sum(indicies==v, axis=1)>0)[0]
                rmi.update(adjacent_triangle_indicies)
            indicies = np.delete(indicies, list(rmi), axis=0)
            #edges = get_edges_from_path(sub_cut)
            #adj_index = trimesh.face_adjacency_edges_tree.query(edges)[1]
            #print(adj_index)

            #faces = trimesh.face_adjacency[adj_index]
            
            #print("indicies before: ", indicies.shape)
            #indicies = np.delete(trimesh.faces, faces, axis=0)
            #print("indicies after: ", indicies.shape)
    
    return indicies

def display_parameterized_geometry(vertex_positions, indicies, colors) :
    trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies) 
    trimesh.visual.face_colors = colors
    scene = tri.Scene(trimesh)
    scene.show(flags = {'wireframe':True, 'cull': False}, line_settings={'line_width': 0.5} )

if __name__ == '__main__' :
    for file in files:
        num_cuts = int(input("Number of additional cuts: "))

        #================================== Data analysis ================================#
        # Read in the vertex positions of the geometry
        # Read in the indicies of the triangle mesh 
        vertex_positions, indicies = igl.read_triangle_mesh("%s%s"%(data_dir, file))

        print("filename: ", file)
        print("vertex_pos shape: ", vertex_positions.shape) 
        #print("vertex_pos head: \n", vertex_positions[:10])
        print("indicies shape: ", indicies.shape)
        #print("indicies head: \n", indicies[:10])
        #==================================#

        #================================== Display Cut ================================#
        boundary = igl.boundary_loop(indicies)
        #print("boundary length: ", len(boundary))

        if len(boundary) == 0: num_cuts+=1

        curvature = igl.gaussian_curvature(vertex_positions, indicies)
        print("Gaussian curvature: ", curvature.shape)
        curvature = np.absolute(curvature)
        max_inds = np.argpartition(curvature, -(num_cuts+len(boundary)))[:num_cuts]
        print(max_inds)

        for max_ind in max_inds:
            seed_triangle_idx = np.where(np.sum(indicies==max_ind, axis=1)>0)[0]
            seed_removed_indicies = np.delete(indicies, seed_triangle_idx, axis=0)

        cut = igl.cut_to_disk(seed_removed_indicies)

        for sub_cut in cut:
            cut_vertices = vertex_positions[sub_cut]
            print("cut head: \n", sub_cut[:1], sub_cut[-1:], "\nlen: ", len(sub_cut))
            #print("cut points: \n", cut_vertices[:1], cut_vertices[-1:])
            #print("cut lines head: \n", np.array(tuple(zi(cut_vertices[:-1][:1], cut_vertices[1:][:1]))), np.array(tuple(zip(cut_vertices[:-1][:1], cut_vertices[1:][-1:])))

        colors = display_cut(vertex_positions=vertex_positions, indicies=indicies, full_cut=cut)
        #==================================#
        
        #================================== Display simple 2D parameterization ================================#
        #bnd = igl.boundary_loop(indicies)
        ##bnd = combine_cut(cut)
        ##print(bnd)
        ##colors = display_cut(vertex_positions=vertex_positions, indicies=indicies, full_cut=[bnd])
        ##bnd_uv = igl.map_vertices_to_circle(vertex_positions, bnd)
        ##print(len(bnd))
        ##print((bnd_uv))
        ##bnd_uv = np.array([circle_to_square(p[0],p[1]) for p in bnd_uv ])
        ##print(bnd_uv)

        #bnd_uv = []
        #bnd_uv.extend(zip(repeat(1.0), np.linspace(0, 1, int(len(bnd)/8), endpoint=False)))
        #bnd_uv.extend(zip(np.linspace(1, -1, int(len(bnd)/4 + len(bnd)%4), endpoint=False), repeat(1.0)))
        #bnd_uv.extend(zip(repeat(-1.0), np.linspace(1, -1, int(len(bnd)/4), endpoint=False)))
        #bnd_uv.extend(zip(np.linspace(-1, 1, len(bnd)-len(bnd_uv)-int(len(bnd)/8), endpoint=False), repeat(-1.0)))
        #bnd_uv.extend(zip(repeat(1.0), np.linspace(-1, 0, int(len(bnd)/8), endpoint=False)))
        #bnd_uv = np.array(bnd_uv)

        ## Create a harmonic parameterization for the inner vertices of the parameterized representation
        #print("running harmonic")
        #uv = igl.harmonic(vertex_positions, indicies, bnd, bnd_uv, 1)
        ##uv = igl.lscm(vertex_positions, indicies, bnd, bnd_uv)
        ##print(uv_h)
        #print(uv)
        #print("ran harmonic")
        #vertex_positions_p = np.hstack([uv, np.zeros((uv.shape[0],1))])

        #display_parameterized_geometry(vertex_positions=vertex_positions_p, indicies=indicies, colors=colors)
        #==================================#
        
        #================================== Trying combining the cut and doing cut_mesh ================================#
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
        #bnd=cut 
        #bnd_uv = []
        #bnd_uv.extend(zip(repeat(1.0), np.linspace(0, 1, int(len(bnd)/8), endpoint=False)))
        #bnd_uv.extend(zip(np.linspace(1, -1, int(len(bnd)/4 + len(bnd)%4), endpoint=False), repeat(1.0)))
        #bnd_uv.extend(zip(repeat(-1.0), np.linspace(1, -1, int(len(bnd)/4), endpoint=False)))
        #bnd_uv.extend(zip(np.linspace(-1, 1, len(bnd)-len(bnd_uv)-int(len(bnd)/8), endpoint=False), repeat(-1.0)))
        #bnd_uv.extend(zip(repeat(1.0), np.linspace(-1, 0, int(len(bnd)/8), endpoint=False)))
        #bnd_uv = np.array(bnd_uv)

        #uv = igl.harmonic(vcut, fcut, cut, bnd_uv,1)
        #vcut = np.hstack([uv, np.zeros((uv.shape[0], 1))])
        #display_parameterized_geometry(vcut, fcut, colors=colors)
        #==================================#

        #================================== Try removing adjacent triangles ================================#
        indicies = remove_triangles_adjacent_to_path(indicies, cut)
        trimesh = tri.Trimesh(vertices=vertex_positions, faces=indicies)
        trimesh.remove_unreferenced_vertices()
        vertex_positions = trimesh.vertices
        indicies = trimesh.faces
        #M = np.sum(np.mean(vertex_positions[indicies], axis=1), axis=1)
        #colors = tri.visual.interpolate(M, color_map='viridis')
        #trimesh.visual.face_colors = colors
        #scene = tri.Scene(trimesh)
        #scene.show(flags = {'cull': False})

        bnd = igl.boundary_loop(indicies)
        #bnd = combine_cut(cut)
        #print(bnd)
        colors = display_cut(vertex_positions=vertex_positions, indicies=indicies, full_cut=[bnd])
        #bnd_uv = igl.map_vertices_to_circle(vertex_positions, bnd)
        #print(len(bnd))
        #print((bnd_uv))
        #bnd_uv = np.array([circle_to_square(p[0],p[1]) for p in bnd_uv ])
        #print(bnd_uv)

        bnd_uv = []
        bnd_uv.extend(zip(repeat(1.0), np.linspace(0, 1, int(len(bnd)/8), endpoint=False)))
        bnd_uv.extend(zip(np.linspace(1, -1, int(len(bnd)/4 + len(bnd)%4), endpoint=False), repeat(1.0)))
        bnd_uv.extend(zip(repeat(-1.0), np.linspace(1, -1, int(len(bnd)/4), endpoint=False)))
        bnd_uv.extend(zip(np.linspace(-1, 1, len(bnd)-len(bnd_uv)-int(len(bnd)/8), endpoint=False), repeat(-1.0)))
        bnd_uv.extend(zip(repeat(1.0), np.linspace(-1, 0, int(len(bnd)/8), endpoint=False)))
        bnd_uv = np.array(bnd_uv)

        # Create a harmonic parameterization for the inner vertices of the parameterized representation
        print("running harmonic")
        uv = igl.harmonic(vertex_positions, indicies, bnd, bnd_uv, 1)
        #uv = igl.lscm(vertex_positions, indicies, bnd, bnd_uv)
        #print(uv_h)
        print(uv)
        print("ran harmonic")
        vertex_positions_p = np.hstack([uv, np.zeros((uv.shape[0],1))])

        display_parameterized_geometry(vertex_positions=vertex_positions_p, indicies=indicies, colors=colors)
        #==================================#

        #================================== Display non-wireframe parameterization ================================#
        #trimesh = tri.Trimesh(vertices=vertex_positions_p, faces=indicies) 
        #trimesh.visual.face_colors = colors
        #scene = tri.Scene(trimesh)
        #scene.show(flags = {'cull': False})
        #==================================#
