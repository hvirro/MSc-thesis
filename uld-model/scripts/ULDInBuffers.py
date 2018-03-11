# -*- coding: utf-8 -*-

# Import system modules
import arcpy
from arcpy.sa import *
import os

# Overwrite outputs
arcpy.env.overwriteOutput = True

# Get user-defined environment settings
arcpy.env.workspace = arcpy.GetParameterAsText(0)

# Get user-defined variables
buffers = arcpy.GetParameterAsText(1)
urbanRaster = arcpy.GetParameterAsText(2)
uldTable = os.path.basename(arcpy.GetParameterAsText(3))

# Use the cell size of urbanRaster for the calculation
arcpy.env.cellSize = urbanRaster

# Execute TabulateArea to calculate the areas of the land use classes in the
# buffers
areaTable = TabulateArea(
    buffers, "OBJECTID", urbanRaster, "CLASS_NAME", "in_memory/areaTable")

# Make a copy of the buffers
buffCopy = arcpy.CopyFeatures_management(buffers, "in_memory/buffCopy")

# Add a field for area calculation to buffCopy and calculate the area of the
# buffers
arcpy.AddField_management(buffCopy, "area", "DOUBLE")
arcpy.CalculateField_management(
    buffCopy, "area", "!SHAPE.AREA@SQUAREMETERS!", "PYTHON")

# Add field 'r_km' to buffCopy and calculate buffer distances in km
arcpy.AddField_management(buffCopy, "r_km", "DOUBLE")
with arcpy.da.UpdateCursor(buffCopy, ["distance", "r_km"]) as cursor:
    for row in cursor:
        row[1] = row[0]/1000
        cursor.updateRow(row)

# Join the fields 'area' and 'r_km' to areaTable
arcpy.JoinField_management(
    areaTable, "OBJECTID", buffCopy, "OBJECTID", ["area", "r_km"])

# Add a field for urban land density calculation to areaTable
name = os.path.basename(urbanRaster)
uldField = "uld_" + os.path.splitext(name)[0][4:]
arcpy.AddField_management(areaTable, uldField, "DOUBLE")

# List the fields in areaTable
fieldNames = [field.name for field in arcpy.ListFields(areaTable)]

# List the classes that will be used during the density calculation
fields = [uldField, "URBAN", "area"]

# List the fields that will be subtracted from the field 'area' during the
# density calculation
subtract = ["NO DATA", "WATER", "WETLAND"]

# Append the fields that will be subtracted from the field 'area' if they are
# present in fieldNames
for f in subtract:
    if f in fieldNames:
        fields.append(f)

# Calculate urban land density in the buffers
with arcpy.da.UpdateCursor(areaTable, fields) as cursor:
    for row in cursor:
        if len(fields) == 6:
            row[0] = row[1]/(row[2]-(row[3]+row[4]+row[5]))
        elif len(fields) == 5:
            row[0] = row[1]/(row[2]-(row[3]+row[4]))
        elif len(fields) == 4:
            row[0] = row[1]/(row[2]-row[3])
        else:
            row[0] = row[1]/row[2]
        cursor.updateRow(row)

# Create FieldMap objects (fm1, fm2) of the fields 'r_km' and 'density' and
# add them to the FieldMappings object (fms)
fm1 = arcpy.FieldMap()
fm2 = arcpy.FieldMap()
fms = arcpy.FieldMappings()
fm1.addInputField(areaTable, "r_km")
fm2.addInputField(areaTable, uldField)
fms.addFieldMap(fm1)
fms.addFieldMap(fm2)

# Create the output table by extracting the mapped fields from areaTable
arcpy.TableToTable_conversion(
    areaTable, arcpy.env.workspace, uldTable, "", fms)

# Clear the in-memory workspace
arcpy.Delete_management("in_memory")
