from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

class Node:
    def __init__(self, parent, node_name, color):
        # hierarchy
        self.parent = parent
        self.children = []
        if parent is not None:
            parent.children.append(self)

        # link transform (static data)
        self.link_transform_from_parent = glm.mat4() # translation matrix
        
        # joint transform (dynamic data)
        self.channels = [] 
        self.joint_transform = []

        # global transformation matrix for calculating
        self.global_transform = glm.mat4()
        # color
        self.color = color

        # name
        self.joint_name = node_name

        # calculated vao for each node
        self.vao_line = None
        self.vao_box = None

    def set_link_transformation(self, link_transformation):
        self.link_transform_from_parent = link_transformation

    def append_joint_transform(self, joint_transforms):
        T_x = 0
        T_y = 0
        T_z = 0
        R = glm.mat4()

        for i, joint_transform in enumerate(joint_transforms):
            channel_i = self.channels[i].lower()
            if channel_i == 'xposition':
                T_x = float(joint_transform)
            elif channel_i == 'yposition':
                T_y = float(joint_transform)
            elif channel_i == 'zposition':
                T_z = float(joint_transform)
            elif channel_i == 'xrotation':
                R = R * glm.rotate(glm.radians(float(joint_transform)), (1, 0, 0))
            elif channel_i == 'yrotation':
                R = R * glm.rotate(glm.radians(float(joint_transform)), (0, 1, 0))
            elif channel_i == 'zrotation':
                R = R * glm.rotate(glm.radians(float(joint_transform)), (0, 0, 1))

        self.joint_transform.append(glm.translate(glm.vec3(T_x, T_y, T_z)) * R)

    def get_global_transform(self):
        return self.global_transform
    
    def get_color(self):
        return self.color
    
    def update_tree_global_transform_skeleton(self):
        if self.parent is not None:
            self.global_transform = self.parent.get_global_transform() * self.link_transform_from_parent
        else:
            self.global_transform = self.link_transform_from_parent

        for child in self.children:
            child.update_tree_global_transform_skeleton()
    
    def update_tree_global_transform(self, frame):
        if self.parent is not None:
            self.global_transform = self.parent.get_global_transform() * self.link_transform_from_parent * self.joint_transform[frame]
        else:
            self.global_transform = self.link_transform_from_parent * self.joint_transform[frame]

        for child in self.children:
            child.update_tree_global_transform(frame)

    def prepare_vao_line(self):
        # prepare vertex data (in main memory)
        vertices = glm.array(glm.float32,
            # position        # color
            0.0, 0.0, 0.0,  1.0, 0.5, 1.0, # line start
            self.link_transform_from_parent[3].x, self.link_transform_from_parent[3].y, self.link_transform_from_parent[3].z,  1.0, 0.5, 1.0, # line end(each of them is offset, xyz value)
        )

        # create and activate VAO (vertex array object)
        VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
        glBindVertexArray(VAO)      # activate VAO

        # create and activate VBO (vertex buffer object)
        VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
        glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

        # copy vertex data to VBO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

        # configure vertex positions
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
        glEnableVertexAttribArray(0)

        # configure vertex colors
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(1)

        self.vao_line = VAO
    
    def prepare_vao_box(self):
        # prepare vertex data (in main memory)
        # 36 vertices for 12 triangles
        thickness = 0.05

        offset_x = self.link_transform_from_parent[3].x
        offset_y = self.link_transform_from_parent[3].y
        offset_z = self.link_transform_from_parent[3].z

        # offset이 y방향만 있는게 아니라 x, y, z 다 있으므로 그걸 고려해줘야함 
        height = glm.sqrt(glm.pow(offset_x, 2) + glm.pow(offset_y, 2) + glm.pow(offset_z, 2))

        cuboid_vertices = [
            [-thickness, height, thickness], # v0
            [thickness, height, thickness], # v1
            [thickness, 0, thickness], # v2
            [-thickness, 0,  thickness], # v3
            [-thickness , height, -thickness], # v4
            [thickness, height, -thickness], # v5
            [thickness, 0, -thickness], # v6
            [-thickness, 0, -thickness], # v7
        ]

        for idx, cuboid_vertex in enumerate(cuboid_vertices):
            if offset_x == 0 and offset_z == 0:
                if offset_y < 0:
                    cuboid_vertices[idx][1] *= -1
            else:
                offset_vector = glm.normalize(glm.vec3(offset_x, offset_y, offset_z))
                normal_vector = glm.normalize(glm.cross(glm.vec3(0, 1, 0), offset_vector))
                cos_theta = glm.dot(glm.vec3(0, 1, 0), offset_vector)

                R = glm.rotate(glm.acos(cos_theta), normal_vector)
                cuboid_vertices[idx] = R * cuboid_vertex

        cuboid_indices = [
            [0,2,1],
            [0,3,2],
            [4,5,6],
            [4,6,7],
            [0,1,5],
            [0,5,4],
            [3,6,2],
            [3,7,6],
            [1,2,6],
            [1,6,5],
            [0,7,3],
            [0,4,7],
        ]
        
        color = [1.0, 0.5, 1.0]

        vertices = []

        for idx, cuboid_index in enumerate(cuboid_indices):
            vector1 = glm.vec3(cuboid_vertices[cuboid_index[1]]) - glm.vec3(cuboid_vertices[cuboid_index[0]])
            vector2 = glm.vec3(cuboid_vertices[cuboid_index[2]]) - glm.vec3(cuboid_vertices[cuboid_index[0]])
            one_vnormal = glm.normalize(glm.cross(vector1, vector2))
            for index in cuboid_index:
                vertices.append([cuboid_vertices[index][0], cuboid_vertices[index][1], cuboid_vertices[index][2], color[0], color[1], color[2], one_vnormal[0], one_vnormal[1], one_vnormal[2]])

        vertices = np.concatenate(np.array(vertices, dtype='f4'))
        vertices = glm.array(vertices)

        # create and activate VAO (vertex array object)
        VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
        glBindVertexArray(VAO)      # activate VAO

        # create and activate VBO (vertex buffer object)
        VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
        glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

        # copy vertex data to VBO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

        # configure vertex positions
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * glm.sizeof(glm.float32), None)
        glEnableVertexAttribArray(0)

        # configure vertex color
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(1)

        # configure vertex normal
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * glm.sizeof(glm.float32), ctypes.c_void_p(6*glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(2)

        self.vao_box = VAO

    def draw_node_line(self, VP, MVP_loc, color_loc):
        MVP = glm.mat4()

        if self.parent is not None:
            MVP = VP * self.parent.get_global_transform()
        else:
            MVP = VP * self.get_global_transform()
        color = self.get_color()

        glBindVertexArray(self.vao_line)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
        glUniform3f(color_loc, color.r, color.g, color.b)
        glDrawArrays(GL_LINES, 0, 2)

    def draw_node_box(self, VP, MVP_loc, color_loc, M_loc):
        M = glm.mat4()
        if self.parent is not None:
            M = self.parent.get_global_transform()
        else:
            M = self.get_global_transform()

        MVP = VP * M
        color = self.get_color()

        glBindVertexArray(self.vao_box)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))        
        glUniformMatrix4fv(M_loc, 1, GL_FALSE, glm.value_ptr(M))
        glUniform3f(color_loc, color.r, color.g, color.b)
        glDrawArrays(GL_TRIANGLES, 0, 36)