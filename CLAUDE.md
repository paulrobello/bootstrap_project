# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

Use `make` for all development tasks:

- `make setup` - First-time setup (uv lock + sync)
- `make checkall` - Format, lint, and typecheck (run before commits)
- `make format` - Format code with ruff
- `make lint` - Lint with ruff (auto-fix enabled)
- `make typecheck` - Type check with pyright
- `make pre-commit` - Run pre-commit hooks on all files
- `make app_help` - Show application help
- `make repl` - Start Python REPL in project environment

## Package Management

This project uses `uv` exclusively:
- `uv sync` - Install/update dependencies
- `uv sync -U` - Update all dependencies
- `uv add package` - Add new dependency
- `uv run bootstrap_project` - Run the application from source

## Architecture Overview

**Core Functionality**: Template-based project bootstrapping tool that:
1. Discovers templates from local directories or remote git repositories
2. Clones remote templates with shallow git clone (--depth 1) for efficiency
3. Copies template directories to new project locations
4. Performs intelligent file/folder renaming (template_name → project_name)
5. Updates content across multiple file types (Python, Markdown, TOML, YAML)
6. Installs package bundles with dependency resolution
7. Initializes git repository and runs dependency sync
8. Manages temporary directories for remote template cleanup

**Key Components**:
- `__main__.py`: Single-command Typer CLI with create_project() as main entry point
- Template discovery logic supports both local paths and remote git URLs
  - Local: searches standard repo locations (`~/Repos`, `D:\Repos`, etc.)
  - Remote: validates and clones from GitHub, GitLab, Bitbucket, and generic HTTPS git URLs
- Git URL validation with pattern matching for common git hosting services
- Temporary directory management for remote template cleanup
- File replacement engine with comprehensive case variant support (snake_case, Title Case, kebab-case, PascalCase)
- Package installation system with dependency resolution (base, cli, textual, par-ai-core)
- Progress tracking and rich console output for user feedback

**File Processing Pattern**:
- Uses `shutil.copytree()` with custom ignore function (excludes .git, .venv, .idea, .ruff_cache)
- Multi-variant string replacement across all case styles
- Configurable file patterns via `DEFAULT_FILE_PATTERNS` and `BOOTSTRAP_FILE_PATTERNS` env var
- Targets: pyproject.toml, README.md, Makefile, CLAUDE.md, Python source files, GitHub workflows

**CLI Design**: Follows Typer best practices with Annotated types for all options, Rich console output, progress tracking, and comprehensive error handling.

## Code Style Configuration

- **Line length**: 120 characters
- **Python target**: 3.12 (ruff config) / 3.11 (project requirement)
- **Import style**: Combined as-imports with isort
- **Quote style**: Double quotes
- **Type checking**: Basic mode with pyright, src/ directory structure

## Template Integration

This bootstrap tool is designed to work seamlessly with multiple template repositories:

### new_cli_project_template

The **new_cli_project_template** repository serves as the primary template for creating modern Python CLI projects with AI integration.

#### CLI Template Features

The `new_cli_project_template` provides:
- **Modern Python project structure** with `src/` layout
- **Multi-command CLI** built with Typer and Rich
- **AI integration** via PAR AI Core library
- **Configuration management** with TOML files and environment variables
- **Development tooling** (ruff, pyright, pre-commit, uv)
- **GitHub workflows** for CI/CD (disabled by default as `.github-disabled/`)

### new_tui_project_template

The **new_tui_project_template** repository serves as the template for creating modern Python Terminal User Interface (TUI) applications.

#### TUI Template Features

The `new_tui_project_template` provides:
- **Modern Python project structure** with `src/` layout
- **TUI application** built with Textual framework
- **Rich terminal output** and styling capabilities
- **Configuration management** with TOML files
- **CSS styling** for terminal interfaces
- **Development tooling** (ruff, pyright, pre-commit, uv)
- **Textual development tools** integration (console, dev mode, debugging)

### File Replacement Compatibility

The bootstrap tool is specifically configured to handle all files in both template repositories:

**Core Files Updated**:
- `pyproject.toml` - Project metadata, dependencies, and build configuration
- `README.md` - Documentation with project-specific examples
- `CLAUDE.md` - Development instructions and architecture notes
- `Makefile` - Build commands and development shortcuts
- `.env` and `.env.example` - Environment configuration templates

**Python Source Files (CLI Template)**:
- `src/new_cli_project_template/__init__.py` - Package metadata and version info
- `src/new_cli_project_template/__main__.py` - CLI application entry point with AI commands
- `src/new_cli_project_template/ai_utils.py` - AI utility functions and examples
- `src/new_cli_project_template/config.py` - Configuration management system
- `src/new_cli_project_template/logging_config.py` - Logging setup with Rich integration

**Python Source Files (TUI Template)**:
- `src/new_tui_project_template/__init__.py` - Package metadata and version info
- `src/new_tui_project_template/__main__.py` - CLI entry point for TUI application
- `src/new_tui_project_template/app.py` - Main TUI application class using Textual
- `src/new_tui_project_template/app.tcss` - CSS styling for TUI components
- `src/new_tui_project_template/logging_config.py` - Logging setup with Rich integration

**Development Files**:
- `.github-disabled/workflows/*.yml` - CI/CD pipeline definitions
- `demo.tape` - VHS demo recording configuration

### Usage Examples

```bash
# Create CLI project from default template
bsp -n my_ai_tool -p par-ai-core

# Create TUI project from TUI template
bsp -n my_tui_app -t new_tui_project_template -p textual

# Create from remote GitHub template
bsp -n my_project -t https://github.com/username/template-repo

# Create from remote GitLab template with packages
bsp -n my_tui_app -t https://gitlab.com/user/template.git -p textual

# Preview remote template without creating project
bsp -n test_project -t https://github.com/user/template --preview

# Create with multiple package bundles
bsp -n my_project -p cli -p textual -p par-ai-core

# Create TUI project with custom packages
bsp -n my_dashboard -t new_tui_project_template -p textual
```

### Template Customization Points

When working on template repositories, key areas to maintain compatibility:

#### For new_cli_project_template:
1. **Consistent naming**: Use `new_cli_project_template` throughout all files and source code
2. **Package structure**: Maintain `src/new_cli_project_template/` layout (gets renamed during bootstrap)
3. **AI integration**: Keep PAR AI Core integration and configuration
4. **Placeholder text**: Use `"new_cli_project_template"` and `"New Cli Project Template"` as placeholders

#### For new_tui_project_template:
1. **Consistent naming**: Use `new_tui_project_template` throughout all files and source code
2. **Package structure**: Maintain `src/new_tui_project_template/` layout (gets renamed during bootstrap)
3. **TUI focus**: Keep Textual framework integration and CSS styling
4. **Placeholder text**: Use `"new_tui_project_template"` and `"New Tui Project Template"` as placeholders
5. **No AI dependencies**: Avoid AI-related packages or configuration

#### Common for both templates:
- **Case variants**: Use project name in multiple formats (snake_case, Title Case, etc.) for comprehensive replacement
- **Configuration management**: TOML-based settings with environment variable support
- **Development tooling**: Consistent ruff, pyright, pre-commit setup

### Environment Variables for Template Location

- `BOOTSTRAP_REPO_DIR`: Override default repo search path
- `BOOTSTRAP_REPO_PATHS`: Comma-separated list of search paths
- `BOOTSTRAP_FILE_PATTERNS`: Additional files to process beyond defaults

## Pre-commit Hooks

Configured to run format, lint, and typecheck via Make targets. Uses local hooks to ensure consistency with development workflow.