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
        self.__vertex_positions = []
        self.__vertex_normals = []
        self.__indices = []
        self.__VAO = None

    @property
    def VAO(self):
        return self.__VAO

    # filepath[i]
    def parse_obj_str(self, filepath):
        faces_cnt = {}

        with open(filepath, 'r') as f:
            lines = f.readlines()

            tmp_vertex_positions = []
            tmp_vertex_normals = []
            
            face_vertex_indices = []
            face_vnormal_indices = []

            for line in lines:
                words = line.split()

                # 'v': parse the vertex position data
                if words[0] == 'v':
                    # TODO: color 파싱
                    vertex = glm.vec3(float(words[1]), float(words[2]), float(words[3]))
                    tmp_vertex_positions.append(vertex)
                
                # 'vn': parse the vertex normal vector data
                elif words[0] == 'vn':
                    vnormal = glm.vec3(float(words[1]), float(words[2]), float(words[3]))
                    tmp_vertex_normals.append(vnormal)
                
                # 'f': parse the face data
                elif words[0] == 'f':
                    vertex_len = len(words) - 1
                    for i in range(1, vertex_len - 1):
                        # 삼각형 하나의 index가 i, j, k로 결정됨

                        # +1을 하는 이유: 0번째 요소는 'f'이기 때문
                        parsed_face_data = words[1].split('/')
                        # -1을 하는 이유: obj 파일에서 첫번째 인덱스는 0이 아닌 1부터 시작하는데,
                        # array에는 0부터 접근가능하기 때문              
                        face_vertex_indices.append(int(parsed_face_data[0]) - 1) 
                        face_vnormal_indices.append(int(parsed_face_data[2]) - 1)

                        parsed_face_data = words[i + 1].split('/')                            
                        face_vertex_indices.append(int(parsed_face_data[0]) - 1)
                        face_vnormal_indices.append(int(parsed_face_data[2]) - 1)

                        parsed_face_data = words[i + 2].split('/')                            
                        face_vertex_indices.append(int(parsed_face_data[0]) - 1)
                        face_vnormal_indices.append(int(parsed_face_data[2]) - 1)

                    if faces_cnt.get(vertex_len) is None:
                        faces_cnt[vertex_len] = 0

                    faces_cnt[vertex_len] = faces_cnt[vertex_len] + 1

                # ignore other input options, continue
                else:
                    continue

            self.__filepath = filepath[0]
            self.__vertices = np.array(tmp_vertex_positions, np.float32)
            self.__vnormals = np.array(tmp_vertex_normals, np.float32)
            self.__vertex_indices = np.array(face_vertex_indices, np.uint32)
            self.__vnormal_indices = np.array(face_vnormal_indices, np.uint32)

        total_faces_cnt = sum(faces_cnt.values())
        faces_3 = int(faces_cnt.get(3) or 0)
        faces_4 = int(faces_cnt.get(4) or 0)

        print("------------------------")
        print('obj file name: ' + self.__filepath.split('\\')[-1])
        print('total number of faces: ' + str(total_faces_cnt)) # TODO: total number of 'f'
        print('number of faces with 3 vertices: ' + str(faces_3))
        print('number of faces with 4 vertices: ' + str(faces_4))
        print('number of faces with more than 4 vertices: ' + str(total_faces_cnt - faces_4 - faces_3))
        print("------------------------")
    
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

        self.__vao = VAO

        return VAO
    
    def draw_mesh(self, MVP, MVP_loc):
        glBindVertexArray(self.__vao)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
        glDrawElements(GL_TRIANGLES, len(self.__vertex_indices), GL_UNSIGNED_INT, None)

    def draw_node(self, node, VP, MVP_loc):
        MVP = VP * node.get_global_transform() * glm.scale(node.get_scale())
        glBindVertexArray(self.__vao)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
        glDrawElements(GL_TRIANGLES, len(self.__vertex_indices), GL_UNSIGNED_INT, None)