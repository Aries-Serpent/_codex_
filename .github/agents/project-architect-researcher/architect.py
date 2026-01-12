#!/usr/bin/env python3
"""
Project Architect Researcher Agent
Generates artifacts for NotebookLM, NotionLM, and AI knowledge platforms
Includes NotebookLM API integration and PRO feature support

NOTE: NotebookLM API integration is a reference implementation.
As of January 2026, NotebookLM does not have a publicly documented API.
This implementation serves as a template for future API integration when available.
For current usage, sources are generated locally and can be uploaded manually.
"""
import click
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import requests
import os


class NotebookLMAPIUnavailableError(Exception):
    """Raised when NotebookLM API is not available or accessible."""
    pass


@dataclass
class NotebookLMSource:
    """Represents a NotebookLM source document."""
    title: str
    content: str
    source_type: str  # 'markdown', 'pdf', 'audio', 'video', 'url'
    metadata: Dict[str, Any]
    citations: List[str]
    
@dataclass
class NotebookLMNotebook:
    """Represents a NotebookLM notebook (PRO feature)."""
    notebook_id: str
    title: str
    sources: List[NotebookLMSource]
    audio_overview: Optional[str]  # PRO: Generated audio URL
    shared_links: List[str]  # PRO: Shared notebook URLs
    

