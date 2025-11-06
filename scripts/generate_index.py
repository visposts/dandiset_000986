#!/usr/bin/env python3
"""Generate index.md from template using session configuration and figure URLs."""

import yaml
from pathlib import Path
from jinja2 import Template

# Load sessions configuration
with open("sessions.yaml", "r") as f:
    config = yaml.safe_load(f)

# Read figure URLs for each session
sessions_with_urls = []
for session in config["sessions"]:
    session_id = session["session_id"]
    url_file = Path(f"figures/{session_id}.url")
    
    if url_file.exists():
        with open(url_file, "r") as f:
            figure_url = f.read().strip()
    else:
        # Placeholder if URL file doesn't exist yet
        figure_url = "# Figure not yet generated"
    
    session_with_url = session.copy()
    session_with_url["figure_url"] = figure_url
    sessions_with_urls.append(session_with_url)

# Load and render template
with open("templates/index.md.jinja", "r") as f:
    template = Template(f.read())

rendered = template.render(
    dandiset_id=config["dandiset_id"],
    sessions=sessions_with_urls
)

# Write output
with open("index.md", "w") as f:
    f.write(rendered)

print(f"Generated index.md with {len(sessions_with_urls)} sessions")
