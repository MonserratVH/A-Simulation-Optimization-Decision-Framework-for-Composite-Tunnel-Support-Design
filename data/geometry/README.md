# Geometry files

This directory contains the tunnel cross-section used by the PLAXIS model.

Included:
- `SeccionSMIGTunelVer02a.dxf`: tunnel cross-section.

Required but not supplied in the source material:
- `SeccionSMIG.dxf`: topographic/soil-domain geometry imported before the tunnel cross-section.

Place the missing file in this directory and keep the filename, or change `PLAXIS_TOPOGRAPHY_DXF` in `.env`.