class NotebookLMAPI:
    """NotebookLM API client with PRO features.
    
    NOTE: This is a reference implementation. NotebookLM API endpoints
    may not be publicly available. This code demonstrates the expected
    integration pattern for when the API becomes available.
    
    For current usage, use the local export feature and upload manually
    to https://notebooklm.google.com
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('NOTEBOOKLM_API_KEY')
        # NOTE: This default base URL is speculative and may not exist.
        # It can be overridden via the NOTEBOOKLM_API_BASE_URL environment variable.
        self.base_url = os.getenv(
            "NOTEBOOKLM_API_BASE_URL",
            "https://notebooklm.google.com/api/v1",  # NOTE: speculative placeholder URL; may not exist
        )
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self._api_available = False  # Track if API is actually available
        self.pro_enabled = self._check_pro_status()
    
    def _check_pro_status(self) -> bool:
        """Check if user has NotebookLM PRO subscription.
        
        Returns:
            bool: True if user has PRO subscription and API is available,
                  False if API is not available, authentication fails, or user
                  does not have PRO subscription.
        
        Side effects:
            Sets _api_available flag based on API accessibility.
        """
        if not self.api_key:
            click.echo("ℹ️  No API key provided. API features disabled.", err=True)
            self._api_available = False
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/account/subscription",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                self._api_available = True
                data = response.json()
                return data.get('subscription_tier') == 'pro'
            elif response.status_code == 404:
                click.echo("ℹ️  NotebookLM API not yet available. Use manual upload.", err=True)
                self._api_available = False
                return False
        except requests.exceptions.RequestException as e:
            click.echo(f"ℹ️  NotebookLM API not accessible: {e}. Use manual upload.", err=True)
        
        self._api_available = False
        return False
    
    def _ensure_api_available(self) -> None:
        """Ensure API is available before making requests.
        
        Raises:
            NotebookLMAPIUnavailableError: If API is not available
        """
        if not self._api_available:
            raise NotebookLMAPIUnavailableError(
                "NotebookLM API not available. Generate sources locally and "
                "upload manually to https://notebooklm.google.com"
            )
    
    def create_notebook(self, title: str, description: str = "") -> str:
        """Create a new NotebookLM notebook.
        
        Raises:
            NotebookLMAPIUnavailableError: If API is not available or creation fails
        """
        self._ensure_api_available()
        
        payload = {
            "title": title,
            "description": description,
            "created_at": datetime.now(datetime.timezone.utc).isoformat()
        }
        
        response = requests.post(
            f"{self.base_url}/notebooks",
            headers=self.headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            notebook_id = response.json()['notebook_id']
            click.echo(f"✅ Created notebook: {notebook_id}")
            return notebook_id
        else:
            raise Exception(f"Failed to create notebook: {response.text}")
    
    def upload_source(self, notebook_id: str, source: NotebookLMSource) -> str:
        """Upload a source to NotebookLM notebook.
        
        Raises:
            NotebookLMAPIUnavailableError: If API is not available or upload fails
        """
        self._ensure_api_available()
        
        payload = {
            "notebook_id": notebook_id,
            "title": source.title,
            "content": source.content,
            "source_type": source.source_type,
            "metadata": source.metadata
        }
        
        response = requests.post(
            f"{self.base_url}/notebooks/{notebook_id}/sources",
            headers=self.headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            source_id = response.json()['source_id']
            click.echo(f"✅ Uploaded source: {source.title}")
            return source_id
        else:
            raise Exception(f"Failed to upload source: {response.text}")
    
    def generate_audio_overview(self, notebook_id: str, 
                                duration: str = "medium") -> str:
        """
        Generate audio overview (PRO feature).
        
        Args:
            notebook_id: The notebook ID
            duration: 'short' (5min), 'medium' (10min), 'long' (20min)
        
        Returns:
            Audio URL
        """
        if not self.pro_enabled:
            raise Exception("Audio overview requires NotebookLM PRO subscription")
        
        payload = {
            "notebook_id": notebook_id,
            "duration": duration,
            "voice_style": "conversational",  # PRO: conversational, formal, technical
            "include_timestamps": True
        }
        
        response = requests.post(
            f"{self.base_url}/notebooks/{notebook_id}/audio-overview",
            headers=self.headers,
            json=payload,
            timeout=30  # Audio generation may take longer
        )
        
        if response.status_code == 200:
            audio_url = response.json()['audio_url']
            click.echo(f"🎙️ Generated audio overview: {audio_url}")
            return audio_url
        else:
            raise Exception(f"Failed to generate audio: {response.text}")
    
    def create_shared_link(self, notebook_id: str, 
                          permissions: str = "view") -> str:
        """
        Create shareable link (PRO feature).
        
        Args:
            notebook_id: The notebook ID
            permissions: 'view', 'comment', 'edit'
        
        Returns:
            Shareable URL
        """
        if not self.pro_enabled:
            raise Exception("Shared links require NotebookLM PRO subscription")
        
        payload = {
            "notebook_id": notebook_id,
            "permissions": permissions,
            "expires_in_days": 30  # PRO: customizable expiration
        }
        
        response = requests.post(
            f"{self.base_url}/notebooks/{notebook_id}/share",
            headers=self.headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            share_url = response.json()['share_url']
            click.echo(f"🔗 Created shareable link: {share_url}")
            return share_url
        else:
            raise Exception(f"Failed to create share link: {response.text}")
    
    def add_inline_citations(self, notebook_id: str, 
                            source_ids: List[str]) -> Dict:
        """
        Enable inline citations (PRO feature).
        
        Returns citations in responses grounded to specific sources.
        """
        if not self.pro_enabled:
            raise Exception("Inline citations require NotebookLM PRO subscription")
        
        payload = {
            "notebook_id": notebook_id,
            "source_ids": source_ids,
            "citation_style": "inline",  # PRO: inline, footnote, endnote
            "include_page_numbers": True
        }
        
        response = requests.post(
            f"{self.base_url}/notebooks/{notebook_id}/citations/enable",
            headers=self.headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            click.echo(f"✅ Enabled inline citations for {len(source_ids)} sources")
            return response.json()
        else:
            raise Exception(f"Failed to enable citations: {response.text}")
    
    def export_notebook(self, notebook_id: str, 
                       format: str = "pdf") -> str:
        """
        Export notebook (PRO feature).
        
        Args:
            notebook_id: The notebook ID
            format: 'pdf', 'docx', 'markdown', 'html'
        
        Returns:
            Download URL
        """
        if not self.pro_enabled:
            raise Exception("Export requires NotebookLM PRO subscription")
        
        response = requests.post(
            f"{self.base_url}/notebooks/{notebook_id}/export",
            headers=self.headers,
            json={"format": format},
            timeout=60  # Export may take longer for large notebooks
        )
        
        if response.status_code == 200:
            download_url = response.json()['download_url']
            click.echo(f"📥 Export ready: {download_url}")
            return download_url
        else:
            raise Exception(f"Failed to export: {response.text}")


class ProjectArchitect:
    """Main architect agent for project planning and artifact generation."""
    
    def __init__(self, notebooklm_api_key: Optional[str] = None):
        self.nlm_api = NotebookLMAPI(notebooklm_api_key) if notebooklm_api_key else None
    
    def generate_notebooklm_sources(self, project_yaml: Path, 
                                    output_dir: Path) -> List[NotebookLMSource]:
        """Generate NotebookLM source documents from project plan."""
        with open(project_yaml) as f:
            project = yaml.safe_load(f)
        
        sources = []
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Source 1: Project Overview
        overview = self._create_overview_source(project)
        sources.append(overview)
        (output_dir / "01_project_overview.md").write_text(overview.content)
        
        # Source 2: Architecture
        architecture = self._create_architecture_source(project)
        sources.append(architecture)
        (output_dir / "02_architecture.md").write_text(architecture.content)
        
        # Source 3+: Phase-specific sources
        for i, phase in enumerate(project.get('phases', []), start=3):
            phase_source = self._create_phase_source(phase, i-2)
            sources.append(phase_source)
            (output_dir / f"{i:02d}_phase_{i-2}.md").write_text(phase_source.content)
        
        # Create manifest for batch upload
        manifest = {
            "project": project.get('name'),
            "sources": [
                {
                    "file": f"{i:02d}_{s.title.lower().replace(' ', '_')}.md",
                    "title": s.title,
                    "type": s.source_type
                }
                for i, s in enumerate(sources, start=1)
            ],
            "created": datetime.now(datetime.timezone.utc).isoformat()
        }
        (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        
        click.echo(f"✅ Generated {len(sources)} NotebookLM sources in {output_dir}")
        return sources
    
    def _create_overview_source(self, project: Dict) -> NotebookLMSource:
        """Create project overview source for NotebookLM."""
        content = f"""---
