import random

import js


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
