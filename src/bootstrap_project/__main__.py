"""Bootstrap Project"""

import os
import shutil
import subprocess
import tempfile
import urllib.parse
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Annotated, Any

import typer
import yaml
from pathlib import Path

from rich.console import Console
from rich.progress import track

from . import __version__, __application_title__

console = Console()
app = typer.Typer()


@dataclass
class AuthorInfo:
    """Author information for template metadata."""

    name: str = ""
    email: str = ""
    github_username: str = ""


@dataclass
class ProjectInfo:
    """Project information for template metadata."""

    description: str = ""
    keywords: list[str] = field(default_factory=list)
    homepage: str = ""
    repository: str = ""
    documentation: str = ""
    issues: str = ""
    license: str = "MIT"


@dataclass
class ReadmeBadge:
    """README badge configuration."""

    name: str
    url: str
    link: str = ""


@dataclass
class ReadmeInfo:
    """README customization information."""

    title: str = ""
    subtitle: str = ""
    description: str = ""
    badges: list[ReadmeBadge] = field(default_factory=list)


@dataclass
class TemplateMetadata:
    """Complete template metadata structure."""

    project: ProjectInfo = field(default_factory=ProjectInfo)
    author: AuthorInfo = field(default_factory=AuthorInfo)
    maintainer: AuthorInfo | None = None
    packages: list[str] = field(default_factory=list)
    readme: ReadmeInfo = field(default_factory=ReadmeInfo)
    pyproject_classifiers: list[str] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    additional_files: list[str] = field(default_factory=list)


class FeatureNames(StrEnum):
    """Enum for feature names."""

    BASE = "base"
    CLI = "cli"
    TEXTUAL = "textual"
    PARAI = "par-ai-core"


available_features: dict[FeatureNames, list[str]] = {
    FeatureNames.BASE: ["python-dotenv", "asyncio", "pydantic-core", "pydantic", "orjson", "rich", "requests"],
    FeatureNames.CLI: ["prompt-toolkit", "typer", "clipman"],
    FeatureNames.TEXTUAL: ["textual", "textual-dev", "clipman"],
    FeatureNames.PARAI: ["par-ai-core"],
}

feature_deps: dict[FeatureNames, list[FeatureNames]] = {
    FeatureNames.CLI: [FeatureNames.BASE],
    FeatureNames.TEXTUAL: [FeatureNames.BASE, FeatureNames.CLI],
    FeatureNames.PARAI: [FeatureNames.BASE],
}

# Default file patterns for template replacement
DEFAULT_FILE_PATTERNS = [
    ".env",
    "README.md",
    "Makefile",
    "pyproject.toml",
    "demo.tape",
    "CLAUDE.md",
    "src/{project_name}/__init__.py",
    "src/{project_name}/__main__.py",
    "src/{project_name}/ai_utils.py",
    "src/{project_name}/config.py",
    "src/{project_name}/logging_config.py",
    ".github-disabled/workflows/build.yml",
    ".github-disabled/workflows/publish.yml",
    ".github-disabled/workflows/publish-dev.yml",
    ".github-disabled/workflows/release.yml",
]

# Default repository search paths
DEFAULT_REPO_PATHS = [
    "~/Repos",
    "d:\\Repos",
    "c:\\Repos",
    "Repos",
]


