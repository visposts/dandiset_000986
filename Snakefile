import yaml

# Load session configuration
with open("sessions.yaml", "r") as f:
    config = yaml.safe_load(f)

# Extract session information
sessions = config["sessions"]
session_ids = [s["session_id"] for s in sessions]

# Define all targets
rule all:
    input:
        expand("figures/{session_id}.url", session_id=session_ids),
        "index.md"

# Dynamic rule to create figures for each session
rule create_figure:
    output:
        "figures/{session_id}.url"
    run:
        # Find the session configuration
        session = next(s for s in sessions if s["session_id"] == wildcards.session_id)
        nwb_path = session["nwb_path"]
        
        # Run the figure creation script
        shell(f"python scripts/create_figure.py {nwb_path} {{output}}")

# Rule to generate index.md from template
rule generate_index:
    input:
        expand("figures/{session_id}.url", session_id=session_ids),
        "sessions.yaml",
        "templates/index.md.jinja"
    output:
        "index.md"
    shell:
        "python scripts/generate_index.py"
