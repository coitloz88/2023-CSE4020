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
        self.__is_animating = False

        self.__filepath = ""
        self.__vertices = []
        self.__vertex_indices = []

        self.__vao = None

    @property
    def vao(self):
        return self.__vao
    
    @property
    def is_animating(self):
        return self.__is_animating
    
    def change_animating_mode(self, flag):
        self.__is_animating = flag

    def parse_obj_str(self, filepath, show_face_cnt = True):
        faces_cnt = {}

        with open(filepath, 'r') as f:
            lines = f.readlines()

            tmp_vertex_pos = []
            tmp_vertex_colors = []
            tmp_vnormals = []
            
            face_vertex_indices = []
            face_vnormal_indices = []

            for line in lines:
                words = line.split()
                if len(words) < 1:
                    continue

                # 'v': parse the vertex data
                if words[0] == 'v':
                    vertex = [float(words[1]), float(words[2]), float(words[3])]
                    tmp_vertex_pos.append(vertex)

                    if(len(words) == 7):
                        color = [float(words[4]), float(words[5]), float(words[6])]
                        tmp_vertex_colors.append(color)
                    else:
                        tmp_vertex_colors.append([1., 1., 1.])
                
                # 'vn': parse the vertex normal vector data
                elif words[0] == 'vn':
                    vnormal = [float(words[1]), float(words[2]), float(words[3])]
                    tmp_vnormals.append(vnormal)
                
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
            
            vbo_arr_data = []
            used_vertices_len = len(face_vertex_indices)
            for idx in range(used_vertices_len):
                vbo_arr_data.append(tmp_vertex_pos[face_vertex_indices[idx]])
                vbo_arr_data.append(tmp_vertex_colors[face_vertex_indices[idx]])
                vbo_arr_data.append(tmp_vnormals[face_vnormal_indices[idx]])

            self.__filepath = filepath
            self.__vertices = np.concatenate(np.array(vbo_arr_data, dtype='f4'))
            self.__vertex_indices = np.array(face_vertex_indices, dtype='u4')

        total_faces_cnt = sum(faces_cnt.values())
        faces_3 = int(faces_cnt.get(3) or 0)
        faces_4 = int(faces_cnt.get(4) or 0)

        if show_face_cnt:
            print("------------------------")
            print('obj file name: ' + self.__filepath.split('\\')[-1])
            print('total number of faces: ' + str(total_faces_cnt)) # TODO: total number of 'f'
            print('number of faces with 3 vertices: ' + str(faces_3))
            print('number of faces with 4 vertices: ' + str(faces_4))
            print('number of faces with more than 4 vertices: ' + str(total_faces_cnt - faces_4 - faces_3))
    
    def prepare_vao_mesh(self):
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
            
    def draw_node(self, node, VP, MVP_loc, M_loc):
        M = node.get_global_transform() * glm.scale(node.get_scale())
        MVP = VP * M
        glBindVertexArray(self.__vao)
        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
        glUniformMatrix4fv(M_loc, 1, GL_FALSE, glm.value_ptr(M))
        glDrawArrays(GL_TRIANGLES, 0, len(self.__vertex_indices))