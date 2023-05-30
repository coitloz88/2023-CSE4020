'''
bvh 파일 parser
'''
from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np
from joint import Joint

class Loader:
    def __init__(self):
        self.__filepath = ""
        self.__vertices = []
        self.__vao = None
        self.__is_fill = False

    @property
    def vao(self):
        return self.__vao

    @property
    def is_fill(self):
        return self.__is_fill

    def change_is_fill(self, new_is_fill):
        self.__is_fill = new_is_fill

    def parse_bvh(self, filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()

            for line in lines:
                words = line.split()

                if len(words) < 1:
                    continue
                
                '''
                Hierarchy에서 가능한 옵션
                - ROOT: Root node를 가리킴
                - {: 새로운 노드의 시작을 가리킴
                - OFFSET: static data인 translational data를 가리킴
                - CHANNELS: dynamic data인 Rotational data를 가리키기 위함
                - JOINT: 해당 Joint의 이름을 나타냄
                - }: 중괄호가 닫힐 때, 해당 노드는 괄호 상위 노드의 자식임을 가리키게 됨
                     직전의 노드가 부모가 아니라. 상위 노드가 부모
                '''
                

                '''
                Motion에서 가능한 옵션
                - Frames: 총 pose의 개수
                - Frame Time: FPS
                - 이외의 숫자 옵션: 각 column의 offset을 저장함
                '''
    
    def prepare_vao_bvh(self):
        vertices = glm.array(self.__vertices)

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

        self.__vao = VAO

        return VAO

    def draw_mesh(self, MVP, MVP_loc):
        glBindVertexArray(self.__vao)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
        glDrawArrays(GL_TRIANGLES, 0, len(self.__vertex_indices))

