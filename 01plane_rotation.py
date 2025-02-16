'''
Plane rotation counter-clockwise
'''
import bpy

# Rotatin

# add object
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
myplane = bpy.context.active_object

# Start frame - no rotation
start_frame = 1
myplane.keyframe_insert("rotation_euler", frame=start_frame)

# End frame - full rotation (2n radians = 360 degrees)
end_frame = 100
myplane.rotation_euler.z = 6.283185 # 2 * pi (approx)
myplane.keyframe_insert("rotation_euler", frame=end_frame)