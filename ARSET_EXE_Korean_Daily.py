import struct
import os, sys, time
import numpy as np, numpy.ma as ma
from osgeo import gdal, ogr, gdalnumeric
import matplotlib.pyplot as plt
import datetime
import statistics as stat
import pandas as pd

#Input VNP46A2 - KR
####Change it to your input Data Folder###
#os.chdir('D:/KEOL/Suomi/Data_BlackMarble_Korea/ALL2019-2021/')
os.chdir('D:/KEOL/Suomi/Training/Data_Korea/')

#Output - KR
####Chage This Path to Output/Temp Folder####
outputFolder = "D:/KEOL/Suomi/Training/Output/"

#Itaewon, KR - Pixel location
lat = 37.535238
lon = 126.993496

def plotTimeSeries(JD, DNBvalue3, DNBvalue1):
    plt.plot_date(JD, DNBvalue3,label = "DNB_3x3", linestyle ='solid')
    plt.plot_date(JD, DNBvalue1,label = "DNB_1x1", linestyle ='solid')
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.gcf().autofmt_xdate
    plt.tight_layout()
    # naming the x axis 
    plt.xlabel('Date', fontsize=26) 
    # naming the y axis 
    plt.ylabel('NTL Radiance', fontsize=26)
    # giving a title to my graph 
    plt.title('NTL Time-Series - Gyeonggi', fontsize=30) 
    # show a legend on the plot 
    plt.legend(fontsize=24) 
    # function to show the plot 
    plt.show() 
    
def conJDtoDate(JD):
    date = datetime.datetime.strptime(JD, '%y%j').date()
    return date

def getRasterData(inputRaster, lat, lon, window):
    raster = gdal.Open(inputRaster,gdal.GA_ReadOnly)
    if raster is None:
        print ("Could not open image " , content[NOF])
        #sys.exit(1)

    band = raster.GetRasterBand(1)

    cols = raster.RasterXSize
    rows = raster.RasterYSize

    transform = raster.GetGeoTransform()
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = -transform[5]
    data = band.ReadAsArray(0, 0, cols, rows)

    col = int((lon - xOrigin) / pixelWidth )
    row = int((yOrigin - lat) / pixelHeight)
#Data AT THAT ROW COLUMN
    if(window == 3):
        #print(window)
        indexX = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
        indexY = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
        newIndexX = indexX + row
        newIndexY = indexY + col
        
        Toalvalue = []
        for i in range(0, 3):
            for j in range(0, 3):
                Toalvalue.append(data[newIndexX[i][j]][newIndexY[i][j]])
                
        value = format(stat.mean(map(float, Toalvalue)),'.2f')
        return float(value)

    else:
        #print(window)
        value = data[row][col]
        return value
        
def processHD5(inputHD5, layer, OutputFolder, lat, lon, window):
    #Get File Name Prefix
    rasterFilePre = inputHD5[:-3]
    ## Open HDF file
    hdflayer = gdal.Open(inputHD5, gdal.GA_ReadOnly)
    subhdflayer = hdflayer.GetSubDatasets()[layer][0]
    rlayer = gdal.Open(subhdflayer, gdal.GA_ReadOnly)
    #Subset the Layer Name
    outputLayerName = subhdflayer[92:]
    #print(outputLayerName)
    
    #outputFile
    outputRaster = OutputFolder + rasterFilePre + "_" + outputLayerName + ".tif"
    
    HorizontalTileNumber = int(rlayer.GetMetadata_Dict()["HorizontalTileNumber"])
    VerticalTileNumber = int(rlayer.GetMetadata_Dict()["VerticalTileNumber"])
    WestBoundCoord = (10*HorizontalTileNumber) - 180
    NorthBoundCoord = 90-(10*VerticalTileNumber)
    
    EastBoundCoord = WestBoundCoord + 10
    SouthBoundCoord = NorthBoundCoord - 10
    
    EPSG = "-a_srs EPSG:4326" #WGS84
    
    translateOptionText = EPSG+" -a_ullr " + str(WestBoundCoord) + " " + str(NorthBoundCoord) + " " + str(EastBoundCoord) + " " + str(SouthBoundCoord)
    translateoptions = gdal.TranslateOptions(gdal.ParseCommandLine(translateOptionText))
    gdal.Translate(outputRaster,rlayer, options=translateoptions)
    value = getRasterData(outputRaster,lat, lon, window)
    os.remove(outputRaster)
    
    return value


rasterFiles = os.listdir(os.getcwd())
rasterFiles.sort()
#print(rasterFiles)

totalFiles = len(rasterFiles)
DNBvalue1 = []
DNBvalue3 = []
JD = []

for NOF in range(0, totalFiles):
    year = rasterFiles[NOF][11:][:2]
    JulianDay = rasterFiles[NOF][13:][:3]
    JulianDay = year + JulianDay

    #Convert Julian day to Date
    dateOfYear = conJDtoDate(JulianDay)
    JD.append(dateOfYear)
    print (JD[NOF])

    DNBvalue3.append((processHD5(rasterFiles[NOF],2,outputFolder, lat, lon, 3)))
    DNBvalue1.append((processHD5(rasterFiles[NOF],2,outputFolder, lat, lon, 1)))
    
plotTimeSeries(JD, DNBvalue3, DNBvalue1)

#Save to excel
#a=np.array(DNBvalue1)
#b=np.array(DNBvalue3)
#np.savetxt('D:/KEOL/Suomi/GeoTIFF_BlackMarble_Korea/Daejeon.csv',DNBvalue3)
#np.savetxt('D:/KEOL/Suomi/GeoTIFF_BlackMarble_Korea/Incheon8.csv',DNBvalue3)
#np.savetxt('D:/KEOL/Suomi/GeoTIFF_BlackMarble_Korea/Itaewon8.5.csv',DNBvalue5)
#np.savetxt('D:/KEOL/Suomi/GeoTIFF_BlackMarble_Korea/Gwangju.csv',DNBvalue3)