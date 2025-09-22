# Import These Panels into ChatGPT Canvas

**Instructions:** Open a new Canvas in ChatGPT. Copy everything from this file and paste it into the Canvas. The content is structured into panelized code blocks with proper ordering. **Do not omit any part** (refer to **NO_BREVITY_POLICY.md**). Once pasted, use the Canvas table of contents to navigate files.

## Table of Contents

{% raw %}
{% for source in sources %}
- **{{ source.path }}**
  {% for panel in source.panels %}
  - *{{ panel.file }}*
  {% endfor %}
{% endfor %}

## Panels

{% raw %}

### File: {{ source.path }}

{% for panel in source.panels %}
<a name="{{ panel.file }}"></a>

{{ panel.content }}

{% endfor %}
{% endfor %}

*This template will be filled with actual panel content by the packer script.* The triple backtick fences include language hints for proper syntax highlighting (filelang is a placeholder for inferring language from file extension). Ensure all panels are included in order. After importing, you may run verification within the Canvas to double-check integrity.
