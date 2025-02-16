'''
Plane moving up and down
'''
# add object
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

# save currently active object
myplane = bpy.context.active_object
# see:      
# >>> bpy.context.active_object
# bpy.data.objects['Plane']

# test:
# myplane2 = bpy.context.active_object
# myplane.name = 'somename'
# myplane2.name

# try:
# myplane.keyframe_insert("location", frame=60)
start_frame = 1
myplane.keyframe_insert("location", frame=start_frame)

# move up to z=5 at middle frame
myplane.location.z = 5
mid_frame = 50
myplane.keyframe_insert("location", frame=mid_frame)

# move back to z=0
myplane.location.z = 0
end_frame = 100
myplane.keyframe_insert("location", frame=end_frame)