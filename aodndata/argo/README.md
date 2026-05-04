# ARGO ETL Pipeline

## Overview

The ARGO pipeline ingests Argo float profile data that has been synchronised from the [Argo Global Data Assembly Centre (GDAC)](https://www.argodatamgt.org/) onto a local filesystem via `rsync`. The pipeline handler (`ArgoHandler`) processes an `rsync` change manifest, uploads new/updated NetCDF profile files to S3, and removes deleted files from both S3 and the AODN catalogue.

Argo float data is managed under the IMOS (Integrated Marine Observing System) programme and published to the path `IMOS/Argo/dac/` in the AODN data store.

---

## Schedule

The schedule is **not managed within this repository**. The upstream `rsync` script (maintained in the [data-services](https://github.com/aodn/data-services) repository) runs periodically to mirror Argo GDAC data to a local working directory (`$WIP_DIR/Argo/dac`). Each time the `rsync` run completes, it deposits a `.rsync_manifest` file into the pipeline's incoming directory to trigger this handler.

A **lock file** mechanism (`argo.lock`) prevents the rsync script from starting a new run while the pipeline is actively processing a manifest:

- The lock file is created at the start of processing (`preprocess`).
- It is deleted once processing finishes (`postprocess`).
- The rsync script checks for the existence of `argo.lock` before starting a new sync.

---

## Inputs

| Item | Detail |
|------|--------|
| **Trigger file** | A single `.rsync_manifest` file dropped into the pipeline's incoming directory |
| **Allowed extensions** | `.rsync_manifest` only |
| **Referenced data** | NetCDF (`.nc`) Argo float profile files located under `$WIP_DIR/Argo/dac/` |

### rsync manifest format

The manifest is an `rsync` itemised change log. Each line represents one filesystem event:

| rsync prefix | Meaning | Pipeline action |
|-------------|---------|----------------|
| `>f.st......` | File transferred (new or updated) | Upload to S3 + harvest to catalogue |
| `*deleting` | File or directory deleted from source | Remove from S3 + unharvest from catalogue |
| `.d..t......` | Directory timestamp updated | Ignored (no action) |

Example manifest:
```
*deleting   aoml/1900709/profiles/
.d..t...... aoml/1900709/
>f.st...... csiro/1901119/profiles/D1901119_001.nc
*deleting   handlers/dummy/aoml/1900728/1900728_Rtraj.nc
```

Only entries for `.nc` files produce pipeline actions; all other file types (e.g. `.bad`, `.txt`) are set to `NO_ACTION` and discarded.

---

## Processing Steps

1. **Resolve** – The `MapManifestResolveRunner` (from `aodncore`) reads the manifest and maps each entry to a `PipelineFile` object, resolving absolute paths relative to `$WIP_DIR/Argo/dac`.

2. **Preprocess**
   - Non-NetCDF files in the collection are assigned `PipelineFilePublishType.NO_ACTION` (skipped).
   - An `argo.lock` file is created in the incoming directory to block concurrent rsync runs.

3. **Check** – NetCDF files are subject to format checking (`FORMAT_CHECK`) to ensure they are valid NetCDF.

4. **Publish** – Each eligible file is published according to its type:
   - New/updated `.nc` files → `HARVEST_UPLOAD` (upload to S3 and index in the AODN catalogue).
   - Deleted `.nc` files → `DELETE_UNHARVEST` (remove from S3 and remove from the AODN catalogue).

5. **Postprocess** – The `argo.lock` file is removed, allowing the rsync script to begin its next run.

---

## Outputs

| Output | Detail |
|--------|--------|
| **S3 destination path** | `IMOS/Argo/dac/<dac>/<float_id>/<file>` (e.g. `IMOS/Argo/dac/csiro/1901119/profiles/D1901119_001.nc`) |
| **Catalogue** | Files are harvested into / removed from the AODN catalogue as appropriate |
| **Lock file** | `argo.lock` created/deleted in `$INCOMING_DIR/Argo` during each run |

The destination path is derived by taking the file's path relative to `$WIP_DIR/Argo/dac` and prepending `IMOS/Argo/dac/`.

---

## Code Location

| Item | Path |
|------|------|
| Handler class | `aodndata/argo/handler.py` – `ArgoHandler` |
| Unit tests | `test_aodndata/argo/test_argoHandler.py` |
| Test fixtures | `test_aodndata/argo/` (`.rsync_manifest` examples, sample `.nc` file) |
| Entry point | `setup.py` → `ArgoHandler = aodndata.argo.handler:ArgoHandler` |

---

## Error Handling

| Scenario | Behaviour |
|----------|-----------|
| File listed in manifest but not present on disk | `MissingFileError` is raised; the handler reports an error |
| Non-NetCDF file in manifest | File is assigned `NO_ACTION` and silently skipped |
| Any unhandled exception | `argo.lock` is still removed in `postprocess` to unblock subsequent rsync runs |
