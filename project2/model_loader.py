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
            "C:\\Users\\loveg\\OneDrive - 한양대학교\\바탕 화면\\Computer Graphics\\2023-CSE4020\\project2\\animating-models\\pikachu.obj",
            "C:\\Users\\loveg\\OneDrive - 한양대학교\\바탕 화면\\Computer Graphics\\2023-CSE4020\\project2\\Project2-sample-objs\\cylinder-tri.obj", 
            "C:\\Users\\loveg\\OneDrive - 한양대학교\\바탕 화면\\Computer Graphics\\2023-CSE4020\\project2\\Project2-sample-objs\\sphere-tri-quad.obj",
            "C:\\Users\\loveg\\OneDrive - 한양대학교\\바탕 화면\\Computer Graphics\\2023-CSE4020\\project2\\Project2-sample-objs\\cube-tri-quad.obj",
            "C:\\Users\\loveg\\OneDrive - 한양대학교\\바탕 화면\\Computer Graphics\\2023-CSE4020\\project2\\Project2-sample-objs\\cube-tri.obj",
            ".\\project2\\animating-models\\zubat.obj"
        ]

        self.__animating_nodes = {}

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

    def prepare_animating(self):
        '''
        while 문 밖에서 일어나는 모든 일을 처리한다.
        vao 세팅, base 세팅 등.
        '''
        base = Node(None, glm.vec3(0.7, 0.7, 0.7), glm.vec3(1., 1., 1.))
        circle_1 = Node(base, glm.vec3(0.5, 0.5, 0.5), glm.vec3(1., 0.5, 0.5))
        circle_2 = Node(base, glm.vec3(0.3, 0.3, 0.3), glm.vec3(1., 0.5, 0.5))

        cube_1 = Node(circle_1, glm.vec3(0.2, 0.3, 0.4), glm.vec3(1., 0.5, 0.5))
        cube_2 = Node(circle_2, glm.vec3(0.6, 0.6, 0.6), glm.vec3(1., 0.5, 0.5))
        jubat = Node(circle_1, glm.vec3(0.3, 0.3, 0.3), glm.vec3(1., 0.5, 0.5))

        self.__animating_nodes['base'] = base
        self.__animating_nodes['circle1'] = circle_1
        self.__animating_nodes['circle2'] = circle_2
        self.__animating_nodes['cube1'] = cube_1
        self.__animating_nodes['cube2'] = cube_2
        self.__animating_nodes['jubat'] = jubat

        for file in self.__animating_files:
            mesh = Mesh()
            mesh.parse_obj_str(file)
            mesh.prepare_vao_mesh()
            self.__meshes.append(mesh)

        return self.__animating_nodes
        
    def draw_hierarchical(self, MVP, MVP_loc):
        t = glfwGetTime()
        base = self.__animating_nodes.get('base')
            
        base.set_transform(glm.translate(glm.vec3(glm.sin(t),0,0)))
        self.__animating_nodes.get('circle1').set_transform(glm.rotate(t, glm.vec3(0,0,1)) * glm.translate(glm.vec3(.5, 0, .01)))
        self.__animating_nodes.get('circle2').set_transform(glm.translate(glm.vec3(-2.0, 2.0, -0.2)) * glm.rotate(2*t, glm.vec3(0,1,0)))
        self.__animating_nodes.get('cube1').set_transform(glm.translate(glm.vec3(glm.sin(t),0,0)))
        self.__animating_nodes.get('cube2').set_transform(glm.rotate(t, glm.vec3(0,0,1)))
        self.__animating_nodes.get('jubat').set_transform(glm.rotate(-t, glm.vec3(0,1,0)) * glm.translate(glm.vec3(1.0, 1.5, 0.5)))

        base.update_tree_global_transform()

        self.draw_nodes(MVP, MVP_loc)

    def draw_nodes(self, MVP, MVP_loc):        
        self.__meshes[0].draw_node(self.__animating_nodes.get('base'), MVP, MVP_loc)
        self.__meshes[1].draw_node(self.__animating_nodes.get('circle1'), MVP, MVP_loc)
        self.__meshes[2].draw_node(self.__animating_nodes.get('circle2'), MVP, MVP_loc)
        self.__meshes[3].draw_node(self.__animating_nodes.get('cube1'), MVP, MVP_loc)
        self.__meshes[4].draw_node(self.__animating_nodes.get('cube2'), MVP, MVP_loc)
        self.__meshes[5].draw_node(self.__animating_nodes.get('jubat'), MVP, MVP_loc)



