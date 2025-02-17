import bpy
import os
import csv

file_path = "/Users/dg/Documents/CODING/mold_wip/MOLD_VINYL.stl"
# output_path = "/Users/dg/Documents/CODING/mold_wip/measurements.txt"
output_path = "/Users/dg/Documents/CODING/mold_wip/heights.csv"

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

def create_dot(location=(8,-1,37)):
    """
    Create a simple measuring dot at specified location.
    """
    # Create the dot
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2)
    dot = bpy.context.active_object
    dot.name = "MeasureDot"

    # Create material
    mat = bpy.data.materials.new(name="DotMaterial")
    mat.use_nodes = False
    mat.diffuse_color = (0, 1, 0, 1)  # green (R=0, G=1, B=0, A=1)
    # Assign material
    dot.data.materials.append(mat)

    # Position dot
    dot.location = location
    
    return dot

def measure_distance(vinyl, dot, frame):
    """
    Measure distance between dot and vinyl surface
    """
    # Move animation to the frame we want to measure
    bpy.context.scene.frame_set(frame)
    # Get dot's position in global space (matrix_world converts from local to global coordinates)
    dot_location = dot.matrix_world @ dot.location
    # Cast ray downward (0, 0, -1 is straight down)
    # ray_cast returns tuple: (hit_success, hit_location, hit_normal, hit_face_index)
    hit_success, hit_location, hit_normal, hit_face = vinyl.ray_cast(dot_location, (0, 0, -1))
    
    if hit_success: # can be result[0]
        distance = (dot_location - hit_location).length
        return distance
    return None

    
vinyl = import_stl(file_path, scale=1.0, location=(4,-1,35), rotation=(1.5708,0,0))
measure_dot = create_dot(location=(0,148,5))

# Animation setup
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120

# Animate the vinyl
vinyl.rotation_euler.z = 0
vinyl.keyframe_insert(data_path="rotation_euler", frame=1)
vinyl.rotation_euler.z = -17.45
vinyl.keyframe_insert(data_path="rotation_euler", frame=120)

# Animate the dot
measure_dot.keyframe_insert(data_path="location", frame=1)
measure_dot.location = (0, 0, 5)  # End at center
measure_dot.keyframe_insert(data_path="location", frame=120)

# Make interpolation linear
for obj in [vinyl, measure_dot]:
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'

# Measure and save to file
with open(output_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write header
    # writer.writerow(['height'])
    
    # Measure every frame
    for frame in range(1, 121):
        distance = measure_distance(vinyl, measure_dot, frame)
        if distance is not None:
            writer.writerow([f"{distance:.6f}"])