rule all:
    input:
        "figures/ses-1.url",
        "figures/ses-2.url",

rule create_figure1:
    output:
        "figures/ses-1.url"
    shell:
        "python scripts/create_figure.py sub-LA11/sub-LA11_ses-1_behavior.nwb {output}"

rule create_figure2:
    output:
        "figures/ses-2.url"
    shell:
        "python scripts/create_figure.py sub-LA11/sub-LA11_ses-2_behavior.nwb {output}"
