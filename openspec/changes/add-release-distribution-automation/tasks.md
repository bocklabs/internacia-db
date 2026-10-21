## 1. Hugging Face
- [x] 1.1 Create HF dataset repo (or use org namespace)
- [x] 1.2 Add release workflow step to push Parquet + README dataset card
- [x] 1.3 Document HF URL in README

## 2. Zenodo automation
- [x] 2.1 Add Zenodo API deposit to release workflow using concept DOI parent
- [x] 2.2 Verify new version appears under existing concept DOI
- [x] 2.3 Remove the workflow deposit step; the Zenodo GitHub integration is the only depositor (concept DOI `10.5281/zenodo.20706176`)

## 3. Secrets and docs
- [x] 3.1 Document required GitHub secrets (HF token) in maintainer docs
- [x] 3.2 Update ATTRIBUTION.md with both distribution channels
