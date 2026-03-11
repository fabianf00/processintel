# Setup Guide

This guide explains how to set up the development environment required for working with **ProcessIntel**.

The setup includes:

- Python installation
- Conda environment (Miniforge)
- Graphviz installation
- Nix development environment
- SSH configuration for GitHub access
- GPG commit signing

Most steps only need to be done **once per machine**.

---

## Table of Contents

- [Python Setup](#python-setup)
  - [Option 1: Install Python from python.org](#option-1-install-python-from-pythonorg)
  - [Option 2: Install Python using Miniforge (Recommended)](#option-2-install-python-using-miniforge-recommended)
  - [Working with Conda Environments](#working-with-conda-environments)
- [Graphviz Setup](#graphviz-setup)
- [Nix Setup](#nix-setup)
  - [Running the Project with Nix](#running-the-project-with-nix)
- [SSH Key Setup](#ssh-key-setup)
- [GPG Key Setup](#gpg-key-setup)
- [Common Problems](#common-problems)

---

## Python Setup

ProcessIntel requires **Python 3.12 or newer**.

You can either install Python directly from the official website or use **Miniforge**, which is recommended for managing environments.

### Option 1: Install Python from python.org

Download Python from the official website:

https://www.python.org/downloads/

Follow the installer instructions for your operating system.

Verify the installation:

```bash
python3 --version
```

or
```bash
python --version
```
You should see something similar to:
```bash
Python 3.12.x
```
The version must be 3.12 or higher.

### Option 2: Install Python using Miniforge (Recommended)

Miniforge is a lightweight Conda distribution that uses the conda-forge ecosystem by default and provides a convenient way to manage Python versions and dependencies.

Download Miniforge:

https://github.com/conda-forge/miniforge

Choose the installer for your operating system and follow the installation instructions.

Verify the installation:
```bash
conda --version
```

#### Working with Conda Environments

Create a new environment for the project:
```bash
conda create -n processintel python=3.13
```
Activate the environment:
```bash
conda activate processintel
```
Install project dependencies:
```bash
pip install -r requirements.txt
```
Run the application:
```bash
python -m streamlit run app/streamlit_app.py
```
Deactivate the environment when finished:
```bash
conda deactivate
```
Using environments keeps dependencies isolated from other projects and prevents version conflicts.

---

## Graphviz Setup

Graphviz is required for **process model rendering** in ProcessIntel.

### Installation

Download and install Graphviz from the official website:

https://graphviz.org/download/

Follow the installer instructions for your operating system.

### Verify Installation

After installation, verify that Graphviz is available in your system:

```bash
dot -V
```

If the installation was successful, the command will print the installed Graphviz version.

### PATH Configuration

Ensure that the Graphviz `bin` directory is available in your system `PATH`.

Example locations:

* **Windows:** `C:\Program Files\Graphviz\bin`
* **macOS / Linux:** usually added automatically by the package manager

If `dot -V` is not recognized, you may need to manually add the `bin` directory to your `PATH`.

---

## Nix Setup

ProcessIntel can also be run using Nix, which provides reproducible development environments.

Install Nix:

https://nixos.org/download.html

Follow the installation instructions for your operating system.

Verify the installation:
```bash
nix --version
```

### Running the Project with Nix

Enter the development environment:
```bash
nix develop --impure
```
This command opens a Nix development shell defined by the repository's Nix configuration.

Once the development shell has been entered:

- all required project dependencies are automatically available
- the correct Python version is provided
- standard Python commands can be executed normally
- the development shell is reproducable across machines

You can now start the application:
```bash
python -m streamlit run app/streamlit_app.py
```
Exit the development shell with:
```bash
exit
```
This approach avoids installing dependencies globally and ensures a reproducible development environment.

---

## SSH Key Setup

SSH access is required for interacting with GitHub repositories. If you already have an SSH key, you can skip the SSH key generation step.

### Step 1: Generate an SSH Key

Generate a new SSH key using the modern ed25519 algorithm:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/<filename>
```

###  Step 2: Add the SSH Key to the SSH Agent

Start the SSH agent:
```bash
eval "$(ssh-agent -s)"
```

Add the SSH private key:
```bash
ssh-add ~/.ssh/<filename>
```

### Step 3: Add the SSH Key to GitHub

Get your public key:
```bash
cat ~/.ssh/<filename>.pub
```
Then:
1. Open your GitHub account
2. Go to Settings -> SSH and GPG Keys
3. Click New SSH Key
4. Paste the key and save

Never upload the private key. Only the .pub file belongs in your GitHub account settings.

---

## GPG Key Setup

GPG is used to cryptographically sign commits and verify authorship.
All commits must be signed.

### Step 1: Generate a GPG Key

```bash
gpg --full-generate-key
```
Recommended options:
- Key type: RSA and RSA
- Key size: 4096
- Email: the same email used for Git commits
- Expiration: optional

### Step 2: Add the GPG Key to GitHub

List your keys and copy the key ID:
```bash
gpg --list-secret-keys --keyid-format=long
```
Export your public key:
```bash
gpg --armor --export YOUR_KEY_ID
```
Then:
1. Open GitHub
2. Go to Settings -> SSH and GPG Keys
3. Click New GPG Key
4. Paste the exported key

### Step 3: Configure Git to Sign Commits

Enable commit signing globally:
```bash
git config --global commit.gpgsign true
git config --global user.signingkey YOUR_KEY_ID
```
### Step 4: Verify Commit Signing

Create a test commit and verify the signature:
```bash
git log --show-signature -1
```
You should see a valid GPG signature.

---

## Common Problems

### Configure Pinentry

GPG uses a helper program called pinentry to request your key's passphrase. 
Some environments require explicit configuration.

You may see errors like:
```bash
gpg: signing failed: Inappropriate ioctl for device
```
Edit (or create):
```
~/.gnupg/gpg-agent.conf
```
Example (macOS):
```
pinentry-program /opt/homebrew/bin/pinentry-mac
```
Example (Linux):
```
pinentry-program /usr/bin/pinentry-gnome3
```
Restart the GPG agent:
```bash
gpgconf --kill gpg-agent
```

#### GPG Client Not found by git

If you see an error message like:
```
gpg: signing failed: No secret key
```
or Git cannot find the GPG client, you may need to explicitly configure which GPG program Git should use.

Set the path to your GPG executable with:
```bash
git config --global gpg.program [PATH_TO_GPG]
```

Example (Linux):
```bash
git config --global gpg.program "/usr/bin/gpg"
```