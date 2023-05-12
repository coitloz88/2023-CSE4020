from OpenGL.GL import *
from glfw.GLFW import *
import glm
import ctypes
import numpy as np
from camera import Camera as cam
from load_obj import Mesh as mesh

g_cam = cam()
g_mesh = mesh()

g_screen_width, g_screen_height = 800, 800

# define mouse properties
last_mouse_x_pos, last_mouse_y_pos = 400, 400
mouse_pressed = {'left': False, 'right': False}

# now projection matrix P is a global variable so that it can be accessed from main() and framebuffer_size_callback()
g_P = glm.mat4()

# show frame
g_show_frame = False

g_vertex_shader_src = '''
#version 330 core

layout (location = 0) in vec3 vin_pos; 
layout (location = 1) in vec3 vin_normal;

out vec3 vout_surface_pos;
out vec3 vout_normal;

uniform mat4 MVP;
uniform mat4 M;

void main()
{
    // 3D points in homogeneous coordinates
    vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);
    gl_Position = MVP * p3D_in_hcoord;

    vout_surface_pos = vec3(M * vec4(vin_pos, 1));
    vout_normal = normalize( mat3(transpose(inverse(M))) * vin_normal);}
'''

g_fragment_shader_src = '''
#version 330 core

in vec3 vout_surface_pos;
in vec3 vout_normal;

out vec4 FragColor;

uniform vec3 view_pos;

void main()
{
    FragColor = vec4(1., 1., 1., 1.);
}
'''

def load_shaders(vertex_shader_source, fragment_shader_source):
    # build and compile our shader program
    # ------------------------------------
    
    # vertex shader 
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)    # create an empty shader object
    glShaderSource(vertex_shader, vertex_shader_source) # provide shader source code
    glCompileShader(vertex_shader)                      # compile the shader object
    
    # check for shader compile errors
    success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if (not success):
        infoLog = glGetShaderInfoLog(vertex_shader)
        print("ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" + infoLog.decode())
        
    # fragment shader
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)    # create an empty shader object
    glShaderSource(fragment_shader, fragment_shader_source) # provide shader source code
    glCompileShader(fragment_shader)                        # compile the shader object
    
    # check for shader compile errors
    success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if (not success):
        infoLog = glGetShaderInfoLog(fragment_shader)
        print("ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" + infoLog.decode())

    # link shaders
    shader_program = glCreateProgram()               # create an empty program object
    glAttachShader(shader_program, vertex_shader)    # attach the shader objects to the program object
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)                    # link the program object

    # check for linking errors
    success = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if (not success):
        infoLog = glGetProgramInfoLog(shader_program)
        print("ERROR::SHADER::PROGRAM::LINKING_FAILED\n" + infoLog.decode())
        
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program    # return the shader program

def key_callback(window, key, scancode, action, mods):
    global g_P, g_cam, g_screen_width, g_screen_height, g_show_frame, g_mesh
    if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    elif key == GLFW_KEY_V and action == GLFW_PRESS:
        g_cam.change_projection_mode()
        
        if g_cam.is_projection_ortho:
            ortho_height = 1.
            ortho_width = ortho_height * g_screen_width/g_screen_height
            g_P = glm.ortho(-ortho_width*.5,ortho_width*.5, -ortho_height*.5,ortho_height*.5, -10,10)
        else: 
            near = 0.5
            far = 20.0
            aspect_ratio = g_screen_width/g_screen_height
            g_P = glm.perspective(glm.radians(45.0), aspect_ratio, near, far)
    
    elif key == GLFW_KEY_F and action == GLFW_PRESS:
        g_show_frame = not g_show_frame
    
    elif key == GLFW_KEY_H and action == GLFW_PRESS:
        g_mesh.change_animating_mode(not g_mesh.is_animating)

    elif key == GLFW_KEY_Z and action == GLFW_PRESS:
        g_mesh.change_solid_mode()


def framebuffer_size_callback(window, width, height):
    global g_P, g_cam, g_screen_width, g_screen_height

    glViewport(0, 0, width, height)

    g_screen_width, g_screen_height = width, height

    if g_cam.is_projection_ortho:
        ortho_height = 10.
        ortho_width = ortho_height * width/height
        g_P = glm.ortho(-ortho_width*.5, ortho_width*.5, -ortho_height*.5, ortho_height*.5, -10,10)
    else: 
        near = 0.5
        far = 20.0
        aspect_ratio = width/height
        g_P = glm.perspective(glm.radians(45.0), aspect_ratio, near, far)

