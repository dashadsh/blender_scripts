import bpy
import os
import csv
import math

file_path = "/Users/dg/Documents/CODING/mold_wip/MOLD_VINYL.stl"
output_path = "/Users/dg/Documents/CODING/mold_wip/heights_3min.csv"

# Changed duration to 3 minutes
FIRST_FRAME = 1
FPS = 24
DURATION_MINUTES = 3  # Changed from 10 to 3

DURATION_SECONDS = DURATION_MINUTES * 60
LAST_FRAME = FIRST_FRAME + (FPS * DURATION_SECONDS)
TOTAL_FRAMES = LAST_FRAME - FIRST_FRAME + 1

RPM = 33.33
RPS = RPM / 60  # Rotations per second
TOTAL_ROTATIONS = DURATION_SECONDS * RPS
ROTATION_RADIANS = -(TOTAL_ROTATIONS * 2 * math.pi)  # Negative for clockwise

print(f"Animation will have {TOTAL_FRAMES} frames")
print(f"Total rotation: {ROTATION_RADIANS:.2f} radians ({TOTAL_ROTATIONS:.1f} rotations)")

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

def create_dot(location=(8,-1,37)):
    """
    Create a simple measuring dot at specified location.
    """
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2)
    dot = bpy.context.active_object
    dot.name = "MeasureDot"

    mat = bpy.data.materials.new(name="DotMaterial")
    mat.use_nodes = False
    mat.diffuse_color = (0, 1, 0, 1)  # green
    dot.data.materials.append(mat)
    dot.location = location
    
    return dot

def measure_distance(vinyl, dot, frame):
    """
    Measure distance between dot and vinyl surface
    """
    bpy.context.scene.frame_set(frame)
    dot_location = dot.matrix_world @ dot.location
    hit_success, hit_location, hit_normal, hit_face = vinyl.ray_cast(dot_location, (0, 0, -1))
    
    if hit_success:
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

# Collect measurements
distances = []
for frame in range(FIRST_FRAME, LAST_FRAME + 1):
    distance = measure_distance(vinyl, measure_dot, frame)
    distances.append(distance)

# Find max value and normalize
max_distance = max(distances)

with open(output_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for distance in distances:
        normalized = max_distance - distance
        writer.writerow([f"{normalized:.6f}"])