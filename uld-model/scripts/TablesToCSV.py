# -*- coding: utf-8 -*-

# Import arcpy, csv and pandas
import arcpy
import os
import csv
import pandas as pd

# Overwrite outputs
arcpy.env.overwriteOutput = True

# Workspace
arcpy.env.workspace = "C:/MSc-thesis/uld-model/ULDModel.gdb"

# Create an array of the ULD tables in the gdb. The tables of a city have to
# have the same number of rows.
names = ["nrv", "prn", "tln", "trt"] # "prn" and "tln" for polycentric
array = []
for i in names:
    tables = arcpy.ListTables(i+"*"+"_ULD") # "_ULD0" for polycentric
    array.append(tables)

# Output folder for the CSV files
folder = "C:/MSc-thesis/data-analysis/data/inputs/uld-mono" # "/uld-poly" for
# polycentric

# Write the three tables for each city into one CSV file
for i in range(len(array)):
    output = os.path.join(folder, names[i]+"_uld.csv")
    output = folder+'\\'+names[i]+"_uld.csv"
    for j in range(len(array[i])):
        fields = arcpy.ListFields(array[i][j])
        fNames = [field.name for field in fields]
        if j==0:
            with open(output, "wb") as f:
                writer = csv.writer(f, delimiter=",")
                writer.writerow(fNames[1:])
                with arcpy.da.SearchCursor(array[i][j], fNames[1:]) as cursor:
                    for row in cursor:
                        writer.writerow(row)
                f.close()
        else:
            with arcpy.da.SearchCursor(array[i][j], fNames[2]) as cursor:
                uldList = []
                for row in cursor:
                    uldList.append(row[0])
            df = pd.read_csv(output)
            df[fNames[2]] = uldList
            df.to_csv(output, index=False)
