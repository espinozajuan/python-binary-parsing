import struct
import pytinyxml2 as xml
from typing import List, ByteString
from typeguard import typechecked

class FXPBinaryData:
    @typechecked
    def __init__(self, fxp_header: ByteString, non_xml_data_before: ByteString, xml_content: ByteString, non_xml_data_after: ByteString, wavetables: List[ByteString]):
        self.fxp_header = fxp_header
        self.non_xml_data_before = non_xml_data_before
        self.xml_content = xml_content
        self.non_xml_data_after = non_xml_data_after
        self.wavetables = wavetables

    @staticmethod
    @typechecked
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
            wavetables = []  # Logic to extract wavetables
            return FXPBinaryData(fxp_header, non_xml_data_before, xml_content, non_xml_data_after, wavetables)

    @typechecked
    def save(self, filename: str) -> None:
        with open(filename, 'wb') as f:
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

        # Add extraction logic for other elements as needed

        return extracted_data

if __name__ == "__main__":
    # Load the original FXP file as binary data
    binary_data = FXPBinaryData.load(r"C:\Users\Juan\Desktop\Bork.fxp")

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

    # Save back to binary format (if needed)
    binary_data.save(r"C:\Users\Juan\Desktop\new_Bork.fxp")

    # Verification (Optional)
    original_data = open(r"C:\Users\Juan\Desktop\Bork.fxp", "rb").read()
    new_data = open(r"C:\Users\Juan\Desktop\new_Bork.fxp", "rb").read()
    assert original_data == new_data, "The original and new FXP files are not identical"
