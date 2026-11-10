# SizaSense — Resilience Intelligence
Open-source prototype concept by Geo Regreen.

SizaSense explores how environmental intelligence can help institutions identify and prioritise environmental threats to water, WASH and essential services, including maternal and community healthcare.

## Data honesty
This is a demonstration prototype. All included facility names, locations, exposure values and water observations are synthetic examples for interface testing. They are not actual clinic records, satellite measurements, verified water-quality results, community interviews or evidence of service disruption.

The prototype does not predict clinic closure, determine route passability, diagnose health conditions or establish water contamination. Scores are transparent triage indicators for human review.

## Run locally
Python 3.11 recommended:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
Run tests with `pytest -q`.

## Included
- Interactive map and service-exposure dashboard
- SizaPulse service-resilience view
- SizaLens WASH observation view
- Explainable weighted exposure-priority score
- Human-review actions and CSV export
- Data-status and safeguarding warnings

## Next increments
1. Replace synthetic sites with curated, licensed and verified facility data.
2. Add dated Sentinel-1 flood layers and Sentinel-2 water/vegetation change indicators with provenance and quality flags.
3. Add verified road-network routing and facility operating status.
4. Integrate accredited laboratory water-quality data with units, methods, dates and verification status.
5. Co-design a privacy-preserving community reporting workflow.
6. Validate against documented historical events and independent field observations before claiming model performance.

## Future production architecture
React/Next.js + MapLibre frontend; Python FastAPI; PostGIS; GeoPandas/Rasterio/Xarray processing; role-based access; standards-based GeoJSON/OGC APIs; secure managed hosting. Keep the first prototype small and explainable.

## Open-source release checklist
Confirm company ownership and contributor rights, audit dependencies, remove secrets, document data provenance, select licence, and publish security/contact and data-governance policies. Do not publish personal or sensitive health information.

## Licence
MPL-2.0. See `LICENSE`.
