import bpy
import os
import csv
import math

file_path = "/Users/dg/Documents/CODING/mold_wip/MOLD_VINYL.stl"
output_path = "/Users/dg/Documents/CODING/mold_wip/data.csv"

FIRST_FRAME = 1
FPS = 24
DURATION_MINUTES = 3

DURATION_SECONDS = DURATION_MINUTES * 60
LAST_FRAME = FIRST_FRAME + (FPS * DURATION_SECONDS)
TOTAL_FRAMES = LAST_FRAME - FIRST_FRAME + 1

RPM = 33.33
RPS = RPM / 60  # Rotations per second
TOTAL_ROTATIONS = DURATION_SECONDS * RPS
ROTATION_RADIANS = -(TOTAL_ROTATIONS * 2 * math.pi)  # Negative for clockwise

def import_stl(file_path, scale=1.0, location=(0,0,0), rotation=(0,0,0)):
    """
    Import an STL file into Blender.
    """
    bpy.ops.wm.stl_import(filepath=file_path)
    obj = bpy.context.active_object
    obj.scale = (scale, scale, scale)
    obj.location = location    
    obj.rotation_euler = rotation
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    return obj

def create_dot(name, location, radius, segments):
    """
    Create a simple measuring dot at specified location.
    """
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=segments, radius=radius, location=location)
    dot = bpy.context.active_object
    dot.name = name

    mat = bpy.data.materials.new(name=f"{name}_material")
    mat.use_nodes = False # ?
    mat.diffuse_color = (1, 0, 0, 1)  # Red color with full opacity
    
    # Assign material
    if dot.data.materials:
        dot.data.materials[0] = mat
    else:
        dot.data.materials.append(mat)
    
    return dot

# dot start porition 0, 148
# dot end posiition 0, 52

vinyl = import_stl(file_path, scale=1.0, location=(4,-1,35), rotation=(1.5708,0,0))

bpy.context.scene.frame_start = FIRST_FRAME
bpy.context.scene.frame_end = LAST_FRAME

vinyl.rotation_euler.z = 0
vinyl.keyframe_insert(data_path="rotation_euler", frame=FIRST_FRAME)
vinyl.rotation_euler.z = ROTATION_RADIANS
vinyl.keyframe_insert(data_path="rotation_euler", frame=LAST_FRAME)

tracking_dot = create_dot(name="tracking_dot", location=(0, 148, 0), radius=0.7, segments=12)

# Add a shrinkwrap constraint to the tracking dot to make it follow the vinyl surface
shrinkwrap = tracking_dot.constraints.new('SHRINKWRAP')
shrinkwrap.target = vinyl
shrinkwrap.shrinkwrap_type = 'NEAREST_SURFACE'
shrinkwrap.distance = 0.1  # Small offset from surface

tracking_dot.keyframe_insert(data_path="location", frame=FIRST_FRAME)
tracking_dot.location = (0, 52, 0)
tracking_dot.keyframe_insert(data_path="location", frame=LAST_FRAME)

# Make interpolation linear
for obj in [vinyl, tracking_dot]:
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'
            
# Make the movement more natural with Bezier curves
#if tracking_dot.animation_data and tracking_dot.animation_data.action:
#    for fcurve in tracking_dot.animation_data.action.fcurves:
#        for kfp in fcurve.keyframe_points:
#            kfp.interpolation = 'BEZIER'
#            kfp.handle_left_type = 'AUTO'
#            kfp.handle_right_type = 'AUTO'