title: {project.get('name', 'Project')}
type: project_documentation
version: {project.get('version', '1.0.0')}
last_updated: {datetime.now(datetime.timezone.utc).date().isoformat()}
---

# {project.get('name', 'Project')}

## 📋 Quick Reference
- **Status**: {project.get('status', 'Planning')}
- **Version**: {project.get('version', '1.0.0')}
- **Start Date**: {project.get('start_date', 'TBD')}
- **Target Date**: {project.get('target_date', 'TBD')}

## 🎯 Objectives
"""
        for i, obj in enumerate(project.get('objectives', []), start=1):
            content += f"{i}. {obj}\n"
        
        content += f"""
## 📊 Current State
{project.get('description', 'No description provided.')}

## 🗺️ Phases
"""
        for phase in project.get('phases', []):
            content += f"- **{phase.get('name')}**: {phase.get('duration', 'TBD')}\n"
        
        return NotebookLMSource(
            title="Project Overview",
            content=content,
            source_type="markdown",
            metadata={"section": "overview"},
            citations=[]
        )
    
    def _create_architecture_source(self, project: Dict) -> NotebookLMSource:
        """Create architecture source for NotebookLM."""
        content = f"""# Architecture: {project.get('name')}

## System Design
{project.get('architecture', {}).get('description', 'Architecture details pending.')}

## Components
"""
        for comp in project.get('architecture', {}).get('components', []):
            content += f"### {comp.get('name')}\n{comp.get('description', '')}\n\n"
        
        return NotebookLMSource(
            title="Architecture Design",
            content=content,
            source_type="markdown",
            metadata={"section": "architecture"},
            citations=[]
        )
    
    def _create_phase_source(self, phase: Dict, phase_num: int) -> NotebookLMSource:
        """Create phase-specific source for NotebookLM."""
        content = f"""# Phase {phase_num}: {phase.get('name')}

## Overview
- **Duration**: {phase.get('duration', 'TBD')}
- **Status**: {phase.get('status', 'Not Started')}
- **Dependencies**: {', '.join(phase.get('dependencies', []))}

## Tasks
"""
        for task in phase.get('tasks', []):
            content += f"""
