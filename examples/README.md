# Template Metadata Examples

This directory contains example YAML metadata files that demonstrate different ways to customize project creation with the Bootstrap Project tool.

## Available Examples

### 1. `ai_project_metadata.yaml` - Comprehensive AI Project

A full-featured AI application setup with:
- **AI Integration**: PAR AI Core, Pydantic AI, HTTPX
- **Dual Interface**: CLI and TUI support via Textual
- **Rich Documentation**: Detailed README with badges and features
- **Environment Setup**: API keys and configuration variables
- **Professional Structure**: Comprehensive pyproject.toml classifiers

**Usage:**
```bash
bsp -n my_ai_app -m examples/ai_project_metadata.yaml
```

**Best for**: AI/ML projects, chatbots, data processing applications

### 2. `simple_metadata.yaml` - Minimal CLI Application

A straightforward CLI application with:
- **Basic Setup**: CLI package bundle only
- **Simple Documentation**: Clean, minimal README
- **Author Information**: Basic project metadata
- **Quick Start**: Essential configuration only

**Usage:**
```bash
bsp -n my_cli_tool -m examples/simple_metadata.yaml
```

**Best for**: Command-line utilities, scripts, simple automation tools

### 3. `tui_app_metadata.yaml` - Terminal User Interface

A Textual-based TUI application featuring:
- **Textual Framework**: Full TUI development stack
- **Terminal Focus**: Specialized for console applications
- **Keyboard Navigation**: Documentation for TUI interactions
- **Custom Styling**: Support for CSS theming
- **Apache License**: Alternative licensing example

**Usage:**
```bash
bsp -n my_tui_app -m examples/tui_app_metadata.yaml
```

**Best for**: Interactive terminal applications, dashboards, console games

## Metadata File Structure

All examples follow this general structure:

```yaml
# Project metadata (pyproject.toml)
project:
  description: "Project description"
  keywords: ["keyword1", "keyword2"]
  homepage: "https://github.com/user/project"
  repository: "https://github.com/user/project"
  license: "MIT"

# Author information
author:
  name: "Author Name"
  email: "email@example.com"
  github_username: "username"

# Package requirements
packages:
  - "package-name"  # Predefined bundles or custom packages

# README customization
readme:
  title: "Project Title"
  subtitle: "Project subtitle"
  description: |
    Multi-line description with
    formatting and examples
  badges:
    - name: "Badge Name"
      url: "https://img.shields.io/badge/..."
      link: "https://link-target.com"

# Additional configurations...
```

## Customizing Examples

You can modify these examples or create your own by:

1. **Copying an example**: Start with the closest match to your project type
2. **Updating project info**: Change name, description, URLs, and keywords
3. **Modifying packages**: Add or remove package dependencies
4. **Customizing README**: Adjust title, description, and badges
5. **Adding environment vars**: Include API keys or configuration settings

## Advanced Usage

### Combining with CLI Options

```bash
# Use metadata but override with additional packages
bsp -n my_project -m examples/simple_metadata.yaml -p textual

# Use metadata with remote templates
bsp -n my_project -t https://github.com/user/template -m examples/ai_project_metadata.yaml
```

### Creating Custom Metadata

```bash
# Copy and modify an example
cp examples/simple_metadata.yaml my_custom_metadata.yaml

# Edit with your preferred editor
nano my_custom_metadata.yaml

# Use your custom metadata
bsp -n my_project -m my_custom_metadata.yaml
```

## Tips

- **Start Simple**: Begin with `simple_metadata.yaml` and add complexity as needed
- **Badge Generation**: Use [shields.io](https://shields.io) for generating badge URLs
- **Package Discovery**: Use `bsp --list-packages` to see available predefined bundles
- **Preview First**: Always test with `--preview` flag before creating projects
- **Version Control**: Keep your metadata files in version control for team consistency

## Contributing

If you create useful metadata examples, consider contributing them back to the project!