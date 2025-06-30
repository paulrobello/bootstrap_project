# Bootstrap Project

A powerful CLI tool for quickly bootstrapping new Python projects from templates with intelligent file renaming and package management.

## Features

- **Template-based Project Creation**: Copy and customize project templates from local directories or remote git repositories
- **Remote Template Support**: Clone templates directly from GitHub, GitLab, Bitbucket, or any public HTTPS git repository
- **Metadata-Driven Customization**: Use YAML metadata files to customize project details, author info, packages, and documentation
- **Intelligent Renaming**: Automatically renames files and updates content (snake_case, Title Case, kebab-case, PascalCase)
- **Package Management**: Install predefined package bundles (base, cli, textual, par-ai-core) plus custom packages
- **Auto-Generated Documentation**: Create rich README files with badges, descriptions, and usage examples
- **Git Integration**: Automatically initializes git repository
- **Flexible Configuration**: Environment variables and command-line options
- **Cross-platform**: Works on Windows, macOS, and Linux

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installing uv

#### Linux and Mac
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation

### From PyPI

```bash
uv tool install bootstrap_project
```

or

```bash
pipx install bootstrap_project
```

### From Source

```bash
git clone https://github.com/paulrobello/bootstrap_project.git
cd bootstrap_project
uv sync
```

## Usage

### Basic Usage

Create a new project from the default template:

```bash
# If installed from PyPI
bsp --project-name my_awesome_project

# If running from source
uv run bootstrap_project --project-name my_awesome_project
```

### Using a Custom Local Template

```bash
bsp --project-name my_project --template-name custom_template
```

### Using a Remote Template

Clone and use templates directly from git repositories:

```bash
# From GitHub
bsp -n my_project -t https://github.com/username/my-template

# From GitLab
bsp -n my_project -t https://gitlab.com/username/my-template.git

# From any HTTPS git repository
bsp -n my_project -t https://git.example.com/templates/python-base
```

### Installing Package Bundles

```bash
# Install with textual package bundle
bsp -n my_tui_app -p textual

# Install multiple package bundles
bsp -n my_app -p cli -p textual

# List available packages
bsp --list-packages
```

### Using Template Metadata

Customize your project with a YAML metadata file:

```bash
# Create project with metadata customization
bsp -n my_ai_app --metadata examples/ai_project_metadata.yaml

# Combine metadata with additional packages
bsp -n my_project -m examples/simple_metadata.yaml -p par-ai-core

# Preview metadata-driven project creation
bsp -n my_project -m examples/tui_app_metadata.yaml --preview
```

### Preview Mode

See what would happen without making changes:

```bash
bsp -n my_project --preview
```

## Available Package Bundles

- **base**: Core packages (python-dotenv, pydantic, rich, requests) - always included
- **cli**: CLI development (prompt-toolkit, typer, clipman)
- **textual**: TUI development (textual, textual-dev, clipman)
- **par-ai-core**: AI integration tools

## Template Metadata

Template metadata files allow you to customize project creation with YAML configuration. This enables standardized project setups with predefined author information, package requirements, and documentation.

### Metadata File Structure

```yaml
# Project information (used in pyproject.toml and README)
project:
  description: "Your project description"
  keywords: ["python", "cli", "ai"]
  homepage: "https://github.com/username/project"
  repository: "https://github.com/username/project"
  license: "MIT"

# Author information (used in pyproject.toml)
author:
  name: "Your Name"
  email: "your.email@example.com"
  github_username: "your-username"

# Required packages (automatically installed)
packages:
  - "par-ai-core"  # Predefined bundle
  - "httpx"        # Custom package

# README customization
readme:
  title: "My Amazing Project"
  subtitle: "Building the future with Python"
  description: |
    Detailed project description with features,
    installation instructions, and usage examples.
  badges:
    - name: "Python"
      url: "https://img.shields.io/badge/python-3.11+-blue.svg"
      link: "https://www.python.org/downloads/"

# pyproject.toml enhancements
pyproject:
  classifiers:
    - "Development Status :: 4 - Beta"
    - "Topic :: Scientific/Engineering :: Artificial Intelligence"

# Environment variables for .env file
environment:
  LOG_LEVEL: "INFO"
  API_TIMEOUT: "30"

# Additional files to process
additional_files:
  - "config/settings.yaml"
  - "docs/*.md"
```

