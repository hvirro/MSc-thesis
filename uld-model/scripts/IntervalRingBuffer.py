# -*- coding: utf-8 -*-

# Import system modules
import arcpy

# Overwrite outputs
arcpy.env.overwriteOutput = True

# Get user-defined environment settings
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# Get user-defined variables
inputFC = arcpy.GetParameterAsText(1)
outputFC = arcpy.GetParameterAsText(2)
maxDist = int(arcpy.GetParameterAsText(3))
interval = int(arcpy.GetParameterAsText(4))
clipFC = arcpy.GetParameterAsText(5)

# Create a list of buffer intervals
distances = []
dist = interval
while dist <= maxDist:
    if len(distances) <= maxDist / interval:
        distances.append(dist)
        dist += interval
    else:
        break

# Create ring buffers at defined distances and clip them if a polygon is
# specified
if clipFC:
    buffers = arcpy.MultipleRingBuffer_analysis(inputFC, \
        arcpy.CreateUniqueName("in_memory/buffers"), distances, "Meters", \
        "", "ALL")
    arcpy.Clip_analysis(buffers, clipFC, outputFC)
else:
    arcpy.MultipleRingBuffer_analysis(inputFC, outputFC, distances, \
        "Meters", "", "ALL")

# Clear the in-memory workspace
arcpy.Delete_management("in_memory")
