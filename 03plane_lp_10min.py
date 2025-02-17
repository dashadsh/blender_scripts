'''
Plane rotation - LP simulation for 10 minutes
'''
import bpy

# Create a plane (our LP record)
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
myplane = bpy.context.active_object

# Set the total animation length for 10 minutes at 24 FPS
# 10 minutes = 600 seconds
# 600 seconds × 24 frames/second = 14400 frames
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 14400

# Calculate total rotation needed:
# 33.33 RPM (rotations per minute)
# 10 minutes × 33.33 rotations/minute = 333.33 total rotations
# 333.33 rotations × 2π radians/rotation ≈ 2093.45 radians

# Keyframe the start position (no rotation)
start_frame = 1
myplane.keyframe_insert("rotation_euler", frame=start_frame)

# Keyframe the end position
end_frame = 14400
myplane.rotation_euler.z = -2093.45  # Negative for counterclockwise rotation
myplane.keyframe_insert("rotation_euler", frame=end_frame)

# This loop changes how Blender interpolates between keyframes
# Without it, Blender would use Bézier curves which make the rotation speed up and slow down
# With 'LINEAR' interpolation, it maintains constant rotation speed
for fcurve in myplane.animation_data.action.fcurves:
    if fcurve.data_path == 'rotation_euler':  # Find the rotation animation data
        for kf in fcurve.keyframes():         # For each keyframe in that data
            kf.interpolation = 'LINEAR'        # Set it to move at constant speed