### Example Metadata Files

The `examples/` directory contains several metadata templates:

- **`ai_project_metadata.yaml`**: Comprehensive AI project with LLM integration, TUI, and extensive documentation
- **`simple_metadata.yaml`**: Minimal CLI application setup
- **`tui_app_metadata.yaml`**: Textual-based terminal interface application

### Metadata Features

- **Author Information**: Automatically populates pyproject.toml with author and maintainer details
- **Package Management**: Installs both predefined bundles and custom packages from metadata
- **README Generation**: Creates rich documentation with badges, descriptions, and usage examples
- **Environment Setup**: Adds configuration variables to .env files
- **Custom File Processing**: Extends template processing to additional files
- **URL Management**: Sets up project homepage, repository, and documentation links

## How It Works

1. **Template Discovery**: 
   - **Local Templates**: Searches for templates in:
     - `~/Repos/`
     - Environment variable `BOOTSTRAP_REPO_DIR`
     - Custom paths via `BOOTSTRAP_REPO_PATHS`
   - **Remote Templates**: Clones from public HTTPS git repositories:
     - GitHub: `https://github.com/user/repo`
     - GitLab: `https://gitlab.com/user/repo`
     - Bitbucket: `https://bitbucket.org/user/repo`
     - Generic HTTPS git URLs

2. **Project Creation**:
   - Copies template to new location
   - Renames `src/template_name/` to `src/project_name/`
   - Updates project name in all relevant files
   - Runs `uv sync` to install dependencies
   - Initializes git repository

3. **File Updates**: Automatically updates project names in:
   - `.env`
   - `README.md`
   - `Makefile`
   - `pyproject.toml`
   - `CLAUDE.md`
   - Python source files
   - GitHub workflow files
   - Additional files specified via `BOOTSTRAP_FILE_PATTERNS`

## Working with Project Templates

This tool is designed to work seamlessly with multiple project templates:

### new_cli_project_template

The [new_cli_project_template](https://github.com/paulrobello/new_cli_project_template) provides:

- Modern Python project structure with `src/` layout
- Multi-command CLI with Typer
- AI integration via PAR AI Core
- Configuration management with TOML
- Rich terminal output
- Comprehensive development tooling (ruff, pyright, pre-commit)

### new_tui_project_template

The [new_tui_project_template](https://github.com/paulrobello/new_tui_project_template) provides:

- Modern Python project structure with `src/` layout
- Terminal User Interface with Textual framework
- CSS styling for terminal interfaces
- Configuration management with TOML
- Rich terminal output and widgets
- TUI development tools and debugging

## Environment Variables

- `BOOTSTRAP_REPO_DIR`: Primary directory to search for templates
- `BOOTSTRAP_REPO_PATHS`: Comma-separated list of directories to search
- `BOOTSTRAP_FILE_PATTERNS`: Comma-separated list of additional files to update

## Examples

### Create an AI-powered CLI tool
```bash
bsp -n my_ai_cli -p par-ai-core
```

### Create a TUI application
```bash
# Create from TUI template
bsp -n my_tui_app -t new_tui_project_template

# Create TUI app with textual package bundle
bsp -n my_dashboard -t new_tui_project_template -p textual
```

### Create projects with metadata customization
```bash
# AI project with comprehensive setup
bsp -n my_ai_project -m examples/ai_project_metadata.yaml

# Simple CLI with basic metadata
bsp -n my_cli_tool -m examples/simple_metadata.yaml

# TUI application with terminal interface focus
bsp -n my_tui_app -m examples/tui_app_metadata.yaml
```

### Use a custom local template location
```bash
export BOOTSTRAP_REPO_DIR=/my/templates
bsp -n my_project -t my_custom_template
```

### Use a remote template from GitHub
```bash
bsp -n my_awesome_app -t https://github.com/paulrobello/new_cli_project_template
```

### Combine remote templates with metadata
```bash
# Use remote template with local metadata customization
bsp -n my_project \
    -t https://github.com/user/python-template \
    -m examples/ai_project_metadata.yaml
```

### Preview what a remote template would create
```bash
bsp -n test_project -t https://github.com/user/template --preview

# Preview with metadata
bsp -n test_project -m examples/tui_app_metadata.yaml --preview
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Paul Robello - probello@gmail.com