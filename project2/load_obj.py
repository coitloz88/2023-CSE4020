'''
obj file을 로드해온다.
class가 parsing된 obj vector 정보 및 file path를 들고 있다.

그래서, 나중에 새로운 파일을 drag & drop하는 경우, 
    이벤트 callback 함수에서
    1. 클래스 인스턴스의 멤버 변수를 변경해주고
    2. load_obj 등의 파싱 함수 등을 다 다시 불러와준다.
'''
from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np
    
class Mesh:
    def __init__(self):
        self.__filepath = ""
        self.__vertices = []
        self.__vnormals = []
        self.__vertex_indices = []
        self.__vnormal_indices = []

    def parse_obj_str(self, filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()

            tmp_vertices = []
            tmp_vnormals = []
            
            face_vertex_indices = []
            face_vnormal_indices = []

            out_vertices = []
            out_vnormals = []

            for line in lines:
                words = line.split()

                # 'v': parse the vertex data
                if words[0] == 'v':
                    vertex = glm.vec3(float(words[1]), float(words[2]), float(words[3]))
                    tmp_vertices.append(vertex)
                
                # 'vn': parse the vertex normal vector data
                elif words[0] == 'vn':
                    vnormal = glm.vec3(float(words[1]), float(words[2]), float(words[3]))
                    tmp_vnormals.append(vnormal)
                
                # 'f': parse the face data
                elif words[0] == 'f':
                    face_vertex_indices.append(int(words[1].split('//')[0]) - 1)
                    face_vertex_indices.append(int(words[2].split('//')[0]) - 1)
                    face_vertex_indices.append(int(words[3].split('//')[0]) - 1)

                    face_vnormal_indices.append(int(words[1].split('//')[1]) - 1)
                    face_vnormal_indices.append(int(words[2].split('//')[1]) - 1)
                    face_vnormal_indices.append(int(words[3].split('//')[1]) - 1)

                # ignore other input options, continue
                else:
                    continue

            # for each vertex of triangle
            vertex_indices_len = len(face_vertex_indices)

            for i in range(vertex_indices_len):
                # get the indices of its attributes
                vertex_index = face_vertex_indices[i]
                normal_index = face_vnormal_indices[i]

                # get the attributes thanks to the index
                vertex = glm.vec3(tmp_vertices[vertex_index])
                normal = glm.vec3(tmp_vnormals[normal_index])
                
                # put the attributes in buffers
                out_vertices.append(vertex)
                out_vnormals.append(normal)

            self.__filepath = filepath
            self.__vertices = np.array(tmp_vertices, np.float32)
            self.__vnormals = np.array(tmp_vnormals, np.float32)
            self.__vertex_indices = np.array(face_vertex_indices, np.uint32)
            self.__vnormal_indices = np.array(face_vnormal_indices, np.uint32)

        return {'vertices': out_vertices, 'normals': out_vnormals}
    
    def prepare_vao_mesh(self):
        vertices = glm.array(self.__vertices)
        indices = glm.array(self.__vertex_indices)

        # create and activate VAO (vertex array object)
        VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
        glBindVertexArray(VAO)      # activate VAO

        # create and activate VBO (vertex buffer object)
        VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
        glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

        # create and activate EBO (element buffer object)
        EBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)  # activate VBO as a vertex buffer object

        # copy vertex data to VBO
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

        # copy index data to EBO
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy index data to the currently bound index buffer

        # configure vertex positions
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * glm.sizeof(glm.float32), None)
        glEnableVertexAttribArray(0)

        return VAO
    
    def draw_mesh(self, vao, MVP, MVP_loc):
        glBindVertexArray(vao)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
        glDrawElements(GL_TRIANGLES, len(self.__vertex_indices), GL_UNSIGNED_INT, None)