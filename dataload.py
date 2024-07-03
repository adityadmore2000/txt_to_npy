import pandas as pd 
import numpy as np
import os
import glob
from tqdm import tqdm
import logging
import open3d as o3d 

logger = logging.getLogger(__name__)

class ReadFileException(Exception):
    def __str__(self):
        return("Can't read the file. Something wrong with data format.")
    pass

class SeparatorException(ReadFileException):
    def __str__(self):
        return("Separator of the file should be comma or tab.")

class DataFormatException(ReadFileException):
    def __str__(self):
        return("The size of data column is not match.")

def read_txt_to_pcd(csv_file):
    pcd_df = pd.read_csv(csv_file,header=None)
    pcd = df_to_pcd(pcd_df)
    return pcd

def df_to_pcd(df):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(df.values[:,:3])
    pcd.colors = o3d.utility.Vector3dVector(df.values[:,3:6]/255)
    return pcd
    

def arr_to_pcd(arr):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(arr[:,:3])
    pcd.colors = o3d.utility.Vector3dVector(arr[:,3:6]/255)
    return pcd

def read_pcd_to_df(pcd_file):
    pcd_o3d = o3d.io.read_point_cloud(pcd_file)
    pcd_df = pcd_to_df(pcd_o3d)
    return pcd_df
    
def pcd_to_df(pcd_o3d):
    pts = pd.DataFrame(np.array(pcd_o3d.points),index=None)
    cls = pd.DataFrame(np.array(pcd_o3d.colors)*255,index=None).astype(int)
    pcd_df = pd.concat((pts,cls),axis=1)    
    return pcd_df

def read_data(file_name:str, separator:str = ","):
    try:
        if separator == ",":
            pcs = pd.read_csv(file_name, index_col=None,header=None, encoding="utf_8")
        elif separator =='t':
            pcs = pd.read_table(file_name, index_col=None,header=None, encoding="utf_8",delimiter='\s+')
        else:
            raise SeparatorException    
        if pcs.dtypes[0] =="O":
            raise ReadFileException
    except ReadFileException as re:
        logger.debug(re)
        return re
    return pcs

def read_csv_to_ndarray(file_name:str, separator:str = ",")-> np.ndarray:
    return read_data(file_name, separator).values
    
        
        
def from_CCannotation_to_xyzrgbl(file_name:str, output_dir:str, separator = ",",intensity=False, drop_color=False)->bool:
    """_summary_
    annotated data to .npy file
    Args:
        file_name (str): input file name(.txt)
        output_dir(str): output directory path 
        separator (str): (comma or tab)
    """    
    try:
        pcs = read_data(file_name,separator)
        #if len(pcs.columns)!= 8:
        #    raise DataFormatException
        #if intensity==True:
        #    pcs = pcs.drop(pcs.columns[6], axis=1) # drop intensity
        os.makedirs(output_dir,exist_ok=True)
        if drop_color:
            pcs= pcs.iloc[:,3:6]=0
        output_file_name = os.path.join(output_dir,os.path.basename(os.path.splitext(file_name)[0])+".npy")
        np.save(output_file_name, pcs.values)
        return True
    except DataFormatException as de:
        logger.debug(de)
    except Exception as e:
        return False        
    
    
def convert_files(input_dir:str,output_dir:str, is_annotated =True,separator:str=",",drop_color=False)->bool:
    files = glob.glob(os.path.join(input_dir, "*"+".txt"))
    os.makedirs(output_dir,exist_ok=True)
    some_error = False
    if is_annotated==True:
        convert = from_CCannotation_to_xyzrgbl
    else:
        convert = from_xyzrgb_to_xyzrgbl
    ng_files = []
    for f in tqdm(files):
        if(convert(f,output_dir, separator,drop_color))==False:
            ng_files.append(f)
    if len(ng_files) !=0:
        print("!!! Some files failed to convert. !!!")
        some_error = True
        for f in ng_files:
            print(f)
    return some_error
    
def from_xyzrgb_to_xyzrgbl(file_name:str, output_dir:str, separator = ",",drop_color=False)->bool:
    """_summary_
    Read not annotated files(.txt) and add dummy label to generate .npy files
    Args:
        file_name (str): input filename(.txt)
        output_dir(str): output directory path      
        separator (str): (comma or tab)
    """    
    try:
        pcs = read_data(file_name,separator)
        pcs = pcs.iloc[:,0:6]
        #print(pcs)
        #pcs = drop_duplicates(pcs) 
        pcs["l"]=1 # dummy label
        os.makedirs(output_dir,exist_ok=True)
        if drop_color:
            pcs.iloc[:,3:6]=0
        
        output_file_name = os.path.join(output_dir,os.path.basename(os.path.splitext(file_name)[0])+"_test.npy")
        np.save(output_file_name, pcs.values)
        return True
    except Exception as e:
        logger.debug(e)
        return False
    
    