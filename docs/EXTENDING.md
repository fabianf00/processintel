## Introduction

This document describes **how to extend the project in a consistent and maintainable way**.

The goal is to ensure that all new functionality:

- follows the existing architecture,
- integrates cleanly with the UI and data flow,
- remains understandable for future students and contributors.

Before adding new pages, views, algorithms, or models, **read this document carefully**.

## Table of Contents

- [Architecture Overview (MVC)](#architecture-overview-mvc)
- [Adding a Page](#adding-a-page)
  - [Controller Methods](#controller-methods)
- [Adding a View to an Existing Page](#adding-a-view-to-an-existing-page)
- [Adding New Column Selections](#adding-new-column-selections)
- [Adding a Mining Algorithm](#adding-a-mining-algorithm)
  - [Views](#views)
  - [Controllers](#controllers)
  - [Mining Model](#mining-model)
  - [Converter](#converter)
  - [Registration](#registration)
- [Extending Models](#extending-models)
  - [Import Formats](#import-formats)
  - [Export Formats](#export-formats)
  - [Prediction Model](#prediction-model)


---
## Architecture Overview (MVC)

This project **uses the Model-View-Controller (MVC) pattern**, and all extensions must follow this architecture.

- **Models** contain business logic and data processing
- **Views** render UI elements only
- **Controllers** handle user input, session state, and coordination

Views must not contain logic, and models must not depend on UI code.

---

## Adding a Page

Each page follows the MVC pattern and requires:

- One **controller**
- One **view**

Both must be placed in a dedicated folder inside the `ui` package.  
Business logic must be implemented in **models**.

Recommended template:

`templates/ui_template`

### Controller Methods

Controllers must implement:

- `process_session_state` - reads or initializes session state
- `select_view` (optional) - required if multiple views exist
- `run` - executed on every reload

Views should use one method per section when possible and may use `create_layout` to structure content.

Register the page in `streamlit_app.py` with a route.

---

## Adding a View to an Existing Page

- Store the new view in the same folder as the page
- Inherit from `BaseView` or the existing page view
- Implement `select_view` in the controller to switch views

Example:

```python
def select_view(self):
     if self.selected_algorithm == "heuristic":
	    return self.views[1], 1
	return self.views[0], 0
```

Adapt the controller's `run` method if views differ in functionality.

---

## Adding New Column Selections

Column selections can be extended using templates from:

`templates/column_selection_template`

Available templates:

- `BaseColumnSelectionViewTemplate` - no predefined columns
- `ExtendedColumnSelectionViewTemplate` - includes time, case, and event columns

Required steps:

- Add entries to `needed_columns` and `column_styles`
- Render selections using keys matching column names
- Update `select_view` in `ColumnSelectionController`
- Override `transform_df_to_log` in the algorithm controller to include new columns

---

## Adding a Mining Algorithm

A mining algorithm consists of:

- `AlgorithmView`
- `AlgorithmController`
- `MiningModel`

Use the template:

`templates/algorithm_ui_template`

### Views

- Must inherit from `BaseAlgorithmView`
- Define sliders in `render_sidebar`
- Slider keys must match session state keys

### Controllers

Controllers must inherit from `BaseAlgorithmController` and override:

- `process_algorithm_parameters`
- `perform_mining`
- `have_parameters_changed`
- `get_sidebar_values`

Override `transform_df_to_log` if additional data or formats are required.

### Mining Model

- **Must inherit from `BaseMining`**
- Must store the resulting graph in `self.graph`
- Graph type must be `BaseGraph`

### Converter

Mining algorithms do **not** directly create visualization graphs.

Instead, a **converter** is required:

- The converter takes the **internal state of the mining algorithm**
- It transforms this state into one of the supported graph types

Currently supported graph implementations are:

- **BPMN**
- **Petri net**
- **Directly-Follows Graph (DFG)**


The converter is responsible for:

- Translating algorithm-specific data structures
- Producing a valid `BaseGraph` instance

Custom graph types may be added in `graphs/visualization`, provided a corresponding converter is implemented.

### Registration

To make the algorithm available:

- Add entries to `algorithm_mappings`
- Add entries to `algorithm_routes` in `config.py`

Documentation must be added in `docs/algorithms`.

---

## Extending Models

### Import Formats

- Add the file type to `import_file_types_mapping`
- Update `HomeController.process_file`
- Implement the reader in `ImportOperations`

### Export Formats

- Update `graph_export_mime_types`
- Update `ExportController`
- Add the exporter to `ExportOperations`

### Prediction Model

- Extend the existing prediction dictionary, or
- Replace the model while keeping the function signature stable