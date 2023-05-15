from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np
from node import Node
from load_obj import Mesh
import os

class ModelLoader:
    def __init__(self):
        self.__is_animating = False
        self.__is_fill = False

        self.__filepath = []
        self.__meshes = []

        current_dir, file = os.path.split(os.path.abspath(__file__))

        self.__animating_files = [
            os.path.join(current_dir, 'animating-models', 'pikachu.obj'),
            os.path.join(current_dir, 'animating-models', 'zubat.obj'),
            os.path.join(current_dir, 'animating-models', 'diglett.obj'),
            os.path.join(current_dir, 'animating-models', 'pokeball.obj'),
            os.path.join(current_dir, 'animating-models', 'pokeball.obj'),
            os.path.join(current_dir, 'animating-models', 'pokeball.obj'),
            os.path.join(current_dir, 'animating-models', 'pokeball.obj'),
        ]

        self.__animating_nodes = []

    @property
    def is_animating(self):
        return self.__is_animating
    
    @property
    def is_fill(self):
        return self.__is_fill

    def change_animating_mode(self, flag):
        self.__is_animating = flag

    def change_fill_mode(self):
        self.__is_fill = not self.__is_fill

    def is_prepared_for_animating(self):
        return len(self.__animating_nodes) > 0

    def prepare_animating(self):
        '''
        while 문 밖에서 일어나는 모든 일을 처리한다.
        vao 세팅, base 세팅 등.
        '''
        base = Node(None, glm.vec3(0.3, 0.3, 0.3))
        child1 = Node(base, glm.vec3(0.2, 0.2, 0.2))
        child2 = Node(base, glm.vec3(0.2, 0.2, 0.2))

        child1_1 = Node(child1, glm.vec3(0.0015, 0.0015, 0.0015))
        child1_2 = Node(child1, glm.vec3(0.0015, 0.0015, 0.0015))
        child2_1 = Node(child2, glm.vec3(0.0015, 0.0015, 0.0015))
        child2_2 = Node(child2, glm.vec3(0.0015, 0.0015, 0.0015))

        self.__animating_nodes.append(base)
        self.__animating_nodes.append(child1)
        self.__animating_nodes.append(child2)
        self.__animating_nodes.append(child1_1)
        self.__animating_nodes.append(child1_2)
        self.__animating_nodes.append(child2_1)
        self.__animating_nodes.append(child2_2)

        for file in self.__animating_files:
            mesh = Mesh()
            mesh.parse_obj_str(file, False)
            mesh.prepare_vao_mesh()
            self.__meshes.append(mesh)

        return self.__animating_nodes
        
    def draw_hierarchical(self, MVP, MVP_loc, M_loc):
        t = glfwGetTime()

        self.__animating_nodes[0].set_transform(glm.translate(glm.vec3(0.4 * glm.sin(t), -0.04, 0.4 * glm.cos(t))))
        self.__animating_nodes[1].set_transform(glm.rotate(t, glm.vec3(0, 1, 0)) * glm.translate(glm.vec3(0, 1.0 + 0.05 * glm.sin(t), -2.5)))
        self.__animating_nodes[2].set_transform(glm.translate(glm.vec3(1.5 * glm.cos(t), 0.01, 1.5)))
        self.__animating_nodes[3].set_transform(glm.rotate(t, glm.vec3(0,1,0)) * glm.translate(glm.vec3(0.55, 0.7 + 0.5 * glm.sin(t), 0.55)))
        self.__animating_nodes[4].set_transform(glm.rotate(t, glm.vec3(0,1,0)) * glm.translate(glm.vec3(-0.55, 0.7 + 0.5 * glm.cos(t), -0.55)))
        self.__animating_nodes[5].set_transform(glm.rotate(t, glm.vec3(0,1,0)) * glm.translate(glm.vec3(0.5, 0.5 + 0.25 * glm.sin(t), -0.5)))
        self.__animating_nodes[6].set_transform(glm.rotate(t, glm.vec3(0,1,0)) * glm.translate(glm.vec3(-0.5, 0.5 + 0.25 * glm.cos(t), 0.5)))

        self.__animating_nodes[0].update_tree_global_transform()

        self.draw_nodes(MVP, MVP_loc, M_loc)

    def draw_nodes(self, MVP, MVP_loc, M_loc):        
        nodes_cnt = len(self.__meshes)
        for idx in range(nodes_cnt):
            self.__meshes[idx].draw_node(self.__animating_nodes[idx], MVP, MVP_loc, M_loc)