def load_metadata_from_yaml(metadata_file: Path) -> TemplateMetadata:
    """Load template metadata from YAML file."""
    if not metadata_file.exists():
        console.print(f"[red]✗ Metadata file not found:[/red] {metadata_file}")
        console.print(f"[dim]Expected file at: {metadata_file.absolute()}[/dim]")
        raise typer.Exit(1)

    if not metadata_file.is_file():
        console.print(f"[red]✗ Path is not a file:[/red] {metadata_file}")
        raise typer.Exit(1)

    try:
        with open(metadata_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            console.print(f"[yellow]⚠ Metadata file is empty:[/yellow] {metadata_file}")
            data = {}

        if not isinstance(data, dict):
            console.print(f"[red]✗ Invalid metadata format:[/red] Expected YAML object, got {type(data).__name__}")
            raise typer.Exit(1)

        metadata = TemplateMetadata()

        # Parse project info with validation
        if "project" in data:
            if not isinstance(data["project"], dict):
                console.print("[red]✗ Invalid project section:[/red] Expected object")
                raise typer.Exit(1)

            project_data = data["project"]
            metadata.project = ProjectInfo(
                description=project_data.get("description", ""),
                keywords=project_data.get("keywords", []) if isinstance(project_data.get("keywords"), list) else [],
                homepage=project_data.get("homepage", ""),
                repository=project_data.get("repository", ""),
                documentation=project_data.get("documentation", ""),
                issues=project_data.get("issues", ""),
                license=project_data.get("license", "MIT"),
            )

        # Parse author info with validation
        if "author" in data:
            if not isinstance(data["author"], dict):
                console.print("[red]✗ Invalid author section:[/red] Expected object")
                raise typer.Exit(1)

            author_data = data["author"]
            metadata.author = AuthorInfo(
                name=author_data.get("name", ""),
                email=author_data.get("email", ""),
                github_username=author_data.get("github_username", ""),
            )

        # Parse maintainer info (optional, defaults to author)
        if "maintainer" in data:
            if not isinstance(data["maintainer"], dict):
                console.print("[red]✗ Invalid maintainer section:[/red] Expected object")
                raise typer.Exit(1)

            maintainer_data = data["maintainer"]
            metadata.maintainer = AuthorInfo(
                name=maintainer_data.get("name", ""),
                email=maintainer_data.get("email", ""),
                github_username=maintainer_data.get("github_username", ""),
            )

        # Parse packages with validation
        packages = data.get("packages", [])
        if not isinstance(packages, list):
            console.print("[red]✗ Invalid packages section:[/red] Expected list")
            raise typer.Exit(1)
        metadata.packages = packages

        # Parse README info with validation
        if "readme" in data:
            if not isinstance(data["readme"], dict):
                console.print("[red]✗ Invalid readme section:[/red] Expected object")
                raise typer.Exit(1)

            readme_data = data["readme"]
            badges = []
            if "badges" in readme_data:
                if not isinstance(readme_data["badges"], list):
                    console.print("[red]✗ Invalid badges section:[/red] Expected list")
                    raise typer.Exit(1)

                for i, badge_data in enumerate(readme_data["badges"]):
                    if not isinstance(badge_data, dict):
                        console.print(f"[red]✗ Invalid badge {i}:[/red] Expected object")
                        raise typer.Exit(1)

                    if "name" not in badge_data or "url" not in badge_data:
                        console.print(f"[red]✗ Badge {i} missing required fields:[/red] name and url are required")
                        raise typer.Exit(1)

                    badges.append(
                        ReadmeBadge(
                            name=badge_data["name"],
                            url=badge_data["url"],
                            link=badge_data.get("link", ""),
                        )
                    )

            metadata.readme = ReadmeInfo(
                title=readme_data.get("title", ""),
                subtitle=readme_data.get("subtitle", ""),
                description=readme_data.get("description", ""),
                badges=badges,
            )

        # Parse pyproject classifiers with validation
        if "pyproject" in data:
            if not isinstance(data["pyproject"], dict):
                console.print("[red]✗ Invalid pyproject section:[/red] Expected object")
                raise typer.Exit(1)

            if "classifiers" in data["pyproject"]:
                classifiers = data["pyproject"]["classifiers"]
                if not isinstance(classifiers, list):
                    console.print("[red]✗ Invalid classifiers section:[/red] Expected list")
                    raise typer.Exit(1)
                metadata.pyproject_classifiers = classifiers

        # Parse environment variables with validation
        environment = data.get("environment", {})
        if not isinstance(environment, dict):
            console.print("[red]✗ Invalid environment section:[/red] Expected object")
            raise typer.Exit(1)
        metadata.environment = environment

        # Parse additional files with validation
        additional_files = data.get("additional_files", [])
        if not isinstance(additional_files, list):
            console.print("[red]✗ Invalid additional_files section:[/red] Expected list")
            raise typer.Exit(1)
        metadata.additional_files = additional_files

        return metadata

    except yaml.YAMLError as e:
        console.print("[red]✗ Invalid YAML syntax in metadata file:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        console.print(f"[dim]File: {metadata_file}[/dim]")
        raise typer.Exit(1)
    except (OSError, UnicodeDecodeError) as e:
        console.print(f"[red]✗ Cannot read metadata file:[/red] {metadata_file}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error parsing metadata file:[/red] {metadata_file}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def transform_case_variants(text: str) -> dict[str, str]:
    """Generate case variants for text replacement."""
    return {
        "snake_case": text,
        "title_case": text.replace("_", " ").title(),
        "kebab_case": text.replace("_", "-"),
        "pascal_case": "".join(word.capitalize() for word in text.split("_")),
    }


def replace_in_file(file_path: Path, replacements: dict[str, str]) -> None:
    """Replaces multiple string patterns in a single pass through the file."""
    if not file_path.exists():
        console.print(f"[yellow]⚠ File not found, skipping:[/yellow] {file_path}")
        return

    if not file_path.is_file():
        console.print(f"[yellow]⚠ Path is not a file, skipping:[/yellow] {file_path}")
        return

    try:
        content = file_path.read_text(encoding="utf-8")
        updated_content = content

        for old, new in replacements.items():
            if old in updated_content:
                updated_content = updated_content.replace(old, new)

        # Only write if content changed
        if updated_content != content:
            file_path.write_text(updated_content, encoding="utf-8")

    except PermissionError:
        console.print(f"[red]✗ Permission denied:[/red] Cannot write to {file_path}")
        console.print("[dim]Check file permissions and try again[/dim]")
        raise typer.Exit(1)
    except UnicodeDecodeError as e:
        console.print(f"[red]✗ Encoding error in file:[/red] {file_path}")
        console.print(f"[red]Error:[/red] {e}")
        console.print("[dim]File may contain non-UTF-8 characters[/dim]")
        raise typer.Exit(1)
    except OSError as e:
        console.print(f"[red]✗ I/O error updating file:[/red] {file_path}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error updating file:[/red] {file_path}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def ignore_dirs(src, names) -> list[str]:
    """Function to ignore specified directories."""
    # typer.echo(f"Ignoring {names} in {src}")
    return [name for name in names if name in [".git", ".venv", "uv.lock", ".idea", ".ruff_cache"]]


def copy_template(template_dir: Path, project_location: Path) -> None:
    """Recursively copy the template directory to the project location."""
    if not template_dir.exists():
        console.print(f"[red]✗ Template directory does not exist:[/red] {template_dir}")
        raise typer.Exit(1)

    if not template_dir.is_dir():
        console.print(f"[red]✗ Template path is not a directory:[/red] {template_dir}")
        raise typer.Exit(1)

    if project_location.exists() and not project_location.is_dir():
        console.print(f"[red]✗ Project location exists but is not a directory:[/red] {project_location}")
        raise typer.Exit(1)

    try:
        shutil.copytree(template_dir, project_location, dirs_exist_ok=True, ignore=ignore_dirs)
        console.print("[green]✓ Template copied successfully[/green]")

    except PermissionError:
        console.print(f"[red]✗ Permission denied:[/red] Cannot copy to {project_location}")
        console.print("[dim]Check directory permissions and try again[/dim]")
        raise typer.Exit(1)
    except shutil.Error as e:
        console.print("[red]✗ Copy operation failed:[/red]")
        for error in e.args[0] if hasattr(e, "args") and e.args else [str(e)]:
            if isinstance(error, tuple) and len(error) >= 3:
                src, dst, msg = error[:3]
                console.print(f"[red]  • {msg}:[/red] {src} → {dst}")
            else:
                console.print(f"[red]  • {error}[/red]")
        raise typer.Exit(1)
    except OSError as e:
        console.print("[red]✗ I/O error during template copy:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        if e.errno:
            console.print(f"[dim]Error code: {e.errno}[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print("[red]✗ Unexpected error copying template:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def rename_src_folder(project_location: Path, template_name: str, project_name: str) -> None:
    """Rename src/template to src/project_name."""
    template_src = project_location / "src" / template_name
    new_src = project_location / "src" / project_name

    if not template_src.exists():
        console.print(f"[red]✗ Template src directory not found:[/red] {template_src}")
        console.print(f"[dim]Expected to find: {template_src.absolute()}[/dim]")

        # Try to provide helpful suggestions
        src_dir = project_location / "src"
        if src_dir.exists():
            existing_dirs = [d.name for d in src_dir.iterdir() if d.is_dir()]
            if existing_dirs:
                console.print(f"[dim]Available directories in src/: {', '.join(existing_dirs)}[/dim]")

        raise typer.Exit(1)

    if not template_src.is_dir():
        console.print(f"[red]✗ Template src path is not a directory:[/red] {template_src}")
        raise typer.Exit(1)

    if new_src.exists():
        console.print(f"[red]✗ Target directory already exists:[/red] {new_src}")
        console.print("[dim]Cannot rename to existing directory[/dim]")
        raise typer.Exit(1)

    try:
        template_src.rename(new_src)
        console.print(f"[green]✓ Renamed src directory:[/green] {template_name} → {project_name}")

    except PermissionError:
        console.print(f"[red]✗ Permission denied:[/red] Cannot rename {template_src}")
        console.print("[dim]Check directory permissions and try again[/dim]")
        raise typer.Exit(1)
    except OSError as e:
        console.print("[red]✗ Error renaming src folder:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        console.print(f"[dim]From: {template_src}[/dim]")
        console.print(f"[dim]To: {new_src}[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print("[red]✗ Unexpected error renaming src folder:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def get_file_patterns() -> list[str]:
    """Get file patterns from environment or use defaults."""
    env_patterns = os.environ.get("BOOTSTRAP_FILE_PATTERNS")
    if env_patterns:
        return env_patterns.split(",")
    return DEFAULT_FILE_PATTERNS


def generate_readme_content(metadata: TemplateMetadata, project_name: str) -> str:
    """Generate README content based on metadata."""
    if not metadata.readme.title and not metadata.readme.description:
        return ""  # Return empty to skip replacement

    content = []

    # Title
    title = metadata.readme.title or project_name.replace("_", " ").title()
    content.append(f"# {title}")

    # Subtitle
    if metadata.readme.subtitle:
        content.append(f"\n{metadata.readme.subtitle}")

    # Badges
    if metadata.readme.badges:
        content.append("\n")
        for badge in metadata.readme.badges:
            if badge.link:
                content.append(f"[![{badge.name}]({badge.url})]({badge.link})")
            else:
                content.append(f"![{badge.name}]({badge.url})")
        content.append("")

    # Description
    if metadata.readme.description:
        content.append(f"\n{metadata.readme.description}")

    return "\n".join(content)


def generate_pyproject_author_section(metadata: TemplateMetadata) -> dict[str, Any]:
    """Generate pyproject.toml author section based on metadata."""
    author_info = {}

    if metadata.author.name or metadata.author.email:
        authors = []
        maintainers = []

        if metadata.author.name and metadata.author.email:
            authors.append({"name": metadata.author.name, "email": metadata.author.email})

        # Use maintainer info if provided, otherwise use author info
        maintainer = metadata.maintainer or metadata.author
        if maintainer.name and maintainer.email:
            maintainers.append({"name": maintainer.name, "email": maintainer.email})

        if authors:
            author_info["authors"] = authors
        if maintainers:
            author_info["maintainers"] = maintainers

    return author_info


def update_files(
    project_location: Path, template_name: str, project_name: str, metadata: TemplateMetadata | None = None
) -> None:
    """Replace all instances of template_name with project_name in specific files."""
    file_patterns = get_file_patterns()
    template_variants = transform_case_variants(template_name)
    project_variants = transform_case_variants(project_name)

    # Create replacement mapping for all case variants
    replacements = {template_variants[variant]: project_variants[variant] for variant in template_variants}

    # Add metadata-specific replacements if metadata is provided
    if metadata:
        # Add project description
        if metadata.project.description:
            replacements["TEMPLATE_DESCRIPTION"] = metadata.project.description

        # Add author name and email placeholders
        if metadata.author.name:
            replacements["TEMPLATE_AUTHOR_NAME"] = metadata.author.name
        if metadata.author.email:
            replacements["TEMPLATE_AUTHOR_EMAIL"] = metadata.author.email

        # Add project URLs
        if metadata.project.homepage:
            replacements["TEMPLATE_HOMEPAGE"] = metadata.project.homepage
        if metadata.project.repository:
            replacements["TEMPLATE_REPOSITORY"] = metadata.project.repository

    # Add additional file patterns from metadata
    additional_patterns = []
    if metadata and metadata.additional_files:
        additional_patterns = [pattern.format(project_name=project_name) for pattern in metadata.additional_files]

    files_to_update = [pattern.format(project_name=project_name) for pattern in file_patterns] + additional_patterns

    for file in track(files_to_update, description="Updating files..."):
        file_path = project_location / file
        if file_path.exists():
            replace_in_file(file_path, replacements)

    # Handle special metadata-driven file updates
    if metadata:
        update_readme_with_metadata(project_location, metadata, project_name)
        update_pyproject_with_metadata(project_location, metadata)
        update_env_with_metadata(project_location, metadata)


def update_readme_with_metadata(project_location: Path, metadata: TemplateMetadata, project_name: str) -> None:
    """Update README.md with metadata-generated content."""
    readme_path = project_location / "README.md"
    if not readme_path.exists():
        console.print("[yellow]⚠ README.md not found, skipping metadata update[/yellow]")
        return

    readme_content = generate_readme_content(metadata, project_name)
    if not readme_content:
        return

    try:
        current_content = readme_path.read_text(encoding="utf-8")

        # Look for a marker to replace content, or prepend to existing content
        if "<!-- METADATA_CONTENT -->" in current_content:
            # Replace marked section
            parts = current_content.split("<!-- METADATA_CONTENT -->")
            if len(parts) >= 2:
                updated_content = f"{readme_content}\n\n{parts[1]}"
                readme_path.write_text(updated_content, encoding="utf-8")
        else:
            # Prepend to existing content
            updated_content = f"{readme_content}\n\n{current_content}"
            readme_path.write_text(updated_content, encoding="utf-8")

        console.print("[green]✓ README.md updated with metadata[/green]")

    except PermissionError:
        console.print("[red]✗ Permission denied:[/red] Cannot write to README.md")
        console.print("[dim]Check file permissions and try again[/dim]")
    except UnicodeDecodeError as e:
        console.print(f"[red]✗ Encoding error in README.md:[/red] {e}")
        console.print("[dim]File may contain non-UTF-8 characters[/dim]")
    except OSError as e:
        console.print(f"[red]✗ I/O error updating README with metadata:[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗ Unexpected error updating README:[/red] {e}")


def update_pyproject_with_metadata(project_location: Path, metadata: TemplateMetadata) -> None:
    """Update pyproject.toml with metadata information."""
    pyproject_path = project_location / "pyproject.toml"
    if not pyproject_path.exists():
        console.print("[yellow]⚠ pyproject.toml not found, skipping metadata update[/yellow]")
        return

    try:
        content = pyproject_path.read_text(encoding="utf-8")
        original_content = content

        # Update description
        if metadata.project.description:
            content = content.replace(
                'description = "TEMPLATE_DESCRIPTION"', f'description = "{metadata.project.description}"'
            )

        # Update keywords
        if metadata.project.keywords:
            keywords_str = '",\n    "'.join(metadata.project.keywords)
            content = content.replace(
                'keywords = [\n    "TEMPLATE_KEYWORDS",\n]', f'keywords = [\n    "{keywords_str}",\n]'
            )

        # Update classifiers
        if metadata.pyproject_classifiers:
            classifiers_str = '",\n    "'.join(metadata.pyproject_classifiers)
            if "TEMPLATE_CLASSIFIERS" in content:
                content = content.replace('"TEMPLATE_CLASSIFIERS",', f'"{classifiers_str}",')

        # Update URLs
        if metadata.project.homepage:
            content = content.replace("TEMPLATE_HOMEPAGE", metadata.project.homepage)
        if metadata.project.repository:
            content = content.replace("TEMPLATE_REPOSITORY", metadata.project.repository)
        if metadata.project.documentation:
            content = content.replace("TEMPLATE_DOCUMENTATION", metadata.project.documentation)
        if metadata.project.issues:
            content = content.replace("TEMPLATE_ISSUES", metadata.project.issues)

        # Only write if content changed
        if content != original_content:
            pyproject_path.write_text(content, encoding="utf-8")
            console.print("[green]✓ pyproject.toml updated with metadata[/green]")

    except PermissionError:
        console.print("[red]✗ Permission denied:[/red] Cannot write to pyproject.toml")
        console.print("[dim]Check file permissions and try again[/dim]")
    except UnicodeDecodeError as e:
        console.print(f"[red]✗ Encoding error in pyproject.toml:[/red] {e}")
        console.print("[dim]File may contain non-UTF-8 characters[/dim]")
    except OSError as e:
        console.print(f"[red]✗ I/O error updating pyproject.toml:[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗ Unexpected error updating pyproject.toml:[/red] {e}")


def update_env_with_metadata(project_location: Path, metadata: TemplateMetadata) -> None:
    """Update .env file with metadata environment variables."""
    if not metadata.environment:
        return

    env_path = project_location / ".env"
    if not env_path.exists():
        console.print("[yellow]⚠ .env file not found, skipping metadata update[/yellow]")
        return

    try:
        content = env_path.read_text(encoding="utf-8")
        original_content = content

        # Add environment variables
        for key, value in metadata.environment.items():
            env_line = f"{key}={value}"
            if f"{key}=" not in content:
                content += f"\n{env_line}"

        # Only write if content changed
        if content != original_content:
            env_path.write_text(content, encoding="utf-8")
            console.print("[green]✓ .env file updated with metadata[/green]")

    except PermissionError:
        console.print("[red]✗ Permission denied:[/red] Cannot write to .env file")
        console.print("[dim]Check file permissions and try again[/dim]")
    except UnicodeDecodeError as e:
        console.print(f"[red]✗ Encoding error in .env file:[/red] {e}")
        console.print("[dim]File may contain non-UTF-8 characters[/dim]")
    except OSError as e:
        console.print(f"[red]✗ I/O error updating .env file:[/red] {e}")
    except Exception as e:
        console.print(f"[red]✗ Unexpected error updating .env file:[/red] {e}")


def resolve_feature_dependencies(requested_features: list[FeatureNames] | None) -> set[FeatureNames]:
    """Resolve feature dependencies and ensure BASE is always included."""
    resolved = {FeatureNames.BASE}  # Always include BASE

    if requested_features is None:
        return resolved

    # Add all requested features
    resolved.update(requested_features)

    # Recursively add dependencies
    to_process = list(requested_features)
    while to_process:
        feature = to_process.pop(0)
        if feature in feature_deps:
            for dep in feature_deps[feature]:
                if dep not in resolved:
                    resolved.add(dep)
                    to_process.append(dep)

    return resolved


def validate_feature_dependencies() -> None:
    """Validate that all feature dependencies are valid."""
    for feature, deps in feature_deps.items():
        if feature not in available_features:
            raise ValueError(f"Feature dependency definition references unknown feature: {feature}")
        for dep in deps:
            if dep not in available_features:
                raise ValueError(f"Feature {feature} has unknown dependency: {dep}")


def run_cli_commands(
    project_location: Path, features: list[FeatureNames] | None, metadata: TemplateMetadata | None = None
) -> None:
    """Run necessary CLI commands."""
    if not project_location.exists():
        console.print(f"[red]✗ Project directory does not exist:[/red] {project_location}")
        raise typer.Exit(1)

    if not project_location.is_dir():
        console.print(f"[red]✗ Project path is not a directory:[/red] {project_location}")
        raise typer.Exit(1)

    # Check for required tools
    required_tools = ["uv", "git"]
    for tool in required_tools:
        if not shutil.which(tool):
            console.print(f"[red]✗ Required tool not found:[/red] {tool}")
            console.print(f"[dim]Please install {tool} and ensure it's in your PATH[/dim]")
            raise typer.Exit(1)

    commands: list[tuple[str, ...]] = [("uv", "sync", "-U")]

    # Collect all features to install
    all_features = list(features) if features else []

    # Add features from metadata
    metadata_features = []
    if metadata and metadata.packages:
        for pkg in metadata.packages:
            # Check if it's a known feature enum
            try:
                enum_feature = FeatureNames(pkg)
                all_features.append(enum_feature)
                metadata_features.append(enum_feature)
            except ValueError:
                # Add as direct package
                metadata_features.append(pkg)

    # Resolve dependencies and ensure BASE is always included
    resolved_features = resolve_feature_dependencies(all_features)

    if resolved_features:
        # Sort features to ensure consistent order (BASE first)
        sorted_features = sorted(resolved_features, key=lambda f: (f != FeatureNames.BASE, f.value))

        # Display what features will be installed
        console.print("\n[bold cyan]Installing features:[/bold cyan]")
        for feature in sorted_features:
            package_list = available_features[feature]
            status = "[green]✓[/green]"
            if feature == FeatureNames.BASE:
                status += " [dim](always included)[/dim]"
            elif features and feature in features:
                status += " [dim](requested)[/dim]"
            elif feature in metadata_features:
                status += " [dim](from metadata)[/dim]"
            else:
                status += " [dim](dependency)[/dim]"
            console.print(f"  {status} [bold]{feature.value}[/bold]: {', '.join(package_list)}")
            commands.append(("uv", "add", *package_list))

    # Add direct packages from metadata (non-feature packages)
    if metadata and metadata.packages:
        direct_packages = []
        for pkg in metadata.packages:
            try:
                FeatureNames(pkg)  # Skip if it's a feature
            except ValueError:
                direct_packages.append(pkg)

        if direct_packages:
            console.print("\n[bold cyan]Installing direct packages from metadata:[/bold cyan]")
            for pkg in direct_packages:
                console.print(f"  [green]✓[/green] [bold]{pkg}[/bold] [dim](from metadata)[/dim]")
            commands.append(tuple(["uv", "add"] + direct_packages))

    commands.append(("git", "init"))

    try:
        for i, cmd in enumerate(track(commands, description="Running setup commands...")):
            timeout = 300 if cmd[0] == "uv" else 30

            try:
                subprocess.run(cmd, cwd=project_location, check=True, capture_output=True, text=True, timeout=timeout)

                # Show success for critical commands
                if cmd[0] == "git" and cmd[1] == "init":
                    console.print("[green]✓ Git repository initialized[/green]")
                elif cmd[0] == "uv" and cmd[1] == "sync":
                    console.print("[green]✓ Dependencies synchronized[/green]")

            except subprocess.CalledProcessError as e:
                console.print(f"\n[red]✗ Command failed:[/red] {' '.join(cmd)}")
                console.print(f"[red]Exit code:[/red] {e.returncode}")

                if e.stderr:
                    console.print("[red]Error output:[/red]")
                    for line in e.stderr.strip().split("\n"):
                        console.print(f"  {line}")

                if e.stdout:
                    console.print("[dim]Standard output:[/dim]")
                    for line in e.stdout.strip().split("\n"):
                        console.print(f"  {line}")

                console.print(f"[dim]Working directory: {project_location}[/dim]")

                # Provide specific help for common errors
                if cmd[0] == "uv":
                    console.print("[dim]Possible solutions:[/dim]")
                    console.print("  • Check if uv is properly installed and up to date")
                    console.print("  • Verify pyproject.toml syntax is correct")
                    console.print("  • Check network connectivity for package downloads")
                elif cmd[0] == "git":
                    console.print("[dim]Possible solutions:[/dim]")
                    console.print("  • Check if directory is already a git repository")
                    console.print("  • Verify write permissions in the directory")

                raise typer.Exit(1)

            except subprocess.TimeoutExpired:
                console.print(f"\n[red]✗ Command timed out:[/red] {' '.join(cmd)}")
                console.print(f"[red]Timeout:[/red] {timeout} seconds")
                console.print(f"[dim]Working directory: {project_location}[/dim]")

                if cmd[0] == "uv":
                    console.print("[dim]Package installation may be taking longer than expected[/dim]")
                    console.print("[dim]Consider checking network connectivity or increasing timeout[/dim]")

                raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Operation cancelled by user[/yellow]")
        raise typer.Exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        console.print("\n[red]✗ Unexpected error during command execution:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def is_git_url(url: str) -> bool:
    """Check if a string is a valid git URL."""
    # Check for common git URL patterns
    git_patterns = [
        r"^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$",
        r"^https://gitlab\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$",
        r"^https://bitbucket\.org/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$",
        r"^https://[\w\-\.]+/[\w\-\./]+(?:\.git)?/?$",  # Generic HTTPS git URL
    ]

    import re

    return any(re.match(pattern, url) for pattern in git_patterns)


def validate_git_url(url: str) -> str:
    """Validate and normalize a git URL."""
    if not url or not url.strip():
        console.print("[red]✗ Empty git URL provided[/red]")
        raise typer.Exit(1)

    url = url.strip()

    if not is_git_url(url):
        console.print(f"[red]✗ Invalid git URL format:[/red] {url}")
        console.print("[dim]Supported formats:[/dim]")
        console.print("  • https://github.com/username/repository")
        console.print("  • https://gitlab.com/username/repository")
        console.print("  • https://bitbucket.org/username/repository")
        console.print("  • https://your-git-server.com/path/repository")
        raise typer.Exit(1)

    try:
        # Normalize URL (ensure it ends with .git if it's a GitHub/GitLab URL)
        parsed = urllib.parse.urlparse(url)

        if not parsed.scheme:
            console.print(f"[red]✗ URL missing scheme (https://):[/red] {url}")
            raise typer.Exit(1)

        if parsed.scheme not in ["https", "http"]:
            console.print(f"[red]✗ Unsupported URL scheme:[/red] {parsed.scheme}")
            console.print("[dim]Only HTTP and HTTPS URLs are supported[/dim]")
            raise typer.Exit(1)

        if not parsed.netloc:
            console.print(f"[red]✗ Invalid URL - missing hostname:[/red] {url}")
            raise typer.Exit(1)

        if parsed.hostname in ["github.com", "gitlab.com", "bitbucket.org"]:
            path = parsed.path.rstrip("/")
            if not path.endswith(".git"):
                path += ".git"
            return f"{parsed.scheme}://{parsed.netloc}{path}"

        return url.rstrip("/")

    except Exception as e:
        console.print(f"[red]✗ Error parsing git URL:[/red] {url}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def clone_remote_template(git_url: str, temp_dir: Path) -> Path:
    """Clone a remote git repository to a temporary directory."""
    console.print(f"[cyan]Cloning remote template from {git_url}...[/cyan]")

    # Check if git is available
    if not shutil.which("git"):
        console.print("[red]✗ Git is not installed or not in PATH[/red]")
        console.print("[dim]Please install Git and try again[/dim]")
        raise typer.Exit(1)

    try:
        # Ensure the temp directory exists
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Clone the repository
        subprocess.run(
            ["git", "clone", "--depth", "1", git_url, str(temp_dir)],
            check=True,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if not temp_dir.exists() or not any(temp_dir.iterdir()):
            console.print(f"[red]✗ Clone completed but directory is empty:[/red] {temp_dir}")
            raise typer.Exit(1)

        console.print("[green]✓ Remote template cloned successfully[/green]")
        return temp_dir

    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗ Failed to clone repository:[/red] {git_url}")
        console.print(f"[red]Exit code:[/red] {e.returncode}")

        if e.stderr:
            console.print("[red]Error output:[/red]")
            for line in e.stderr.strip().split("\n"):
                console.print(f"  {line}")

        # Provide specific help based on common error patterns
        if e.stderr:
            stderr_lower = e.stderr.lower()
            if "authentication failed" in stderr_lower or "permission denied" in stderr_lower:
                console.print("[dim]Possible solutions:[/dim]")
                console.print("  • Check if the repository is public")
                console.print("  • Verify your Git credentials are configured")
                console.print("  • Try using SSH instead of HTTPS URL")
            elif "repository not found" in stderr_lower or "not found" in stderr_lower:
                console.print("[dim]Possible solutions:[/dim]")
                console.print("  • Verify the repository URL is correct")
                console.print("  • Check if the repository exists and is accessible")
            elif "network" in stderr_lower or "connection" in stderr_lower:
                console.print("[dim]Possible solutions:[/dim]")
                console.print("  • Check your internet connection")
                console.print("  • Try again later if the server is temporarily unavailable")

        raise typer.Exit(1)

    except subprocess.TimeoutExpired:
        console.print(f"[red]✗ Git clone timed out:[/red] {git_url}")
        console.print("[red]Timeout:[/red] 300 seconds")
        console.print("[dim]Possible solutions:[/dim]")
        console.print("  • Check your internet connection speed")
        console.print("  • Try cloning a smaller repository or one with better connectivity")
        console.print("  • The repository might be very large")
        raise typer.Exit(1)

    except PermissionError:
        console.print("[red]✗ Permission denied:[/red] Cannot create temporary directory")
        console.print(f"[dim]Location: {temp_dir}[/dim]")
        console.print("[dim]Check file system permissions[/dim]")
        raise typer.Exit(1)

    except Exception as e:
        console.print("[red]✗ Unexpected error during git clone:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        console.print(f"[dim]Repository: {git_url}[/dim]")
        console.print(f"[dim]Target directory: {temp_dir}[/dim]")
        raise typer.Exit(1)


def get_template_directory(template_name: str) -> tuple[Path, bool]:
    """Get template directory, handling both local paths and remote git URLs.

    Returns:
        tuple[Path, bool]: (template_path, is_temporary)
    """
    if not template_name or not template_name.strip():
        console.print("[red]✗ Template name cannot be empty[/red]")
        raise typer.Exit(1)

    template_name = template_name.strip()

    # Check if it's a git URL
    if is_git_url(template_name):
        git_url = validate_git_url(template_name)

        # Create temporary directory for cloning
        try:
            temp_dir = Path(tempfile.mkdtemp(prefix="bootstrap_template_"))
        except (OSError, PermissionError) as e:
            console.print("[red]✗ Cannot create temporary directory for cloning[/red]")
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

        try:
            clone_remote_template(git_url, temp_dir)
            return temp_dir, True
        except Exception:
            # Clean up temp directory on failure
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception as cleanup_error:
                console.print(f"[yellow]⚠ Could not clean up temp directory:[/yellow] {cleanup_error}")
            raise

    # Handle local template
    repo_dir = find_local_repo_directory()
    if repo_dir is None:
        console.print("[red]✗ No repository directory found for local template[/red]")
        console.print("[dim]Configure BOOTSTRAP_REPO_DIR or check default paths[/dim]")
        raise typer.Exit(1)

    template_dir = repo_dir / template_name
    return template_dir, False


def find_local_repo_directory() -> Path | None:
    """Find the repository directory from environment or defaults."""
    # Check environment variable first
    env_repo_dir = os.environ.get("BOOTSTRAP_REPO_DIR")
    if env_repo_dir:
        repo_path = Path(env_repo_dir).expanduser().resolve()
        if repo_path.exists():
            return repo_path

    # Check default paths
    repo_paths = os.environ.get("BOOTSTRAP_REPO_PATHS", ",".join(DEFAULT_REPO_PATHS)).split(",")

    for path_str in repo_paths:
        repo_path = Path(path_str.strip()).expanduser().resolve()
        if repo_path.exists():
            return repo_path

    return None


def validate_project_setup(template_dir: Path, project_location: Path, is_remote: bool = False) -> bool:
    """Validate project setup parameters."""
    if not template_dir.exists():
        template_type = "Remote template" if is_remote else "Template directory"
        console.print(f"[red]✗ {template_type} not found:[/red] {template_dir}")
        console.print(f"[dim]Expected location: {template_dir.absolute()}[/dim]")

        if not is_remote:
            # For local templates, suggest available templates
            repo_dir = find_local_repo_directory()
            if repo_dir and repo_dir.exists():
                available = [d.name for d in repo_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
                if available:
                    console.print(f"[dim]Available templates in {repo_dir}:[/dim]")
                    for template in sorted(available)[:5]:  # Show first 5
                        console.print(f"  • {template}")
                    if len(available) > 5:
                        console.print(f"  ... and {len(available) - 5} more")

        raise typer.Exit(1)

    if not template_dir.is_dir():
        console.print(f"[red]✗ Template path is not a directory:[/red] {template_dir}")
        raise typer.Exit(1)

    if not is_remote and template_dir.resolve() == project_location.resolve():
        console.print("[red]✗ Template and project directories cannot be the same[/red]")
        console.print(f"[dim]Path: {template_dir.resolve()}[/dim]")
        raise typer.Exit(1)

    if project_location.exists():
        if project_location.is_file():
            console.print(f"[red]✗ Project location exists as a file:[/red] {project_location}")
            console.print("[dim]Cannot create directory at this location[/dim]")
            raise typer.Exit(1)

        if project_location.is_dir() and any(project_location.iterdir()):
            console.print(f"[yellow]⚠ Project directory already exists and is not empty:[/yellow] {project_location}")
            console.print("[dim]Existing files may be overwritten[/dim]")

            # List existing contents
            try:
                existing = list(project_location.iterdir())
                if len(existing) <= 5:
                    console.print("[dim]Existing contents:[/dim]")
                    for item in existing:
                        icon = "📁" if item.is_dir() else "📄"
                        console.print(f"  {icon} {item.name}")
                else:
                    console.print(f"[dim]Directory contains {len(existing)} items[/dim]")
            except PermissionError:
                console.print("[dim]Cannot list directory contents (permission denied)[/dim]")

    # Check write permissions for parent directory
    parent_dir = project_location.parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            console.print(f"[red]✗ Cannot create parent directory:[/red] {parent_dir}")
            console.print("[dim]Check directory permissions[/dim]")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]✗ Error creating parent directory:[/red] {parent_dir}")
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    if not os.access(parent_dir, os.W_OK):
        console.print(f"[red]✗ No write permission for parent directory:[/red] {parent_dir}")
        console.print("[dim]Check directory permissions and try again[/dim]")
        raise typer.Exit(1)

    return True


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print(f"{__application_title__}: {__version__}")
        raise typer.Exit()


@app.command()
def create_project(
    project_name: Annotated[str | None, typer.Option("--project-name", "-n", help="Project name in snake_case")] = None,
    template_name: Annotated[
        str, typer.Option("--template-name", "-t", help="Template name or git URL")
    ] = "new_cli_project_template",
    features: Annotated[
        list[FeatureNames] | None, typer.Option("--features", "-f", help="List of features to install")
    ] = None,
    metadata_file: Annotated[
        str | None, typer.Option("--metadata", "-m", help="Path to YAML metadata file for template customization")
    ] = None,
    list_features: Annotated[bool, typer.Option("--list-features", "-L", help="List available features")] = False,
    preview: Annotated[bool, typer.Option("--preview", "-P", help="Preview operation")] = False,
    version: Annotated[  # pylint: disable=unused-argument
        bool | None,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
):
    """CLI entry point to create a new project from a local template or remote git repository."""
    # Validate feature dependencies on startup
    validate_feature_dependencies()

    # Load metadata if provided
    metadata = None
    if metadata_file:
        metadata_path = Path(metadata_file).expanduser().resolve()
        metadata = load_metadata_from_yaml(metadata_path)
        console.print(f"[green]✓ Loaded metadata from {metadata_path}[/green]")

    if preview:
        console.print("Preview mode enabled")
        if metadata:
            console.print("[bold cyan]Metadata loaded:[/bold cyan]")
            if metadata.project.description:
                console.print(f"  Description: {metadata.project.description}")
            if metadata.author.name:
                console.print(f"  Author: {metadata.author.name} <{metadata.author.email}>")
            if metadata.packages:
                console.print(f"  Required packages: {', '.join(metadata.packages)}")

    if list_features:
        console.print("[bold]Available Features:[/bold]")
        for feature, packages in available_features.items():
            dep_info = ""
            if feature in feature_deps:
                dep_names = [dep.value for dep in feature_deps[feature]]
                dep_info = f" (depends on: {', '.join(dep_names)})"
            console.print(f"  {feature.value}: {packages}{dep_info}")
        raise typer.Exit()

    if features is not None:
        invalid_features = [feat for feat in features if feat not in available_features]
        if invalid_features:
            console.print(f"[red]✗ Invalid feature(s):[/red] {', '.join([f.value for f in invalid_features])}")
            console.print("[dim]Available features:[/dim]")
            for feat in FeatureNames:
                console.print(f"  • {feat.value}")
            raise typer.Exit(1)

        # Show resolved dependencies if in preview mode
        if preview:
            resolved = resolve_feature_dependencies(features)
            requested_set = set(features) if features else set()
            auto_added = resolved - requested_set - {FeatureNames.BASE}

            console.print(f"[bold]Requested features:[/bold] {[f.value for f in features]}")
            console.print("[bold]BASE feature:[/bold] Always included")
            if auto_added:
                console.print(f"[bold]Auto-added dependencies:[/bold] {[f.value for f in auto_added]}")
            console.print(
                f"[bold]Final feature list:[/bold] {[f.value for f in sorted(resolved, key=lambda x: x.value)]}"
            )
    if not project_name:
        console.print("[red]✗ Project name is required[/red]")
        console.print("[dim]Use --project-name or -n to specify a project name[/dim]")
        console.print("[dim]Example: bsp -n my_awesome_project[/dim]")
        raise typer.Exit(1)

    # Validate project name
    if not project_name.replace("_", "").replace("-", "").isalnum():
        console.print(f"[red]✗ Invalid project name:[/red] {project_name}")
        console.print("[dim]Project name should contain only letters, numbers, underscores, and hyphens[/dim]")
        console.print("[dim]Examples: my_project, awesome-app, project123[/dim]")
        raise typer.Exit(1)

    if len(project_name) > 50:
        console.print(f"[red]✗ Project name too long:[/red] {len(project_name)} characters")
        console.print("[dim]Project name should be 50 characters or less[/dim]")
        raise typer.Exit(1)

    # Get template directory (local or remote)
    try:
        template_dir, is_temp_template = get_template_directory(template_name)
    except Exception as e:
        console.print("[red]✗ Failed to get template directory:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Determine project location
    try:
        if is_git_url(template_name):
            # For remote templates, use current working directory
            project_location = Path.cwd() / project_name
        else:
            # For local templates, use the same repo directory
            repo_dir = find_local_repo_directory()
            if repo_dir is None:
                console.print("[red]✗ No repository directory found for local template[/red]")
                console.print("[dim]Configure BOOTSTRAP_REPO_DIR environment variable or use default paths[/dim]")
                console.print("[dim]Default paths: ~/Repos, D:/Repos, C:/Repos, ./Repos[/dim]")
                raise typer.Exit(1)
            project_location = repo_dir / project_name
    except Exception as e:
        console.print("[red]✗ Error determining project location:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Extract template name from directory for file replacements
    actual_template_name = template_dir.name

    validate_project_setup(template_dir, project_location, is_temp_template)

    # Show feature resolution summary for non-preview mode
    if not preview:
        resolved = resolve_feature_dependencies(features)
        requested_set = set(features) if features else set()
        auto_added = resolved - requested_set - {FeatureNames.BASE}

        console.print("\n[bold blue]🎯 Feature Resolution Summary:[/bold blue]")
        if features:
            console.print(f"  [cyan]📦 Requested:[/cyan] {', '.join([f.value for f in features])}")
        console.print("  [green]⭐ BASE:[/green] Always included")
        if auto_added:
            console.print(f"  [yellow]🔗 Auto-added dependencies:[/yellow] {', '.join([f.value for f in auto_added])}")
        console.print(f"  [bold]📊 Total features to install:[/bold] {len(resolved)}")
        console.print()  # Add spacing

    try:
        console.print(f"[cyan]Copying template from {template_dir} to {project_location}...[/cyan]")
        if not preview:
            copy_template(template_dir, project_location)

        console.print(f"[cyan]Renaming src/{actual_template_name} to src/{project_name}...[/cyan]")
        if not preview:
            rename_src_folder(project_location, actual_template_name, project_name)  # type: ignore

        console.print(f"[cyan]Updating files with project name '{project_name}'...[/cyan]")
        if not preview:
            update_files(project_location, actual_template_name, project_name, metadata)  # type: ignore

        console.print("[cyan]Running CLI commands...[/cyan]")
        if not preview:
            run_cli_commands(project_location, features, metadata)

        if preview:
            console.print(f"[green]✓ Preview completed for project '{project_name}'[/green]")
        else:
            console.print(f"[green]✓ Project '{project_name}' created successfully![/green]")
            console.print(f"[dim]Location: {project_location.absolute()}[/dim]")

    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Operation cancelled by user[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print("\n[red]✗ Unexpected error during project creation:[/red]")
        console.print(f"[red]Error:[/red] {e}")
        console.print(f"[dim]Template: {template_name}[/dim]")
        console.print(f"[dim]Project: {project_name}[/dim]")
        raise typer.Exit(1)
    finally:
        # Clean up temporary directory if it was created
        if is_temp_template and template_dir.exists():
            try:
                console.print("[dim]Cleaning up temporary template directory...[/dim]")
                shutil.rmtree(template_dir)
            except Exception as e:
                console.print(f"[yellow]⚠ Could not clean up temporary directory:[/yellow] {template_dir}")
                console.print(f"[yellow]Error:[/yellow] {e}")
                console.print("[dim]You may need to manually delete this directory[/dim]")


if __name__ == "__main__":
    app()
