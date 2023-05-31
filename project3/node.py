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
        self.link_transform_from_parent = glm.mat4() # offset
        
        # joint transform (dynamic data)
        self.channels = [] 
        self.joint_transform = []

        # global transformation matrix for calculating
        self.global_transform = glm.mat4()
        # color
        self.color = color

        # name
        self.joint_name = node_name
    
    def set_link_transformation(self, link_transformation):
        self.link_transform_from_parent = link_transformation

    def append_joint_transform(self, joint_transforms):
        # TODO: 곱하는 순서가 position 먼저인지 rotation 먼저인지
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
    
    def update_tree_global_transform(self, frame):
        if self.parent is not None:
            self.global_transform = self.parent.get_global_transform() * self.link_transform_from_parent * self.joint_transform[frame]
        else:
            self.global_transform = self.link_transform_from_parent * self.joint_transform[frame]

        for child in self.children:
            child.update_tree_global_transform(frame)

    def draw_node(self, vao, VP, MVP_loc, color_loc):
        MVP = VP * self.get_global_transform()
        color = self.get_color()

        glBindVertexArray(vao)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
        glUniform3f(color_loc, color.r, color.g, color.b)
        glDrawArrays(GL_TRIANGLES, 0, 36)