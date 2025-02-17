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
    obj.rotation_euler = rotation
    obj.location = location
    
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
mold = import_stl(file_path, scale=1.0, location=(0,0,0), rotation=(0,0,0))