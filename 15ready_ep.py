import bpy
import os
import csv
import math

file_path = "/Users/dg/Documents/CODING/mold_wip/MOLD_VINYL.stl"
output_path = "/Users/dg/Documents/CODING/mold_wip/heights_10min.csv"

FIRST_FRAME = 1
FPS = 24
DURATION_MINUTES = 10

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

bpy.context.scene.frame_start = FIRST_FRAME
bpy.context.scene.frame_end = LAST_FRAME

vinyl.rotation_euler.z = 0
vinyl.keyframe_insert(data_path="rotation_euler", frame=FIRST_FRAME)
vinyl.rotation_euler.z = ROTATION_RADIANS
vinyl.keyframe_insert(data_path="rotation_euler", frame=LAST_FRAME)

# Animate the dot
measure_dot.keyframe_insert(data_path="location", frame=FIRST_FRAME)
measure_dot.location = (0, 52, 5)
measure_dot.keyframe_insert(data_path="location", frame=LAST_FRAME)

# Make interpolation linear
for obj in [vinyl, measure_dot]:
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'

# First pass: collect all measurements and find min/max
distances = []
for frame in range(FIRST_FRAME, LAST_FRAME + 1):
    distance = measure_distance(vinyl, measure_dot, frame)
    #if distance is not None:
    distances.append(distance)

# Find min and max values
#Original:    5.0, 7.0, 6.0  (where 7.0 is deepest)
#Normalized:  2.0, 0.0, 1.0  (7.0 - original = new value)
max_distance = max(distances)

with open(output_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    #writer.writerow(['height'])  # header
    
    for distance in distances:
        # Invert and normalize: deepest (max distance) becomes 0, highest (min distance) becomes max-min
        normalized = max_distance - distance
        writer.writerow([f"{normalized:.6f}"])