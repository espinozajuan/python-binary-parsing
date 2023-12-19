import struct
import pytinyxml2 as xml
from typing import List, ByteString
from typeguard import typechecked
from tqdm import tqdm
import glob
import os
import tempfile

@typechecked
class FXPBinaryData:
    def __init__(self, fxp_header: ByteString, non_xml_data_before: ByteString, xml_content: ByteString, non_xml_data_after: ByteString, wavetables: List[ByteString]):
        self.fxp_header = fxp_header
        self.non_xml_data_before = non_xml_data_before
        self.xml_content = xml_content
        self.non_xml_data_after = non_xml_data_after
        self.wavetables = wavetables

    @staticmethod
    def load(filename: str) -> "FXPBinaryData":
        with open(filename, 'rb') as f:
            fxp_header = f.read(60)
            assert len(fxp_header) == 60, "FXP header size must be 60 bytes"
            content = f.read()
            start = content.find(b"<?xml")
            end = content.find(b"</patch>") + len(b"</patch>")
            non_xml_data_before = content[:start] if start != -1 else b''
            xml_content = content[start:end] if start != -1 and end != -1 else b''
            non_xml_data_after = content[end:] if end != -1 else b''
            
            # Logic to extract wavetables (if applicable)
            wavetables = []  
            return FXPBinaryData(fxp_header, non_xml_data_before, xml_content, non_xml_data_after, wavetables)

    def save(self, file) -> None:
        """
        Save the FXP data to a file.

        :param file: A file path (str) or a file-like object.
        """
        if isinstance(file, str):
            with open(file, 'wb') as f:
                self._write_to_file(f)
        else:
            self._write_to_file(file)

    def _write_to_file(self, f):
        """
        Write the FXP data to a given file-like object.

        :param f: A file-like object.
        """
        f.write(self.fxp_header)
        f.write(self.non_xml_data_before)
        f.write(self.xml_content)
        f.write(self.non_xml_data_after)
        for wt in self.wavetables:
            f.write(wt)

class FXPHumanReadable:
    @typechecked
    def __init__(self, binary_data: FXPBinaryData):
        self.binary_data = binary_data
        self.extracted_xml_data = self.extract_xml_data()

    @typechecked
    def extract_xml_data(self) -> dict:
        xml_doc = xml.XMLDocument()
        xml_doc.Parse(self.binary_data.xml_content.decode())
        extracted_data = {}

        # Extracting meta information
        meta = xml_doc.FirstChildElement("patch").FirstChildElement("meta")
        if meta is not None:
            extracted_data["meta"] = {
                "name": meta.Attribute("name"),
                "category": meta.Attribute("category"),
                "comment": meta.Attribute("comment"),
                "author": meta.Attribute("author")
            }

        # Extracting parameters
        parameters = xml_doc.FirstChildElement("patch").FirstChildElement("parameters")
        param = parameters.FirstChildElement()
        extracted_data["parameters"] = {}
        while param is not None:
            name = param.Value()
            param_type = param.Attribute("type")
            param_value = param.Attribute("value")
            extracted_data["parameters"][name] = {"type": param_type, "value": param_value}
            param = param.NextSiblingElement()

        return extracted_data

if __name__ == "__main__":
    # Load and process a single FXP file for demonstration
    single_fxp_path = r"C:\Users\Juan\Desktop\Boom.fxp"

    # Load the original FXP file as binary data
    binary_data = FXPBinaryData.load(single_fxp_path)

    # Convert binary data to human-readable format
    human_readable = FXPHumanReadable(binary_data)

    # Save the human-readable data to a new file
    with open(r"C:\Users\Juan\Desktop\extracted_data.txt", "w") as file:
        for key, value in human_readable.extracted_xml_data.items():
            if isinstance(value, dict):
                file.write(f"{key}:\n")
                for subkey, subvalue in value.items():
                    file.write(f"    {subkey}: {subvalue}\n")
            else:
                file.write(f"{key}: {value}\n")

    # Save back to binary format using a temporary file for comparison
    with tempfile.TemporaryFile() as tmp_file:
        binary_data.save(tmp_file)
        tmp_file.seek(0)  # Rewind to the beginning of the tempfile
        saved_data = tmp_file.read()

    # Load the original data for in-memory comparison
    with open(single_fxp_path, 'rb') as original_file:
        original_data = original_file.read()

    # Verify the original and saved data are identical
    assert original_data == saved_data, "The original and new FXP files are not identical"

    # Set default directory path for batch processing of FXP files
    surge_path = r"C:\ProgramData\Surge XT"

    # Find all .fxp files in the specified directory and its subdirectories
    fxp_files = glob.glob(os.path.join(surge_path, "**/*.fxp"), recursive=True)

    # Process each FXP file with a progress bar
    for fxp_file in tqdm(fxp_files):
        try:
            binary_data = FXPBinaryData.load(fxp_file)
            # Additional processing of binary_data (if required)

            # For demonstration, print the filename
            print(f"Processed {fxp_file}")
        except Exception as e:
            print(f"Error processing {fxp_file}: {e}")