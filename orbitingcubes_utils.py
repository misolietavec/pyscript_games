# %% [markdown]
# 1. One hundred cubes
# 2. Of randomly-selected size
# 3. Each having semi-tranparent fill and stroke
# 4. Each colored according to an underlying algorithm
# 5. Each rotating around its own center with a randomly-selected speed and
#    direction
# 6. Randomly distributed around the circumference of
# 7. One of several concentric circles
# 8. All cubes rotating at a randomly-selected speed and direction around
#    a common center point
#
# Updated implemention, using pyscript and three.js by Ben Alkov May 2022
# Implementation by Ben Alkov December 2016

# %%
import math
import random
import js

# -------------------------------------utils.py ------------------------------
def avoid_zero(range_, tolerance):
    # Return a random value in the range from `-range` to strictly less than
    # `range`, excluding the inner range +/-`tolerance` (and, logically, zero as
    # well).
    attempt = rand_float(-range_, range_)
    while -tolerance < attempt and attempt < tolerance:
        attempt = rand_float(-range_, range_)
    return attempt


# Linear mapping from range [from_start, from_end] to range [to_start, to_end]
def map_linear(to_map, from_start, from_end, to_start, to_end):
    """Implementation as found in three.js
        Pending merge of https://github.com/pyodide/pyodide/pull/2520
    """
    return to_start + (to_map - from_start) * (to_end - to_start) / (from_end - from_start)


def platform_request_animation_frame():
    return (js.window.requestAnimationFrame or
            js.window.mozRequestAnimationFrame or
            js.window.webkitRequestAnimationFrame)


# Random float from [low, high] interval
def rand_float(start, end):
    """Implementation as found in three.js
        Pending merge of https://github.com/pyodide/pyodide/pull/2520
    """
    return start + random.random() * (end - start)


def renderer_config(renderer, width, height, clear_color=0x000000):
    renderer = renderer.new(
        powerPreference='high-performance',
        antialias=True,
        stencil=False,
        depth=True
    )
    renderer.setPixelRatio(js.window.devicePixelRatio)
    renderer.setSize(width, height)
    renderer.setClearColor(clear_color, 1.0)
    return renderer

# ---------------------------------------- /utils.py -----------------------------
# %%
# Not strictly necessary, but seeing naked e.g. `document`, `window`, etc. really bothers me
from pyodide.ffi import create_proxy
from three import (
    AmbientLight,
    BoxBufferGeometry,
    Color,
    DirectionalLight,
    DoubleSide,
    EdgesGeometry,
    Euler,
    LineBasicMaterial,
    LineSegments,
    Mesh,
    MeshLambertMaterial,
    Object3D,
    PerspectiveCamera,
    Scene,
    Vector3,
    WebGLRenderer,
)

# %%
_AMB_LIGHT = None
_CAMERA = None
_CLICKED = 0
_HEIGHT = js.window.innerHeight
_LIGHT = None
_RENDERER = None
_SCENE = None
_WIDTH = js.window.innerWidth

# %%
_CUBES = None


