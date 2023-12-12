# Surge Synthesizer FXP File Handler

## Overview
This project provides a Python tool for handling FXP files used by the Surge synthesizer. It allows for loading, parsing, and saving FXP files, ensuring that the XML content is accurately parsed and serialized, and the integrity of the files is maintained.

## Features
-   **XML Parsing**: Uses `pytinyxml2` to parse and serialize XML content within FXP files.
-   **File Integrity**: Ensures that loading and saving an FXP file preserves its original content and structure.
-   **Data Extraction**: Extracts all fields used by the Surge synthesizer from the FXP files, allowing for detailed analysis and manipulation of synthesizer settings.

## Requirements Fulfilled
1.  **XML Handling**: Parses XML content within FXP files and serializes it back while saving.
2.  **File Integrity**: Loading and saving an FXP file results in identical files, preserving the file's integrity.
3.  **Data Extraction**: All relevant fields used by the Surge synthesizer are extracted individually, enabling detailed access to synthesizer parameters.

## Installation
To use this tool, clone the repository and ensure that Python 3 is installed on your system. Additionally, install `pytinyxml2` for XML parsing.
```bash
git clone https://github.com/espinozajuan/python-binary-parsing.git
cd python-binary-parsing
# Ensure Python 3 and pytinyxml2 are installed
```

## Usage

To use the tool, run the Python script with the path to the FXP file:
```python
# Load an FXP file
fxp = FXP.load("path/to/your/file.fxp")

# Save the FXP file (optional)
fxp.save("path/to/your/newfile.fxp")

# Access extracted data (example)
print(fxp.extracted_xml_data)
```
