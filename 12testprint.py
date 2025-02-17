import bpy
import os

# Define the output file path
output_path = "/Users/dg/Documents/CODING/mold_wip/test.txt"

# Write test message to file
with open(output_path, 'w') as f:
    f.write("Test message - hello from Blender!")