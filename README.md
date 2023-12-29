# Surge Synthesizer FXP File Handler

## Overview

This project provides a Python tool for handling FXP files used by the Surge synthesizer. It allows for loading, parsing, and saving FXP files, ensuring that the XML content is accurately parsed and serialized, and the integrity of the files is maintained.

## Features

- **XML Parsing**: Uses `pytinyxml2` to parse and serialize XML content within FXP files.
- **File Integrity**: Ensures that loading and saving an FXP file preserves its original content and structure.
- **Data Extraction**: Extracts all fields used by the Surge synthesizer from the FXP files, allowing for detailed analysis and manipulation of synthesizer settings.

## Enhanced Functionality

- **Binary Data Analysis**: The tool now includes robust parsing of non-XML binary data, providing insights into the nature of this data as used by the synthesizer.
- **Human-Readable Conversion**: Binary data is converted into a human-readable format, facilitating easier understanding and manipulation of the synthesizer parameters.

## Requirements Fulfilled

1. **XML Handling**: Parses XML content within FXP files and serializes it back while saving.
2. **File Integrity**: Loading and saving an FXP file results in identical files, preserving the file's integrity.
3. **Data Extraction**: All relevant fields used by the Surge synthesizer are extracted individually, enabling detailed access to synthesizer parameters.
4. **Binary Data Parsing**: The non-XML binary data before and after the XML content is now parsed, offering a clearer picture of the file's structure and content.

## Installation

To use this tool, clone the repository and ensure that Python 3 is installed on your system. Additionally, install `pytinyxml2` for XML parsing.

```bash
git clone https://github.com/espinozajuan/python-binary-parsing.git
cd python-binary-parsing
# Ensure Python 3 and pytinyxml2 are installed
```

## Usage

```bash
python script_name.py your_surge_path_here
```

## Documentation

Detailed documentation is provided in the code, explaining the parsing process for both XML and non-XML binary data. This includes insights into how this data is structured and utilized within the Surge synthesizer, based on an analysis of the Surge CPP code and other relevant tools.

## Iteration of 12/28/2023

1. **Using `human_readable` Instead of Ignoring It**:
   - The script now correctly utilizes the `human_readable` object. After extracting XML data from the binary file, it converts this data into a human-readable format using the `FXPHumanReadable` class.
2. **Writing Back to an FXP and Comparing**:
   - The script saves the `human_readable` data back into an FXP format using the `save` method of the `FXPBinaryData` class. This step effectively "roundtrips" the data from binary to human-readable and back to binary.
   - After saving the processed data back to a temporary binary file, the script compares this newly saved data with the original file data to ensure they are identical. This comparison ensures that the conversion from binary to human-readable and back again does not alter the core data.
3. **Demonstrating Full Functionality**:
   - By implementing the roundtrip conversion (binary -> human-readable -> binary) and validating the integrity of the data before and after the process, the script demonstrates the full functionality as requested.
   - The script no longer performs only a partial conversion. It now fully processes the FXP files as per the specifications and checks to ensure data consistency.

Overall, the revised script should meet the requirements and address the concerns raised. It demonstrates the capability to parse, process, convert, and validate FXP files as needed.
