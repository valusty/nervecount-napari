[![DOI](https://zenodo.org/badge/920814706.svg)](https://doi.org/10.5281/zenodo.17037042)

nervecount-napari
===============

nervecount: a napari plugin for the segmentation of immunofluorescent images of nerve transverse sections for the evaluation of morphometric parameters of axons

This tool processes confocal images stained for Neurofilament Heavy Chain (NfH), a marker for axons, to extract key morphometric parameters. The plugin automates all needed processes, making it a helpful tool for evaluating axonal morphometry. Additionally, the plugin is optimized to run efficiently without requiring high-performance hardware

------

### Preprocessing

The `preprocessing` is designed to preprocess image data for further segmentation and analysis. This setup performs several steps, including background correction of the chosen channel, maximum projection of the 3D picture, and median filtering, which help enhance image quality

#### Parameters

- `image` (Image): The image object containing data for further processing. *Note: At this stage, the image should contain more than one optical plane along the Z-axis*
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

------

### Multi-Otsu

The `multiotsu` function applies the Multi-Otsu thresholding method to segment an image into multiple regions based on pixel intensity, identifying different structures or areas in the image that exhibit distinct intensity values.

#### Parameters

- `image` (Image): The image object containing data for further processing - *chose `{image.name}_ch{channel}_preprocessed`*

#### Steps

1.  Multi-Otsu thresholding for determining multiple threshold values that divide the pixel intensities of the image into different regions - *for distinguishing between different structures based on the intensity*
2. Segmentation into regions based on the calculated thresholds 
3.  Masking for division of our image into different regions: `length_mask_raw` and `top_mask_raw` correspond to the specific areas based on the thresholds (in this case, `regions_img == 1` for one region and `regions_img == 2` for another) - *for ensuring that only the correctly aligned axons are measured, avoiding measurements of misdirected or incorrectly oriented axons, which can negatively impact subsequent morphometric analysis*

#### Output

- `{image.name}_top_multiotsu` (Label): A label mask for the region identified as "top"

------

### Opening

The `opening` operation applies a morphological opening to a label mask, refining and smoothing the labeled regions to eliminate small noise and smooth boundaries by removing small objects or gaps within the label regions

#### Parameters

- `label` (Label): The label object containing the mask to be processed - *chose `{image.name}_top_multiotsu`*
- `morph_disk` (int): The kernel for the morphological opening operation (default is `2`)

#### Steps

1. Morphological opening with a disk-shaped kernel of size `morph_disk` - *for smoothing the boundaries of the labeled regions and removing small noise from the label mask*

#### Output

- `{image.name}_top_multiotsu_opened` (Label): A label mask where small objects and gaps are removed

------

### Watershed segmentation

The `watershed_seg` applies the watershed segmentation technique to label regions in an image based on the distance transform - for separating overlapping or closely connected objects, such as axons, and for enhancing boundaries to distinguish distinct regions in the label mask

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

------

### Quantify all

The `quantify_all` is designed to quantify various properties of labeled regions in an image, such as axon measurements and intensity properties, and save the results as a CSV file. It computes morphometric properties for each region, including major and minor axis lengths, area, and intensity, and then generates summary statistics for the entire field of view

#### Parameters

- `image` (Image): The image object containing the data to be analyzed -  *chose `{image.name}_ch{channel}_max_pr`*
- `label` (Labels): The label object containing the mask for the segmented regions - *chose `{label.name}_watershed`*
- `date_microscopy` (str): The date when the microscopy image was taken
- `op_date` (str): The date of the operation or analysis
- `animal` (str): The animal identifier for the experiment
- `paw` (Literal, ['L', 'R']): The paw designation, either 'L' for left or 'R' for right
- `group` (Literal, ['co', 's_tube', 'eptfe', 'autoneuropl', 'neurorr', 'scaffold']): The experimental group (default is `'co'`)
- `spot` (Literal, ['ps', 'tube', 'ds']): The spot designation in the experiment (default is `'ps'`)
- `pixel_size` (float): The pixel size in micrometers per pixel (default is `0.317`)
- `image_dimensions` (int): The dimension of the image in pixels (default is `1024`)
- `saving_path` (Path): The path where the results will be saved as a CSV file (default is the current working directory)

#### Steps

1. Extraction of various properties from the labeled regions, including mean intensity, area, and axis lengths (major and minor axes)
2. Conversation of the axis lengths (*major and minor*) are converted from pixels to micrometers using the provided `pixel_size`
3. Calculation of the axis ratio (*minor/major axis*), as well as additional summary statistics, including:
   1. Total number of labels
   2. Total area of axons in the field of view
   3. Area of axons as a percentage of the total image area
   4. Area of axons in square millimeters and as a percentage of the total area

4. Saving quantification results and summary statistics are concatenated into a final data frame as a CSV file at the specified `saving_path`. The filename includes the operation date, experimental group, paw, and spot 
5. Displaying results for preview

#### Output

- `{op_date}_{group}_{paw}_{spot}_{image.name}_quantification.csv`:  A .csv file containing the detailed properties for each labeled region and summary statistics for the entire field of view

------

### Additional: Analyze

The `analyze` combines multiple processing and segmentation steps into a single pipeline, automating image preprocessing, thresholding, morphological operations, and watershed segmentation. It integrates the functionality of `preprocessing`, `multiotsu`, `opening`, and `watershed_seg` into one process

#### Parameters

- `image` (Image): The input image to be analyzed
- `channel` (int): The selected image channel for processing (default is `1`)
- `ax` (int): The axis along which the maximum projection is calculated (default is `0`)
- `morph_disk_prepro` (int): Kernel size for median filtering in the preprocessing step (default is `2`)
- `morph_disk_opening` (int): Kernel size for morphological opening  (default is `2`)

#### Output

- `{image.name}_ch{channel}_max_pr` (Image): Maximum projection of the selected channel
- `{image.name}_ch{channel}_preprocessed'` (Image): Preprocessed image after median filtering
- `{image.name}_top_multiotsu_opened` (Label): Segmentation mask after morphological opening
- `{image.name}_watershed_boundaries` (Label): Boundary mask of segmented objects
- `{image.name}_watershed` (Label): Watershed-segmented label mask

------

### Further directions & modifications

We are actively working on expanding the functionality of `nervecount` to support additional cases, including:

1. A function for creating and appending data to an existing dataset, containing data from all analyzed images, allowing for easier analysis of results across multiple images and groups of animals
2. Developing a segmentation pipeline for detecting myelin sheaths on confocal images stained for NfH and myelin basic protein (MBP)

Also in plans is the development of a pipeline for analysis of images for detecting both myelinating and non-myelinating Schwann cells on confocal images stained for NfH and S100

------

### Installation 

Set up a new conda environment with Python 3.12:

```
conda create -n nervecount python>3.12 
```

Activate existing environment:

```
conda activate nervecount
```

Install napari:

```
python -m pip install "napari[all]"
```

Clone the repository:

```
git clone https://github.com/valusty/nervecount-napari.git
```

Open the cloned repository via `cd` and install the plugin locally with `pip`:

```
cd nervecount-napari
python -m pip install .
```

------

### Cite this work

If you use this plugin in your research, please cite:

```bibtex
@software{ustymenko_nervecount_2025,
  author       = {Ustymenko, Valeriia},
  title        = {valusty/nervecount-napari: v0.1.0-beta},
  version      = {v0.1.0-beta},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.17037042},
  url          = {https://doi.org/10.5281/zenodo.17037042}
}
```
