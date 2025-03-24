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

- `{image.name}_ch{channel}_max_pr` (Image) - the maximum intensity projection of the corrected image - *for further usage in the quantification step*
- `{image.name}_ch{channel}_preprocessed` (Image) - the median-filtered image after background correction and maximum projection

![image-20250324200414036](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324200414036.png)

------

### Multi-Otsu

The `multiotsu` function applies the Multi-Otsu thresholding method to segment an image into multiple regions based on pixel intensity for identifying different structures or areas in an image that exhibit distinct intensity values

#### Parameters

- `image` (Image): The image object containing data for further processing - *chose `{image.name}_ch{channel}_preprocessed`*

#### Steps

1.  Multi-Otsu Thresholding for determining multiple threshold values that divide the pixel intensities of the image into different regions - *for distinguishing between different structures based on intensity*
2. Segmentation into regions based on the calculated thresholds 
3.  Masking for division of our image into different regions: `length_mask_raw` and `top_mask_raw` correspond to specific regions based on the thresholds (in this case, `regions_img == 1` for one region and `regions_img == 2` for another) - *for ensuring that only the correctly aligned axons are measured, avoiding measurements of misdirected or incorrectly oriented axons, which can negatively impact subsequent morphometric analysis*

#### Output

- `f'{image.name}_top_multiotsu'` (Label) - a label mask for the region identified as "top"

![image-20250324202600432](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324202600432.png)

------

#### Opening

![image-20250324202705710](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324202705710.png)



![image-20250324202728720](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324202728720.png)



![image-20250324202923880](C:\Users\USER\AppData\Roaming\Typora\typora-user-images\image-20250324202923880.png)



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

