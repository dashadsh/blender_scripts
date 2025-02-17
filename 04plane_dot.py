import bpy

# Clear existing objects (optional)
#bpy.ops.object.select_all(action='SELECT')
#bpy.ops.object.delete()

# Create LP (plane that only rotates)
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
lp = bpy.context.active_object
lp.name = "LP"

# Create needle (another plane, we'll make it smaller)
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(1, 0, 0.1))
needle = bpy.context.active_object
needle.name = "Needle"
needle.scale = (0.02, 0.02, 0.02)

# 5 seconds test animation
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120

# LP Animation - only rotation
start_frame = 1
lp.keyframe_insert("rotation_euler", frame=start_frame)

end_frame = 120
lp.rotation_euler.z = -17.45  # Rotation for 5 seconds at 33⅓ RPM
lp.keyframe_insert("rotation_euler", frame=end_frame)

# Needle Animation - only movement
needle.keyframe_insert("location", frame=start_frame)  # Start at outer edge
needle.location.x = 0  # Move to center
needle.keyframe_insert("location", frame=end_frame)

# Make movements linear
for obj in [lp, needle]:
    for fcurve in obj.animation_data.action.fcurves:
        for kf in fcurve.keyframes():
            kf.interpolation = 'LINEAR'