def mouse_button_callback(window, button, action, mods):

    # This function tells you if you are currently holding down the mouse button and, if so, what you are holding down.

    global mouse_pressed

    if action == GLFW_PRESS:
        if button == GLFW_MOUSE_BUTTON_LEFT:
            mouse_pressed['left'] = True
        elif button == GLFW_MOUSE_BUTTON_RIGHT:
            mouse_pressed['right'] = True
    elif action == GLFW_RELEASE:
            mouse_pressed = {'left': False, 'right': False}

def cursor_position_callback(window, x_pos, y_pos):

    # manage cursor position callback event

    global mouse_pressed, g_cam, last_mouse_x_pos, last_mouse_y_pos

    sensitivity = 0.02

    x_offset = (x_pos - last_mouse_x_pos) * sensitivity
    y_offset = (y_pos - last_mouse_y_pos) * sensitivity

    last_mouse_x_pos = x_pos
    last_mouse_y_pos = y_pos

    if mouse_pressed.get('left'):
        # rotate orbit
        g_cam.rotate_orbit(x_offset, y_offset)

    elif mouse_pressed.get('right'):
        # panning
        g_cam.panning(0.05, x_offset, y_offset)

def scroll_callback(window, x_scroll, y_scroll):
    global g_cam
    g_cam.scroll(0.05, y_scroll)

def drop_callback(window, filepath):
    global g_mesh

    g_mesh.change_animating_mode(False)
    g_mesh.parse_obj_str(filepath)
    g_mesh.prepare_vao_mesh_vertex()

def prepare_vao_grid():
    # prepare vertex data (in main memory)

    vertices = glm.array(glm.float32,
    -1.0, 0, -1, 1, 1, 1, -1.0, 0, 1, 1, 1, 1, -0.9, 0, -1, 1, 1, 1, -0.9, 0, 1, 1, 1, 1, -0.8, 0, -1, 1, 1, 1, -0.8, 0, 1, 1, 1, 1, -0.7, 0, -1, 1, 1, 1, -0.7, 0, 1, 1, 1, 1, -0.6, 0, -1, 1, 1, 1, -0.6, 0, 1, 1, 1, 1, -0.5, 0, -1, 1, 1, 1, -0.5, 0, 1, 1, 1, 1, -0.4, 0, -1, 1, 1, 1, -0.4, 0, 1, 1, 1, 1, -0.3, 0, -1, 1, 1, 1, -0.3, 0, 1, 1, 1, 1, -0.2, 0, -1, 1, 1, 1, -0.2, 0, 1, 1, 1, 1, -0.1, 0, -1, 1, 1, 1, -0.1, 0, 1, 1, 1, 1, 0.0, 0, -1, 1, 1, 1, 0.0, 0, 1, 1, 1, 1, 0.1, 0, -1, 1, 1, 1, 0.1, 0, 1, 1, 1, 1, 0.2, 0, -1, 1, 1, 1, 0.2, 0, 1, 1, 1, 1, 0.3, 0, -1, 1, 1, 1, 0.3, 0, 1, 1, 1, 1, 0.4, 0, -1, 1, 1, 1, 0.4, 0, 1, 1, 1, 1, 0.5, 0, -1, 1, 1, 1, 0.5, 0, 1, 1, 1, 1, 0.6, 0, -1, 1, 1, 1, 0.6, 0, 1, 1, 1, 1, 0.7, 0, -1, 1, 1, 1, 0.7, 0, 1, 1, 1, 1, 0.8, 0, -1, 1, 1, 1, 0.8, 0, 1, 1, 1, 1, 0.9, 0, -1, 1, 1, 1, 0.9, 0, 1, 1, 1, 1, 1.0, 0, -1, 1, 1, 1, 1.0, 0, 1, 1, 1, 1, -1, 0, -1.0, 1, 1, 1, 1, 0, -1.0, 1, 1, 1, -1, 0, -0.9, 1, 1, 1, 1, 0, -0.9, 1, 1, 1, -1, 0, -0.8, 1, 1, 1, 1, 0, -0.8, 1, 1, 1, -1, 0, -0.7, 1, 1, 1, 1, 0, -0.7, 1, 1, 1, -1, 0, -0.6, 1, 1, 1, 1, 0, -0.6, 1, 1, 1, -1, 0, -0.5, 1, 1, 1, 1, 0, -0.5, 1, 1, 1, -1, 0, -0.4, 1, 1, 1, 1, 0, -0.4, 1, 1, 1, -1, 0, -0.3, 1, 1, 1, 1, 0, -0.3, 1, 1, 1, -1, 0, -0.2, 1, 1, 1, 1, 0, -0.2, 1, 1, 1, -1, 0, -0.1, 1, 1, 1, 1, 0, -0.1, 1, 1, 1, -1, 0, 0.0, 1, 1, 1, 1, 0, 0.0, 1, 1, 1, -1, 0, 0.1, 1, 1, 1, 1, 0, 0.1, 1, 1, 1, -1, 0, 0.2, 1, 1, 1, 1, 0, 0.2, 1, 1, 1, -1, 0, 0.3, 1, 1, 1, 1, 0, 0.3, 1, 1, 1, -1, 0, 0.4, 1, 1, 1, 1, 0, 0.4, 1, 1, 1, -1, 0, 0.5, 1, 1, 1, 1, 0, 0.5, 1, 1, 1, -1, 0, 0.6, 1, 1, 1, 1, 0, 0.6, 1, 1, 1, -1, 0, 0.7, 1, 1, 1, 1, 0, 0.7, 1, 1, 1, -1, 0, 0.8, 1, 1, 1, 1, 0, 0.8, 1, 1, 1, -1, 0, 0.9, 1, 1, 1, 1, 0, 0.9, 1, 1, 1, -1, 0, 1.0, 1, 1, 1, 1, 0, 1.0, 1, 1, 1
    )

    # create and activate VAO (vertex array object)
    VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
    glBindVertexArray(VAO)      # activate VAO

    # create and activate VBO (vertex buffer object)
    VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
    glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

    # copy vertex data to VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer

    # configure vertex positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
    glEnableVertexAttribArray(0)

    # configure vertex colors
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
    glEnableVertexAttribArray(1)

    return VAO

