import bpy
import os

def import_stl(file_path, scale=1.0, location=(0,0,0), rotation=(0,0,0)):
    """
    Import an STL file into Blender.
    """
    # Import STL file
    bpy.ops.wm.stl_import(filepath=file_path)
    
    # Get imported object
    obj = bpy.context.active_object
    
    # Apply parameters
    obj.scale = (scale, scale, scale)
    obj.location = location    
    obj.rotation_euler = rotation
    
    # Apply transformations - otherwise didn't work
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    return obj

file_path = "/Users/dg/Documents/CODING/mold_wip/MOLD_VINYL.stl"
vinyl = import_stl(file_path, scale=1.0, location=(4,-1,35), rotation=(1.5708,0,0))

#create the needle

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120

# Calculate rotation for 5 seconds at 33.33 RPM
# 33.33 RPM = 0.5555 RPS (rotations per second)
# 5 seconds * 0.5555 RPS = 2.7775 rotations
# 2.7775 rotations * 2π = ~17.45 radians

# Animate the vinyl's movement
vinyl.rotation_euler.z = 0
vinyl.keyframe_insert(data_path="rotation_euler", frame=1)
vinyl.rotation_euler.z = -17.45
vinyl.keyframe_insert(data_path="rotation_euler", frame=120)

# Make interpolation linear
for obj in [vinyl]:
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'

