# Embla

The visual review gallery is organized by chart type: lines, bars/markers, heatmaps, tables, 3D and diagrams. A unified Colors page contains 5/10/20-color sequences and theme surfaces. Scientific examples include control timelines,
pulse tracks, Bloch sphere animations, and annotated physical concept diagrams.
Example geometry and analytic illustrations are explicitly identified; consumers
retain scientific interpretation and device data.

Embla is a Plotly presentation reference: Plot Demos, copyable native Plotly templates and interaction configuration, and Usage Tutorials for people and agents. Its primary delivery is understandable presentation recipes rather than an installable package.

Embla owns presentation behavior. Consumer repositories own their scientific data and meaning, including units, normalization, axis ranges, and domain-specific calculations. This repository does not own SCQ or SCGSim source and does not replace Askr, the Quarto reading page.

This repository is at the beginning of a **CONVERGING** V1. The Python API, profile names, packaging, and failure behavior have not been selected or accepted. Copyable presentation recipes are available for review; no installed package or release is promised.

Development checkpoints are delivered on `develop`; promotion to `main` is a separate decision. Personal-Presentations records an exact child commit as a submodule pin when its root owner integrates one.

The documentation site uses [Askr 0.8.0](https://github.com/arfiligol/askr/releases/tag/v0.8.0) through the native `askr-html` format. Update the bundled extension with `quarto add arfiligol/askr@v0.8.0`.

## Contributor planning and delivery

External proposals prepared with ChatGPT Pro are optional design input for substantial work. Designate the Embla Lead as the single primary recipient for Embla-only proposals; resolve the responsible owner before editing across repositories. Small, clear fixes need no Pro prerequisite or Plan Mode.

The recipient checks the repository, branch, commit SHA, relevant source, work in progress, current contract, and available tool capabilities, then maintains the current execution plan in the existing work packet. Use Plan Mode to reconcile substantial proposals; if unavailable, keep intake read-only and request the mode change.

Under standing authorization, the original Git owner closes ordinary work by running the existing required checks, committing only the assigned changes to `develop`, pushing, and reading back the remote SHA. Report the repository, branch, full commit SHA, changed paths, check results, and pending items. If nothing changed, report that outcome without an empty commit.

Promotion to `main`, deployment, tags, releases, and root submodule pins require separate authorization.