def draw_grid(vao, MVP, MVP_loc):
    glBindVertexArray(vao)
    glDrawArrays(GL_LINES, 0, 84)

def draw_obj(vao, MVP, MVP_loc, length):
    glBindVertexArray(vao)    
    glDrawArrays(GL_TRIANGLES, 0, int(length / 3))

def main():
    global g_P, g_cam, g_show_frame, g_mesh

    # initialize glfw
    if not glfwInit():
        return
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)   # OpenGL 3.3
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE) # for macOS

    # create a window and OpenGL context
    window = glfwCreateWindow(800, 800, 'project2: Obj viewer & Hierarchical Model', None, None)
    if not window:
        glfwTerminate()
        return
    glfwMakeContextCurrent(window)

    # register event callbacks
    glfwSetKeyCallback(window, key_callback)
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSetCursorPosCallback(window, cursor_position_callback)
    glfwSetScrollCallback(window, scroll_callback)
    glfwSetDropCallback(window, drop_callback)

    # load shaders
    shader_program = load_shaders(g_vertex_shader_src, g_fragment_shader_src)

    # get uniform locations
    MVP_loc = glGetUniformLocation(shader_program, 'MVP')
    M_loc = glGetUniformLocation(shader_program, 'M')
    view_pos_loc = glGetUniformLocation(shader_program, 'view_pos')

    # prepare vao
    vao_grid = prepare_vao_grid()

    # initialize projection matrix
    g_P = glm.perspective(glm.radians(45.0), 1, 0.5, 20)

    # loop until the user closes the window
    while not glfwWindowShouldClose(window):
        # enable depth test (we'll see details later)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.5, 0.5, 0.5, 0.0)

        # render in "wireframe mode"
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glUseProgram(shader_program)

        M = glm.mat4()
        V = glm.lookAt(g_cam.pos, g_cam.pos + g_cam.front, g_cam.up)
        P = g_P

        MVP = P * V * M

        glUniformMatrix4fv(MVP_loc, 1, GL_FALSE, glm.value_ptr(MVP))
        glUniformMatrix4fv(M_loc, 1, GL_FALSE, glm.value_ptr(M))
        glUniform3f(view_pos_loc, g_cam.pos.x, g_cam.pos.y, g_cam.pos.z)

        # draw grid
        draw_grid(vao_grid, g_P*V*M, MVP_loc)
        
        # draw obj file
        if g_mesh.vao is not None:
            if not g_mesh.is_animating:
                g_mesh.draw_mesh()

        # swap front and back buffers
        glfwSwapBuffers(window)

        # poll events
        glfwPollEvents()

    # terminate glfw
    glfwTerminate()

if __name__ == "__main__":
    main()