### {task.get('name')}
- **ID**: {task.get('id')}
- **Effort**: {task.get('effort', 'TBD')}
- **Status**: {task.get('status', 'Pending')}
- **Description**: {task.get('description', 'No description')}
"""
        
        return NotebookLMSource(
            title=f"Phase {phase_num}: {phase.get('name')}",
            content=content,
            source_type="markdown",
            metadata={"section": "phase", "phase_number": phase_num},
            citations=[]
        )


@click.group()
def cli():
    """Project Architect Researcher Agent"""
    pass


@cli.command()
@click.option('--project', type=click.Path(exists=True), required=True,
              help='Project YAML file')
@click.option('--output', type=click.Path(), required=True,
              help='Output directory for sources')
@click.option('--api-key', envvar='NOTEBOOKLM_API_KEY',
              help='NotebookLM API key (or set NOTEBOOKLM_API_KEY env var)')
@click.option('--upload/--no-upload', default=False,
              help='Upload to NotebookLM via API (requires API key)')
@click.option('--generate-audio/--no-generate-audio', default=False,
              help='Generate audio overview (PRO feature)')
@click.option('--create-share-link/--no-create-share-link', default=False,
              help='Create shareable link (PRO feature)')
def export_notebooklm(project, output, api_key, upload, generate_audio, create_share_link):
    """Generate NotebookLM source package from project plan."""
    architect = ProjectArchitect(api_key)
    output_path = Path(output)
    
    # Generate local sources
    sources = architect.generate_notebooklm_sources(Path(project), output_path)
    
    if upload and api_key:
        # Upload via API
        project_data = yaml.safe_load(Path(project).read_text())
        notebook_id = architect.nlm_api.create_notebook(
            title=project_data.get('name', 'Project'),
            description=project_data.get('description', '')
        )
        
        source_ids = []
        for source in sources:
            source_id = architect.nlm_api.upload_source(notebook_id, source)
            source_ids.append(source_id)
        
        # PRO features
        if architect.nlm_api.pro_enabled:
            # Enable inline citations
            architect.nlm_api.add_inline_citations(notebook_id, source_ids)
            
            if generate_audio:
                audio_url = architect.nlm_api.generate_audio_overview(notebook_id)
                click.echo(f"🎙️ Audio overview: {audio_url}")
            
            if create_share_link:
                share_url = architect.nlm_api.create_shared_link(notebook_id, 'view')
                click.echo(f"🔗 Share link: {share_url}")
        else:
            click.echo("ℹ️  PRO features require NotebookLM PRO subscription")
    
    click.echo(f"\n✅ Complete! Sources ready in {output_path}/")
    if not upload:
        click.echo(f"📤 Upload manually to: https://notebooklm.google.com")


@cli.command()
@click.option('--notebook-id', required=True, help='NotebookLM notebook ID')
@click.option('--api-key', envvar='NOTEBOOKLM_API_KEY', required=True)
@click.option('--duration', type=click.Choice(['short', 'medium', 'long']), 
              default='medium')
def generate_audio(notebook_id, api_key, duration):
    """Generate audio overview (PRO feature)."""
    architect = ProjectArchitect(api_key)
    audio_url = architect.nlm_api.generate_audio_overview(notebook_id, duration)
    click.echo(f"✅ Audio generated: {audio_url}")


@cli.command()
@click.option('--notebook-id', required=True)
@click.option('--api-key', envvar='NOTEBOOKLM_API_KEY', required=True)
@click.option('--permissions', type=click.Choice(['view', 'comment', 'edit']),
              default='view')
def share(notebook_id, api_key, permissions):
    """Create shareable link (PRO feature)."""
    architect = ProjectArchitect(api_key)
    share_url = architect.nlm_api.create_shared_link(notebook_id, permissions)
    click.echo(f"✅ Share URL: {share_url}")


@cli.command()
@click.option('--notebook-id', required=True)
@click.option('--api-key', envvar='NOTEBOOKLM_API_KEY', required=True)
@click.option('--format', type=click.Choice(['pdf', 'docx', 'markdown', 'html']),
              default='pdf')
def export(notebook_id, api_key, format):
    """Export notebook (PRO feature)."""
    architect = ProjectArchitect(api_key)
    download_url = architect.nlm_api.export_notebook(notebook_id, format)
    click.echo(f"✅ Download: {download_url}")


if __name__ == '__main__':
    cli()
