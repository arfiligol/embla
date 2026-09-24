# Plotly Design Kit

Plotly Design Kit is the shared home for versioned Python presentation choices for Plotly figures and `go.Table` tables. Its intended scope covers visual themes and templates, interaction configuration, and output profiles that consumers can apply consistently.

The Kit owns presentation behavior. Consumer repositories own their scientific data and meaning, including units, normalization, axis ranges, and domain-specific calculations. This repository does not own SCQ or SCGSim source and does not replace the Quarto Design Kit.

This repository is at the beginning of a **CONVERGING** V1. The Python API, profile names, packaging, and failure behavior have not been selected or accepted. No importable implementation or release is provided yet. Product behavior will be defined with the Human before an implementation is proposed for acceptance.

Development checkpoints are delivered on `develop`; promotion to `main` is a separate decision. Personal-Presentations records an exact child commit as a submodule pin when its root owner integrates one.
