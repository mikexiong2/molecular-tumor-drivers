# Tumor Driver Atlas

A self-contained molecular pathology study website covering 401 broad malignant tumor entries in 18 organ and lineage groups, with 232 linked taxonomy and molecular references.

Includes searchable reference cards, SNV/indel–copy number–rearrangement comparisons, a printable info sheet, flashcards, bookmarks and browser-local learning progress. All CSS, JavaScript and study data are embedded in `index.html`. No API key, backend, package installation or build step is needed to publish the supplied page.

## Publish on GitHub Pages

1. Extract this ZIP on your computer. Upload the extracted files, not the ZIP itself.
2. Create a GitHub repository, for example `tumor-driver-atlas`.
3. Add the **contents** of this folder to the repository. `index.html` should be directly at the repository root, alongside this README and the `source` folder. Do not put them inside an extra enclosing folder.
4. Include the empty `.nojekyll` file. If your computer hides dotfiles, use GitHub’s **Add file → Create new file**, name it `.nojekyll`, and commit it. This tells Pages to serve the static files directly.
5. Open the repository’s **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, then **main** (or the branch containing these files) and **/(root)**. Save.
6. Wait for the Pages deployment to finish, then open the website address shown in Settings → Pages.

GitHub documentation: [Configure a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) and [Create a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).

The entry page also works by opening `index.html` directly. Bookmarks and learning progress are saved in that browser, separately for each website address. They do not transfer automatically from the original hosted page or the offline file to GitHub Pages.

## Files

| File or folder | Purpose |
| --- | --- |
| `index.html` | Ready-to-host page with all styling, interactions and data embedded. |
| `.nojekyll` | Disables Jekyll processing on GitHub Pages. |
| `.gitignore` | Excludes common local system and Python cache files from Git. |
| `source/template.html` | Editable page layout, CSS and JavaScript, with a data placeholder. |
| `source/data/*.json` | Five editable source datasets: visceral, epithelial, neuro/mesenchymal, hematologic and supplementary entries. |
| `source/data/build_*.py` | Four optional authoring helpers retained from the original project. They regenerate their corresponding dataset files. |
| `source/build.py` | Portable assembler; combines the datasets, applies the existing editorial corrections and writes the root `index.html`. |
| `source/atlas.json` | Generated consolidated dataset containing all entries, sources and scope notes. |
| `SHA256SUMS.txt` | Checksums for the files in this export. |

Only `index.html` is needed to run the atlas. Keep the source files if you want to edit or extend it. The original hosting-provider metadata, Git history and environment-specific deployment files are omitted because GitHub Pages does not use them.

## Edit and rebuild

Python 3 is needed only if you want to rebuild after editing. It uses the standard library; there are no dependencies to install.

- Edit appearance and behavior in `source/template.html`.
- Edit tumor entries, source links or scope notes in `source/data/*.json`.
- Review the editorial-corrections section in `source/build.py` when changing the affected records.
- `source/atlas.json` is generated output. Edit the source datasets instead.

From this folder, run:

```sh
python3 source/build.py
```

On Windows, you can use:

```powershell
py -3 source/build.py
```

Commit the updated root `index.html` along with your source changes. GitHub Pages serves that generated file; it does not run the Python assembler for this setup.

The optional `source/data/build_*.py` helpers are not part of the normal build. Running one overwrites its corresponding JSON dataset, so incorporate your changes into that helper first if you choose to use it. `visceral.json` was authored directly and has no separate generator.

## Content scope and verification

The medical content retains its original review date of 19 October 2026. This export was prepared on 21 October 2026 and does not constitute a new literature review.

This is an independent educational synthesis based on the WHO 5th edition, with broad diagnoses and selected molecular distinctions. Completeness against every current WHO entity and every 6th-edition revision has not been certified. The webpage contains detailed grouping, evidence and exclusion notes. An empty alteration column does not imply a negative molecular test; listed alterations may occur only in subsets.

The export was checked for complete data/source references and an identical generated entry page. Search, filtering, bookmarks, flashcard logic and print-sheet generation passed the original logic checks. Visual browser QA remained unavailable because the browser tool could not verify an administrator security policy.

The initial `SHA256SUMS.txt` applies to this delivered export; it will no longer match files that you subsequently edit or rebuild differently.
