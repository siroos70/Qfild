# GeoSurvey Enterprise GIS Architecture

## System Overview

GeoSurvey is an enterprise-grade Survey and GIS system designed for QGIS Desktop 4.2.1 and QField 4.3.3.

## Dual-Platform Architecture

### Product A: QGIS Desktop Plugin
- **Target**: QGIS Desktop 4.2.1
- **Purpose**: Survey/GIS Control Center
- **Modules**: COGO, QC, Survey, Jobs, Import/Export, Settings

### Product B: QField Mobile Plugin
- **Target**: QField 4.3.3 (Android)
- **Purpose**: Field data collection
- **Modules**: GNSS, Survey Capture, Offline, Sync-ready

## Shared Data Model

### Coordinate System
- Display: X, Y, Z (projected coordinates)
- Storage: Real CRS via PyQGIS
- Default CRS: EPSG:32639 (UTM Zone 39N)

### Feature Model
- id, name, code, survey_date, surveyor
- accuracy, hdop, fix_type
- geometry, crs

## Agent Architecture

16 Agents defined in specification:
1. GIS Orchestrator
2. GIS Analyst Agent
3. GIS QC Agent
4. Field Operations Agent
5. GNSS/Survey Agent
6. GNAF Agent
7. Urban/Cadastre Agent
8. BI & Dashboard Agent
9. Report Agent
10. Data Management Agent
11. Document Intelligence Agent
12. Workflow Agent
13. Project Manager Agent
14. Monitoring & Alert Agent
15. AI Assistant/Voice GIS Agent
16. Security Agent

## Key Design Decisions

1. **No Fake Data**: All computations use real PyQGIS APIs
2. **Offline First**: QField works without internet
3. **Real COGO**: All geometry computations are mathematically correct
4. **Real QC**: Quality control uses actual geometric checks
5. **Independent Packages**: Desktop and Mobile are separate ZIP files

## Technology Stack

- QGIS Desktop 4.2.1
- QField 4.3.3
- Qt 6.11.1
- PyQt6
- PyQGIS
- Python 3.12