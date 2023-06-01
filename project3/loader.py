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
        self.__is_animating = False

        self.frames = 0
        self.frame_time = 1
        
        # for debugging...
        self.__total_frame_cnt = 0
        self.__channel_cnt = 0

    @property
    def root(self):
        return self.__root

    @property
    def is_fill(self):
        return self.__is_fill
    
    @property
    def is_animating(self):
        return self.__is_animating

    def is_float(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def change_is_fill(self, new_is_fill):
        self.__is_fill = new_is_fill

    def change_is_animating(self):
        self.__is_animating = not self.__is_animating

    def parse_channel_data(self, channel_data):
        '''
        DFS로 root부터 돌면서 channel data를 파싱하여 넣어줌
        한 프레임에 대한 channel data를 파싱
        '''
        visited = []
        channel_stack = [self.__root]

        data_cnt = 0

        while channel_stack:
            current_node = channel_stack.pop()
            if current_node not in visited:
                visited.append(current_node)
                channel_data_per_frame = channel_data[data_cnt:data_cnt + len(current_node.channels)]
                data_cnt += len(current_node.channels)
                current_node.append_joint_transform(channel_data_per_frame)

                for child in reversed(current_node.children):
                    channel_stack.append(child)

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
                
                # Hierarchy에서 가능한 옵션
                # - ROOT: Root node를 가리킴
                # - {: 새로운 하위 노드의 시작을 가리킴
                # - OFFSET: static data인 translational data를 가리킴
                # - CHANNELS: dynamic data인 Rotational data를 가리키기 위함
                # - JOINT: 해당 Joint의 이름을 나타냄
                # - }: 중괄호가 닫힐 때, 해당 노드는 괄호 상위 노드의 자식임을 가리키게 됨
                #      직전의 노드가 부모가 아니라. 상위 노드가 부모
                # - End Site: End effector
                
                if words[0] == '{':
                    parent_joint = current_joint

                elif words[0] == '}':
                    current_joint = current_joint.parent
                    parent_joint = current_joint

                elif words[0] == 'OFFSET':
                    current_joint.set_link_transformation(glm.translate(glm.vec3(float(words[1]), float(words[2]), float(words[3]))))

                elif words[0] == 'CHANNELS':
                    total_length = int(words[1])
                    self.__channel_cnt += total_length
                    for i in range(total_length):
                        current_joint.channels.append(words[i + 2])

                elif words[0] == 'ROOT' or words[0] == 'JOINT' or words[0] == 'End':
                    current_joint = Joint(parent_joint, words[1], glm.vec3(1,1,1)) # TODO: End site는 이름 설정 X

                    if words[0] == 'ROOT':
                        self.__root = current_joint

                # Motion에서 가능한 옵션
                # - Frames: 총 pose의 개수
                # - Frame Time: FPS
                # - 이외의 숫자 옵션: 각 column의 offset을 저장함
 
                elif words[0] == 'Frames:':
                    self.frames = int(words[1])
                
                elif words[0] == 'Frame' and words[1] == 'Time:':
                    self.frame_time = float(words[2])
                
                elif self.is_float(words[0]):
                    self.__total_frame_cnt += 1
                    self.parse_channel_data(words)

        self.__filepath = filepath

    def prepare_vaos_line(self):
        visited = []
        channel_stack = [self.__root]

        while channel_stack:
            current_node = channel_stack.pop()
            if current_node not in visited:
                visited.append(current_node)
                current_node.prepare_vao_line()

                for child in reversed(current_node.children):
                    channel_stack.append(child)
        
        self.__root.update_tree_global_transform(0)

    def draw_animation(self, VP, MVP_loc, color_loc, frame):
        '''
        그려야하는 cube 개수만큼(root + joint 개수만큼),
        joint 배열을 순회하면서 해당 joint node의 draw를 호출
        '''
        if self.__is_animating:
            self.__root.update_tree_global_transform(frame)

        visited = []
        channel_stack = [self.__root]

        while channel_stack:
            current_node = channel_stack.pop()
            if current_node not in visited:
                visited.append(current_node)
                current_node.draw_node(VP, MVP_loc, color_loc)

                for child in reversed(current_node.children):
                    channel_stack.append(child)
