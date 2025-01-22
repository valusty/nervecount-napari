import napari
from napari import Viewer
from napari.layers import Image, Labels
from napari.utils.notifications import show_info
from napari.qt.threading import thread_worker

from magicgui import magic_factory
from typing import Literal

import numpy as np

from skimage import filters, morphology, measure
from skimage.segmentation import watershed, find_boundaries
from skimage.feature import peak_local_max
from skimage.measure import regionprops, label

import scipy
from scipy import signal, stats, ndimage

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas

import pandas as pd

@magic_factory(call_button='analyze')
def analyze(viewer:Viewer, image:Image, channel:int=1, ax:int=0, morph_disk_prepro:int=2, morph_disk_opening:int=2):
    image_data = image.data
    image_channel = image_data[channel]
    bc_p = lambda x:np.array([f - np.percentile(f, 1) for f in x]).clip(min=0).astype(dtype=x.dtype)
    corr_image = bc_p(image_channel)
    max_pr=np.max(corr_image, axis=ax)
    median_image=filters.median(max_pr, footprint=morphology.disk(morph_disk_prepro))

    thresholds = filters.threshold_multiotsu(median_image)
    regions_img = np.digitize(median_image, bins=thresholds)
    length_mask_raw = regions_img == 1
    top_mask_raw = regions_img == 2

    nfh_mask = morphology.opening(top_mask_raw, footprint=morphology.disk(morph_disk_opening))

    label_data = nfh_mask.astype(int)
    distance = ndimage.distance_transform_edt(label_data.astype(bool))
    local_maxi = peak_local_max(distance, footprint=np.ones((3, 3)), labels=(label_data.astype(bool)))
    peaks_mask = np.zeros_like(distance, dtype=bool)
    peaks_mask[tuple(local_maxi.T)] = True
    markers = morphology.label(peaks_mask)
    labels_ws = watershed(-distance, markers, mask=label_data.astype(bool))
    ans = labels_ws.astype(int)
    boundary_mask = find_boundaries(ans, mode='outer').astype(int)
    
    viewer.add_image(median_image, name=f'{image.name}_ch{channel}_preprocessed')   
    #viewer.add_labels(top_mask_raw, name=f'{image.name}_top_multiotsu')
    viewer.add_labels(nfh_mask, name=f'{image.name}_top_multiotsu_opened')
    viewer.add_labels(boundary_mask, name=f'{image.name}_watershed_boundaries')
    viewer.add_labels(ans, name=f'{image.name}_watershed')
    

@magic_factory(call_button='preprocessing')
def preprocessing(viewer:Viewer, image:Image, channel:int=1, ax:int=0, morph_disk:int=2):
    image_data = image.data
    image_channel = image_data[channel]
    bc_p = lambda x:np.array([f - np.percentile(f, 1) for f in x]).clip(min=0).astype(dtype=x.dtype)
    corr_image = bc_p(image_channel)
    max_pr=np.max(corr_image, axis=ax)
    median_image=filters.median(max_pr, footprint=morphology.disk(morph_disk))
    viewer.add_image(median_image, name=f'{image.name}_ch{channel}_preprocessed')

@magic_factory(call_button='multiotsu')
def multiotsu (viewer:Viewer, image:Image):
    image_data = image.data
    thresholds = filters.threshold_multiotsu(image_data)
    regions_img = np.digitize(image_data, bins=thresholds)
    length_mask_raw = regions_img == 1
    top_mask_raw = regions_img == 2
    viewer.add_labels(top_mask_raw, name=f'{image.name}_top_multiotsu')

@magic_factory(call_button='opening')
def opening(viewer:Viewer, label:Labels, morph_disk:int=2):
    label_data = label.data
    nfh_mask = morphology.opening(label_data, footprint=morphology.disk(morph_disk))
    viewer.add_labels(nfh_mask, name=f'{label.name}_top_multiotsu_opened')

@magic_factory(call_button='watershed_seg')
def watershed_seg(viewer:Viewer, label:Labels):
    label_data = label.data.astype(int)
    distance = ndimage.distance_transform_edt(label_data.astype(bool))
    local_maxi = peak_local_max(distance, footprint=np.ones((3, 3)), labels=(label_data.astype(bool)))
    peaks_mask = np.zeros_like(distance, dtype=bool)
    peaks_mask[tuple(local_maxi.T)] = True
    markers = morphology.label(peaks_mask)
    labels_ws = watershed(-distance, markers, mask=label_data.astype(bool))
    ans = labels_ws.astype(int)
    boundary_mask = find_boundaries(ans, mode='outer').astype(int)
    viewer.add_labels(boundary_mask, name=f'{label.name}_watershed_boundaries')
    viewer.add_labels(ans, name=f'{label.name}_watershed')

@magic_factory(call_button='quantify_all')
def quantify_all(viewer:Viewer, image:Image, label:Labels, 
                 paw:str, date_microscopy:str, op_date:str,
                 group:Literal['co','s_tube', 'eptfe', 'autoneuropl', 'neurorr', 'scaffold']='co', 
                 spot:Literal['ps','tube','ds']='ps', 
                 pixel_size:float=0.317
                 ):
    image_data = image.data
    label_data = label.data.astype(int)
    nfh_quantity_dict = measure.regionprops_table(label_data, intensity_image=image_data, 
                                                properties=("label", "intensity_mean", "area", "axis_major_length", "axis_minor_length"))
    nfh_quantity_df = pd.DataFrame(nfh_quantity_dict)
    nfh_quantity_df['major_length_um'] = nfh_quantity_df['axis_major_length'] * pixel_size
    nfh_quantity_df['minor_length_um'] = nfh_quantity_df['axis_minor_length'] * pixel_size
    nfh_quantity_df['axis_ratio'] = np.divide(nfh_quantity_df['axis_minor_length'], nfh_quantity_df['axis_major_length'])
    nfh_quantity_df['name'] = f'{image.name}'
    nfh_quantity_df['date'] = date_microscopy
    nfh_quantity_df['op_date'] = op_date
    nfh_quantity_df['group'] = group[0] if len(group) == 1 else group
    nfh_quantity_df['paw'] = paw 
    nfh_quantity_df['spot'] = spot[0] if len(spot) == 1 else spot 
    viewer.add_table(nfh_quantity_df, name='NfH Quantity Data') 

