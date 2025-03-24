nervecount-napari
===============

nervecount: napari plugin for segmentation of immunofluorescent images of nerve transverse section for evaluation of morphometric parameters of axons

------

## Functions

------

### Preprocessing

The `preprocessing` function is designed to preprocess image data for further segmentation and analysis. This function performs several steps, including background correction of the chosen channel, maximum projection of 3D picture, and median filtering, which help enhance image quality

#### Parameters

- `image` (Image): The image object containing data for further processing
- `channel` (int): The specific channel of the image that contains data (default is `0`)
- `ax` (int):  The axis along which to compute the maximum projection (default is `0`)
- `morph_disk` (int): The disk size for the morphological median filter (default is `2`)

#### Steps

1. Background correction by subtracting the 1st percentile value from each pixel in the chosen `channel`, ensuring that the minimum pixel value is 0 - *for removing background noise*
2. Maximum projection along the specified axis (`ax`) - *for highlighting the most intense pixel values across slices and improving the visibility of features in 3D images*
3. A morphological median filter using a disk-shaped footprint with chosen kernel `morph_disk` - *for smoothing the image and reducing noise* 

#### Output

- `{image.name}_ch{channel}_max_pr` (Image): The maximum intensity projection of the corrected image - *for further usage in the quantification step*
- `{image.name}_ch{channel}_preprocessed` (Image): The median-filtered image after background correction and maximum projection

![image-20250324200414036](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324200414036.png)

------

### Multi-Otsu

The `multiotsu` function applies the Multi-Otsu thresholding method to segment an image into multiple regions based on pixel intensity for identifying different structures or areas in an image that exhibit distinct intensity values

#### Parameters

- `image` (Image): The image object containing data for further processing - *chose `{image.name}_ch{channel}_preprocessed`*

#### Steps

1.  Multi-Otsu Thresholding for determining multiple threshold values that divide the pixel intensities of the image into different regions - *for distinguishing between different structures based on the intensity*
2. Segmentation into regions based on the calculated thresholds 
3.  Masking for division of our image into different regions: `length_mask_raw` and `top_mask_raw` correspond to specific regions based on the thresholds (in this case, `regions_img == 1` for one region and `regions_img == 2` for another) - *for ensuring that only the correctly aligned axons are measured, avoiding measurements of misdirected or incorrectly oriented axons, which can negatively impact subsequent morphometric analysis*

#### Output

- `{image.name}_top_multiotsu` (Label): A label mask for the region identified as "top"

![image-20250324202600432](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324202600432.png)

------

### Opening

The `opening` function applies a morphological opening operation to a label mask to refine and smooth the labeled regions to eliminate small noise and smooth boundaries by removing small objects or gaps in the label regions

#### Parameters

- `label` (Label): The label object containing the mask to be processed - *chose `{image.name}_top_multiotsu`*
- `morph_disk` (int): The kernel for the morphological opening operation (default is `2`)

#### Steps

1. Morphological opening with a disk-shaped kernel of size `morph_disk` - *for smoothing the boundaries of the labeled regions and removing small noise from the label mask*

#### Output

- `{image.name}_top_multiotsu_opened` (Label): A label mask where small objects and gaps are removed

![image-20250324202705710](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324202705710.png)

------

### Watershed segmentation

The `watershed_seg` function applies the watershed segmentation technique to label regions in an image based on the distance transform - for separating overlapping or closely connected objects, such as axons, and for enhancing boundaries to distinguish distinct regions in the label mask

#### Parameters

- `label` (Label): The label object containing the mask to be processed - *chose `{image.name}_top_multiotsu_opened`*

#### Steps

1. Computing the distance transform of the label mask, where each pixel’s value represents the distance to the nearest background pixel - *to identify the center of each object in the image*
2. Identifying local maxima (peaks) in the image, which are potential markers for different regions - *for further definition of separate regions in the watershed segmentation*
3. Watershed segmentation - *for segmentation where different regions are separated based on their boundaries*
4. Detection of the boundaries of the segmented regions - *for highlighting the outer borders of the segmented regions*

#### Output

- `{label.name}_watershed_boundaries` (Label):  A label mask showing the boundaries of the segmented regions
- `{label.name}_watershed`): A label mask with the final watershed segmentation

![image-20250324202728720](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324202728720.png)

------

### Quantify all

The `quantify_all` function is designed to quantify various properties of labeled regions in an image, such as axon measurements and intensity properties, and save the results as a CSV file. This function computes morphometric properties for each region, including major and minor axis lengths, area, and intensity, and then generates summary statistics for the entire field of view

#### Parameters

- `image` (Image): The image object containing the data to be analyzed -  *chose `{image.name}_ch{channel}_max_pr`*
- `label` (Labels): The label object containing the mask for the segmented regions - *chose `{label.name}_watershed`*
- `date_microscopy` (str): The date when the microscopy image was taken
- `op_date` (str): The date of the operation or analysis
- `animal` (str): The animal identifier for the experiment
- `paw` (Literal['L', 'R']): The paw designation, either 'L' for left or 'R' for right
- `group` (Literal['co', 's_tube', 'eptfe', 'autoneuropl', 'neurorr', 'scaffold']): The experimental group (default is `'co'`)
- `spot` (Literal['ps', 'tube', 'ds'], optional): The spot designation in the experiment (default is `'ps'`).
- `pixel_size` (float, optional): The pixel size in micrometers per pixel (default is `0.317`).
- `image_dimensions` (int, optional): The dimension of the image in pixels (default is `1024`).
- `saving_path` (pathlib.Path, optional): The path where the results will be saved as a CSV file (default is the current working directory).

#### Steps

1. Computing the distance transform of the label mask, where each pixel’s value represents the distance to the nearest background pixel - *to identify the center of each object in the image*
2. Identifying local maxima (peaks) in the image, which are potential markers for different regions - *for further definition of separate regions in the watershed segmentation*
3. Watershed segmentation - *for segmentation where different regions are separated based on their boundaries*
4. Detection of the boundaries of the segmented regions - *for highlighting the outer borders of the segmented regions*

#### Output

- `{label.name}_watershed_boundaries` (Label):  A label mask showing the boundaries of the segmented regions
- `{label.name}_watershed`): A label mask with the final watershed segmentation

![image-20250324202923880](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324202923880.png)

------

### Additional: Analyze

![image-20250324202948379](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324202948379.png)

------

### Plugin structure:
```
nervecount-napari/
└── src/
│   └── nervecount_napari/
│       ├── __init__.py
│       ├── napari.yaml
│       └── _widget.py
├─── pyproject.toml
├─── setup.cfg
├─── README.md
├─── LICENSE
└─── .gitignore
```

### Dependency
- python >= 3.12
- matplotlib
- numpy
- os
- pandas
- pathlib
- scikit-image
- scipy

### Local installation in editable mode with `pip`:
```
python -m pip install -e .
```

