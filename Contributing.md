# Contributing Guidelines

Thank you for your interest in contributing to this project!

This project is primarily developed by **students as part of their bachelor theses**.  
The goal is to maintain a **high-quality, well-tested, well-documented, and secure academic codebase**, suitable for **research, reproducibility, and long-term maintenance** in the field of **process mining**.

Please read and follow these guidelines carefully.

---

## General Principles

- Keep changes **small, focused, and reviewable**
- Maintain **high code quality**
- Write **tests for all relevant code**
- Document your work clearly and precisely
- Follow established software engineering and academic best practices
- These rules apply to **all contributors**, including thesis students

---

## Security Requirements

### SSH Usage

All interactions with the repository **must use SSH**.

- HTTPS access is not allowed
- Configure an SSH key in your Forgejo account before cloning
- All pushes and fetches must use SSH URLs

Example:

`git clone git@code.swisdata.eu:your-username/processintel.git`

---

### GPG Commit Signing

All commits **must be cryptographically signed** using a GPG key.

- Unsigned commits will be rejected
- Your GPG key must be uploaded to your Forgejo profile
- This ensures authorship, accountability, and academic integrity

Enable commit signing:

```bash
git config --global commit.gpgsign true 
git config --global user.signingkey YOUR_KEY_ID
```

---

## Repository Workflow

### Forking the Repository

All work **must** be done in a fork of the main repository.

1. Create a fork of the repository on Forgejo
2. Clone your fork locally:

```bash
git clone git@code.swisdata.eu:your-username/processintel.git
```

3. Add the upstream repository:


```bash
git remote add upstream git@code.swisdata.eu:SWISDATA/processintel.git
```

Direct commits to the main repository are **not allowed**.

---

## Branch Rules

- Every change must be done in **its own branch**
- Never commit directly to `main`
- Branch names must be **descriptive**
### Branch Naming Examples

- `add-xes-support`
- `add-inductive-miner`
- `add-filtering-to-algorithms`
- `update-happy-path`

---

## Pull Requests

### One Purpose per Pull Request

Each Pull Request (PR) **must do exactly one thing**.

Allowed:

- One feature
- One bug fix
- One refactor

Not allowed:

- Mixing unrelated changes
- Combining features and fixes
- Large cleanup PRs

Split your work into **multiple PRs** if needed.

---

### Pull Request Requirements

Each PR must:

- Be based on a fork and a dedicated branch    
- Be formatted using **Black**
- Include **tests** for new or changed functionality
- Pass all automated checks
- Update documentation where applicable
- Clearly explain what was changed and **why**

PRs not meeting these requirements **will not be merged**.

---

## Code Formatting

This project **requires** the use of the **Black** code formatter.

- All Python code must be formatted with Black
- Formatting is not optional

Install and run:

```bash
pip install 
black black .
```

---

## Testing Requirements

All code **must be tested** using Python's **built-in `unittest` framework**.

- The project uses **`unittest` exclusively**
- Do **not** introduce alternative testing frameworks (e.g. `pytest`, `nose`)
- Tests must be reproducible, readable, and deterministic

### Test Structure Guidelines

- Place tests in the designated `tests/` directory
- Name test files as `<module>/<name>_test.py`
- Use descriptive test case and method names
- Each test should validate **one specific behavior**
    
PRs without appropriate `unittest`-based tests will be rejected unless **explicitly justified**.

---

## Docstring Guidelines (Mandatory)

### Required Docstring Format

All public functions, classes, and modules **must use NumPy-style docstrings**.
This format is **mandatory**.

#### Required structure

```python
"""Short summary of the function.

Parameters 
---------- 
param_name : type
     Description of the parameter. 
optional_param : type, optional
     Description, by default VALUE
       
Returns 
------- 
return_type
     Description of the return value.
     
Raises 
------ 
ExceptionType
     Description of when this exception is raised. 
"""
```

#### Docstring Rules

- Use **NumPy docstring format**
- Be precise and explicit
- Describe behavior, not implementation details
- All parameters and return values must be documented

Code without proper docstrings **will not be accepted**.

---

## Commit Message Guidelines

Commit messages must follow this format:

`<module>, <submodule>: short description`

Rules:

- Keep the description short and clear
- One logical change per commit

Examples:

```
parser, config: handle empty configuration files 
docs, architecture: add system overview diagram`
```
---

## Review Process

- All Pull Requests require review
- Feedback is part of the learning process
- Maintainers have final merge authority
- Changes may be requested for correctness or clarity

---

## Questions

If something is unclear, open an issue or contact your supervisor.  
As this is an academic project, **asking questions is encouraged**.

---

## Extending the Project

Guidelines for extending the project architecture (UI pages, views, algorithms, models, and data formats) are documented separately.

Before implementing new features, contributors **must read and follow**:

- [EXTENDING.md](docs/EXTENDING.md) - Architecture and extension guidelines

All extensions are expected to follow the documented MVC structure and existing templates.

---

Thank you for contributing to a **high-quality and secure** open source process mining project.