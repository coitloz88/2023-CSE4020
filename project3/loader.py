'''
bvh 파일 parser
'''
from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np
from node import Node as Joint

class Loader:
    def __init__(self):
        self.__filepath = ""
        self.__root = None
        self.__is_fill = False

    @property
    def is_fill(self):
        return self.__is_fill

    def change_is_fill(self, new_is_fill):
        self.__is_fill = new_is_fill

    def parse_bvh(self, filepath):
        print("call parse bvh")
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
            parent_joint = None
            current_joint = None

            for line in lines:
                words = line.split()

                if len(words) < 1:
                    continue
                
                '''
                Hierarchy에서 가능한 옵션
                - ROOT: Root node를 가리킴
                - {: 새로운 하위 노드의 시작을 가리킴
                - OFFSET: static data인 translational data를 가리킴
                - CHANNELS: dynamic data인 Rotational data를 가리키기 위함
                - JOINT: 해당 Joint의 이름을 나타냄
                - }: 중괄호가 닫힐 때, 해당 노드는 괄호 상위 노드의 자식임을 가리키게 됨
                     직전의 노드가 부모가 아니라. 상위 노드가 부모
                - End Site: End effector
                '''
                
                if words[0] == '{':
                    parent_joint = current_joint

                elif words[0] == '}':
                    current_joint = current_joint.parent
                    parent_joint = current_joint

                elif words[0] == 'OFFSET':
                    current_joint.set_link_transformation(glm.translate(glm.vec3(float(words[1]), float(words[2]), float(words[3]))))

                elif words[0] == 'CHANNELS':
                    total_length = int(words[1])
                    for i in range(total_length):
                        current_joint.channels.append(words[i + 2])
                    print("pass " + current_joint.joint_name)

                elif words[0] == 'ROOT' or words[0] == 'JOINT' or words[0] == 'End':
                    current_joint = Joint(parent_joint, words[1], glm.vec3(1,1,1)) # TODO: End site는 이름 설정 X

                    if words[0] == 'ROOT':
                        self.__root = current_joint

                '''
                Motion에서 가능한 옵션
                - Frames: 총 pose의 개수
                - Frame Time: FPS
                - 이외의 숫자 옵션: 각 column의 offset을 저장함
                '''
        
        self.__filepath = filepath

    def draw_animation(self):
        '''
        그려야하는 cube 개수만큼(root + joint 개수만큼),
        joint 배열을 순회하면서 해당 joint node의 draw를 호출
        '''
        pass
