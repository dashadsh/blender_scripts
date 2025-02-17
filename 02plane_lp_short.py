'''
Plane rotation - LP simulation short
'''
import bpy

# add object
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
myplane = bpy.context.active_object

# Set scene frame range - let's test with 5 seconds (120 frames)
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120

# Calculate rotation for 5 seconds at 33.33 RPM
# 33.33 RPM = 0.5555 RPS (rotations per second)
# 5 seconds * 0.5555 RPS = 2.7775 rotations
# 2.7775 rotations * 2π = ~17.45 radians

# Start frame - no rotation
start_frame = 1
myplane.keyframe_insert("rotation_euler", frame=start_frame)

# End frame with realistic 33.33 RPM rotation
end_frame = 120
myplane.rotation_euler.z = -17.45  # for counterclockwise
myplane.keyframe_insert("rotation_euler", frame=end_frame)

# Make the interpolation linear
for fcurve in myplane.animation_data.action.fcurves:
    if fcurve.data_path == 'rotation_euler':
        for kf in fcurve.keyframes():
            kf.interpolation = 'LINEAR'