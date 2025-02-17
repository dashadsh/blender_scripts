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
 
    # -----------OPTIONAL----------
    # Smooth the object
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    
    # Recalculate normals
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    #Smooth shades
    bpy.ops.object.shade_smooth()
    bpy.ops.object.normal_calculate_to_face()
    # -----------OPTIONAL----------
    
    return obj

file_path = "/Users/dg/Documents/CODING/mold_wip/MOLD_VINYL.stl"
obj = import_stl(file_path, scale=1.0, location=(4,-1,35), rotation=(1.5708,0,0))

#bpy.context.object.location[0] = 4 # x
#bpy.context.object.location[1] = -1 # y
#bpy.context.object.location[2] = 35 # Z

#bpy.context.object.rotation_euler[0] = 1.5708 # X 90 grad

mold = bpy.context.active_object
# mold.name = "MOLD"

# Set animation frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120

# Store initial X rotation (90 degrees)
initial_x_rotation = mold.rotation_euler[0]  # Keep the 1.5708 X rotation

# Start frame - initial position
start_frame = 1
mold.rotation_euler = (initial_x_rotation, 0, 0)  # Keep X rotation, zero Z
mold.keyframe_insert(data_path="rotation_euler", frame=start_frame)

end_frame = 120
#mold.rotation_euler.z = -17.45  # Rotation for 5 seconds at 33⅓ RPM
mold.rotation_euler = (initial_x_rotation, 0, -17.45)  # Keep X rotation, add Z rotation
mold.keyframe_insert(data_path="rotation_euler", frame=end_frame)

# Make movements linear
for obj in [mold]:
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframes():
            kf.interpolation = 'LINEAR'