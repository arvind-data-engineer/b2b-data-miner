# Saved HTML Pages

Save IndiaMART listing pages in this folder.

Recommended filename example:

indiamart_industrial_machinery.html

Then run from the project root:

python run_pipeline.py --html-file html_pages\indiamart_industrial_machinery.html --category "industrial machinery" --marketplace indiamart --url "https://dir.indiamart.com/search.mp?ss=industrial%20machinery"

The web app saves uploaded or pasted HTML here automatically using this naming format:

<marketplace>_<category>.html

Example:

indiamart_industrial_machinery.html