# %%
class Cube():
    # three.js length units are in meters
    CUBE_MIN_SIZE = 1.25
    CUBE_MAX_SIZE = 2.0

    # ORBIT_SPEED and SELF_ROT are degrees/frame
    # [-0.13, 0.13] within 0.01 degree of 0
    ORBIT_SPEED_LIMIT = 0.13
    ORBIT_SPEED_TOLERANCE = 0.01

    # [-1.3, 1.3] within 0.5 degree of 0
    SELF_ROT_SPEED_LIMIT = 1.3
    SELF_ROT_TOLERANCE = 0.5

    # Pythagoras in 3D
    CUBE_MAX_EXTENT = math.sqrt(3) * CUBE_MAX_SIZE

    # First orbit is a little larger than the diagonal extent of the largest cube
    FIRST_ORBIT = CUBE_MAX_EXTENT + (CUBE_MAX_SIZE * 0.5)
    ORBITS = (FIRST_ORBIT, FIRST_ORBIT * 2,
              FIRST_ORBIT * 3, FIRST_ORBIT * 4)

    def __init__(self):
        self._size = rand_float(self.CUBE_MIN_SIZE, self.CUBE_MAX_SIZE)
        self._position, self._radius = Cube._position_on_orbit()
        self._angle = self._update_angle()
        self._rotation = Euler.new(0.0, 0.0, rand_float(0.0, math.tau))
        self._orbit_angular_speed = avoid_zero(self.ORBIT_SPEED_LIMIT,
                                                     self.ORBIT_SPEED_TOLERANCE)
        self._object_angular_speed = avoid_zero(self.SELF_ROT_SPEED_LIMIT,
                                                      self.SELF_ROT_TOLERANCE)
        self._cube_geometry = BoxBufferGeometry.new(self._size, self._size, self._size)
        self._outline_geometry = EdgesGeometry.new(self._cube_geometry)
        alpha = map_linear(self._radius, self.ORBITS[1] - 2, self.ORBITS[3], 1.0, 0.5)
        self._cube_material = MeshLambertMaterial.new(
            transparent=True,
            side=DoubleSide,
            opacity=alpha)
        self._outline_material = LineBasicMaterial.new(
            transparent=True,
            side=DoubleSide,
            opacity=alpha)
        self._outline_mesh = LineSegments.new(self._outline_geometry,
                                              self._outline_material)
        self._cube_mesh = Mesh.new(self._cube_geometry, self._cube_material)
        self._cube_mesh.position.copy(self._position)
        self._cube_mesh.rotation.copy(self._rotation)
        self._cube_mesh.add(self._outline_mesh)
        self.recolor()

    def _update_angle(self):
        return math.atan2(self._position.y, self._position.x)

    def get_mesh_object(self):
        return self._cube_mesh

    def orbit(self):
        x_pos = self._position.x
        y_pos = self._position.y
        theta = math.radians(self._orbit_angular_speed)
        self._position.x = x_pos * math.cos(theta) + y_pos * math.sin(theta)
        self._position.y = y_pos * math.cos(theta) - x_pos * math.sin(theta)
        self._cube_mesh.position.copy(self._position)
        self._angle = self._update_angle()

    def rotate(self):
        self._rotation.x += math.radians(self._object_angular_speed)
        self._rotation.y += math.radians(self._object_angular_speed)
        self._rotation.z += math.radians(self._object_angular_speed)
        self._cube_mesh.rotation.x = self._rotation.x
        self._cube_mesh.rotation.y = self._rotation.y
        self._cube_mesh.rotation.z = self._rotation.z

    def recolor(self):
        blue = Color.new(0x1515eb)
        dk_blue = Color.new(0x0a0a73)
        green = Color.new(0x95c251)
        dk_green = Color.new(0x394a1f)
        angle = abs(self._angle)
        half_pi = math.pi / 2
        # Left half
        if angle >= half_pi:
            shade = map_linear(angle, math.pi, half_pi, 0, 0.5)
            color = green.clone()
            other_color = blue.clone()
            outline_color = dk_green.clone()
            other_outline_color = dk_blue.clone()
        # Right half.
        else:
            shade = map_linear(angle, 0, half_pi, 0, 0.5)
            color = blue.clone()
            other_color = green.clone()
            outline_color = dk_blue.clone()
            other_outline_color = dk_green.clone()

        self._cube_material.color = color.clone()
        self._cube_material.color.lerp(
            other_color.clone(),
            # avoid obvious color bands
            shade + rand_float(-0.02, 0.02))
        self._outline_material.color = outline_color.clone()
        self._outline_material.color.lerp(
            other_outline_color.clone(),
            # avoid obvious color bands
            shade + rand_float(-0.02, 0.02))

    def _choose_orbit():
        # Randomly choose an orbit, based on a set of probabilities.
        # The probabilities favor larger orbits, as they have room for more cubes.
        chance = rand_float(0.0, 1.0)
        if chance < 0.16:
            return Cube.ORBITS[0]
        if chance < 0.40:
            return Cube.ORBITS[1]
        if chance < 0.72:
            return Cube.ORBITS[2]
        if chance < 1.0:
            return Cube.ORBITS[3]

        return 0

    def _position_on_orbit():
        # Generate a random position on the circumference of the orbit chosen for
        # this item.
        angle = rand_float(0.0, math.tau)
        orbit = Cube._choose_orbit()

        # Randomly offset the position on the orbit, so we don't end up with multiple
        # cubes orbiting on *exactly* the same circles.
        radius = orbit + rand_float(0.0, Cube.ORBITS[0])
        creation_x = math.cos(angle) * radius
        creation_y = math.sin(angle) * radius
        position = Vector3.new(creation_x, creation_y, 0)
        return [position, radius]


