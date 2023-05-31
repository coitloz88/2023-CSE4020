from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

class Node:
    def __init__(self, parent, link_transform_from_parent, color):
        # hierarchy
        self.parent = parent
        self.children = []
        if parent is not None:
            parent.children.append(self)

        # transform
        self.link_transform_from_parent = link_transform_from_parent
        self.joint_transform = glm.mat4()
        self.global_transform = glm.mat4()

        # color
        self.color = color

    def set_joint_transform(self, joint_transform):
        self.joint_transform = joint_transform

    def update_tree_global_transform(self):
        if self.parent is not None:
            self.global_transform = self.parent.get_global_transform() * self.link_transform_from_parent * self.joint_transform
        else:
            self.global_transform = self.link_transform_from_parent * self.joint_transform

        for child in self.children:
            child.update_tree_global_transform()

    def get_global_transform(self):
        return self.global_transform
    
    def get_color(self):
        return self.color
    
    def draw_node(self, vao, VP, MVP_loc, color_loc):
        MVP = VP * self.get_global_transform()
        color = self.get_color()

        glBindVertexArray(vao)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
        glUniform3f(color_loc, color.r, color.g, color.b)
        glDrawArrays(GL_TRIANGLES, 0, 36)

