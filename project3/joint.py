from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np

class Joint:
    def __init__(self):
        self.__name = ""
        self.__parent = None
        self.__children = []
        self.__offset = []