# %%
def _handle_resize(event):
    _CAMERA.aspect = js.window.innerWidth / js.window.innerHeight
    _CAMERA.updateProjectionMatrix()
    _RENDERER.setSize(js.window.innerWidth, js.window.innerHeight)
    _RENDERER.setPixelRatio(js.window.devicePixelRatio)


# %%
def _handle_click(event):
    global _CLICKED
    if _CLICKED == 0:
        _CAMERA.near = 31.9
        _CAMERA.far = 32.1
        _CAMERA.updateProjectionMatrix()
    if _CLICKED == 1:
        _CAMERA.position.y = -20
        _CAMERA.position.z = 20
        _CAMERA.near = 15
        _CAMERA.far = 150
        _CAMERA.lookAt(Vector3.new(0, 0, 0))
        _CAMERA.updateProjectionMatrix()
    if _CLICKED == 2:
        _CAMERA.position.y = -1
        _CAMERA.position.z = 32
        _CAMERA.lookAt(Vector3.new(0, 0, 0))
        _CAMERA.updateProjectionMatrix()
    _CLICKED = _CLICKED + 1 if _CLICKED < 2 else 0


# %%
def _init():
    global _SCENE
    global _AMB_LIGHT
    global _LIGHT
    global _CAMERA
    global _RENDERER

    _SCENE = Scene.new()

    # I can't find another way to do this...
    Object3D.DefaultUp = Vector3.new(0, 0, 1)
    _LIGHT = DirectionalLight.new()
    Object3D.DefaultUp = Vector3.new(0, 1, 0)
    _AMB_LIGHT = AmbientLight.new()
    _CAMERA = PerspectiveCamera.new(
        50,  # F.O.V.
        _WIDTH / _HEIGHT,  # Aspect
        30,  # Near clip
        34  # Far clip
    )
    _RENDERER = renderer_config(WebGLRenderer, _WIDTH, _HEIGHT,
                                      Color.new(0x46474c))  # Middle grey


# %%
def _setup():
    global _CUBES

    num_cubes = 100

    _CAMERA.setFocalLength = 70
    _CAMERA.position.z = 32
    _CAMERA.lookAt(Vector3.new(0, 0, 0))
    _CAMERA.updateProjectionMatrix()
    _AMB_LIGHT.color = Color.new(0xb3a297)  # amber
    _AMB_LIGHT.intensity = 0.6
    _SCENE.add(_LIGHT)
    _SCENE.add(_AMB_LIGHT)
    _CUBES = [Cube() for _ in range(num_cubes)]
    for cube in _CUBES:
        _SCENE.add(cube.get_mesh_object())
    js.window.addEventListener('click', create_proxy(_handle_click))
    js.window.addEventListener('resize', create_proxy(_handle_resize))
    js.document.body.appendChild(_RENDERER.domElement)
    _RENDERER.setAnimationLoop(create_proxy(_animate))
    _RENDERER.render(_SCENE, _CAMERA)


# %%
def _animate(*args):
    for cube in _CUBES:
        cube.rotate()
        cube.orbit()
        cube.recolor()
    _RENDERER.render(_SCENE, _CAMERA)


# %%
pyscript_loader.close()

# %%
_init()
_setup()
_animate()
