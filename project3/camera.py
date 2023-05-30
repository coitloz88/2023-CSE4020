'''
camera module
'''

from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

class Camera:
    def __init__(self):
        # angles
        self.__azimuth = 0.
        self.__elevation = 0.

        # projection mode: orthogonal, perspective
        self.__is_projection_ortho = False

        # geometric data of camera
        self.__pos = glm.vec3(0., 0., -1.)
        self.__front = glm.vec3(0., 0., 1.)
        self.__up = glm.vec3(0., 1., 0.)
    
    @property
    def azimuth(self):
        return self.__azimuth

    @property
    def elevation(self):
        return self.__elevation
    
    @property 
    def is_projection_ortho(self):
        return self.__is_projection_ortho
    
    @property
    def pos(self):
        return self.__pos
    
    @property
    def front(self):
        return self.__front
    
    @property
    def up(self):
        return self.__up

    def change_projection_mode(self):
        self.__is_projection_ortho = not self.__is_projection_ortho
    
    def rotate_orbit(self, x_offset, y_offset):
        self.__azimuth += x_offset
        self.__elevation += y_offset

        front = glm.vec3(
            np.sin(np.radians(self.__azimuth)) * np.cos(np.radians(self.__elevation)),
            np.sin(np.radians(self.__elevation)),
            np.cos(np.radians(self.__azimuth)) * np.cos(np.radians(self.__elevation))
        )
        self.__front = glm.normalize(front)

        up = glm.vec3(
            - np.sin(np.radians(self.__azimuth)) * np.sin(np.radians(self.__elevation)),
            np.cos(np.radians(self.__elevation)),
            -np.cos(np.radians(self.__azimuth)) * np.sin(np.radians(self.__elevation))        
        )
        self.__up = glm.normalize(up)

    def panning(self, moving_speed, x_offset, y_offset):
        self.__pos += self.__up * y_offset * moving_speed + glm.normalize(glm.cross(self.__up, self.__front)) * x_offset * moving_speed

    def scroll(self, moving_speed, y_offset):
        self.__pos += self.__front * moving_speed * y_offset