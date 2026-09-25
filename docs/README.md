# GeoSurvey Enterprise GIS

## Overview
Enterprise-grade Survey, GIS, GNSS, COGO, QC, GNAF, Cadastre and Offline/Sync system for QGIS Desktop 4.2.1 and QField 4.3.3.

## Architecture

```
PROJECT_ROOT/
├── desktop/GeoSurveyDesktop/     # QGIS Desktop 4.2.1 Plugin
├── mobile/GeoSurveyFieldTools/  # QField 4.3.3 Plugin
├── shared/                       # Shared modules
│   ├── coordinate-rules/         # Coordinate rules & transformations
│   └── specifications/           # COGO, QC, geometry engines
├── docs/                         # Documentation
├── tests/                        # Unit tests
└── releases/                     # ZIP packages
```

## Features

### QGIS Desktop
- COGO Engine (Bearing+Distance, Intersections, Offsets, Arcs)
- QC Engine (Geometry, Spatial, GNSS QC)
- Survey Tools (Point/Line/Polygon capture)
- Job Management
- Import/Export (SHP, GPKG, GeoJSON, CSV, KML, DXF, PDF)
- Settings Management

### QField Mobile
- Field Survey Capture (Point/Line/Polygon)
- GNSS Status Display
- Position Quality Assessment
- Offline-first design
- Sync-ready architecture

## Installation

### QGIS Desktop
1. Open QGIS Desktop 4.2.1
2. Go to Plugins > Manage and Install Plugins
3. Add from ZIP and select the desktop release ZIP
4. Enable the GeoSurveyDesktop plugin

### QField
1. Copy the mobile release ZIP to your Android device
2. Open QField 4.3.3
3. Go to Settings > Plugins
4. Install the GeoSurveyFieldTools plugin

## Testing

Run the COGO unit tests:
```
python tests/test_cogo.py
```

## Version
1.0.0