nervecount-napari
===============

nervecount: napari plugin for segmentation of immunofluorescent images of nerve transections for evaluation of morphometric parameters of axons

Based on official [naparu Plugins Guide](https://napari.org/stable/plugins/first_plugin.html)

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
- scikit-image

### Local installation in editable mode with `pip`:
```
python -m pip install -e .
```