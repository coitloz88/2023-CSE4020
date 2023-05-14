from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np
from node import Node
from load_obj import Mesh

class ModelLoader:
    def __init__(self):
        self.__is_animating = False
        self.__is_fill = False

        self.__filepath = []
        self.__meshes = []

        self.__animating_files = [
            ".\\project2\\animating-models\\pikachu.obj",            
            ".\\project2\\animating-models\\zubat.obj",
            ".\\project2\\animating-models\\diglett.obj",
            ".\\project2\\animating-models\\pokeball.obj",
            ".\\project2\\animating-models\\pokeball.obj",
            ".\\project2\\animating-models\\pokeball.obj",
            ".\\project2\\animating-models\\pokeball.obj",
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
        base = Node(None, glm.vec3(0.3, 0.3, 0.3), glm.vec3(1., 1., 1.))
        child1 = Node(base, glm.vec3(0.2, 0.2, 0.2), glm.vec3(1., 0.5, 0.5))
        child2 = Node(base, glm.vec3(0.2, 0.2, 0.2), glm.vec3(1., 0.5, 0.5))

        child1_1 = Node(child1, glm.vec3(0.0015, 0.0015, 0.0015), glm.vec3(1., 0.5, 0.5))
        child1_2 = Node(child1, glm.vec3(0.0015, 0.0015, 0.0015), glm.vec3(1., 0.5, 0.5))
        child2_1 = Node(child2, glm.vec3(0.0015, 0.0015, 0.0015), glm.vec3(1., 0.5, 0.5))
        child2_2 = Node(child2, glm.vec3(0.0015, 0.0015, 0.0015), glm.vec3(1., 0.5, 0.5))

        self.__animating_nodes.append(base)
        self.__animating_nodes.append(child1)
        self.__animating_nodes.append(child2)
        self.__animating_nodes.append(child1_1)
        self.__animating_nodes.append(child1_2)
        self.__animating_nodes.append(child2_1)
        self.__animating_nodes.append(child2_2)

        for file in self.__animating_files:
            mesh = Mesh()
            mesh.parse_obj_str(file)
            mesh.prepare_vao_mesh()
            self.__meshes.append(mesh)

        return self.__animating_nodes
        
    def draw_hierarchical(self, MVP, MVP_loc, M_loc):
        t = glfwGetTime()

        self.__animating_nodes[0].set_transform(glm.translate(glm.vec3(0.15 * glm.sin(t), -0.04, 0)))
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



