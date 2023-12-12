import struct
import pytinyxml2 as xml
from typing import List, ByteString
from typeguard import typechecked

class FXP:
    @typechecked
    def __init__(self, version: int, fxId: int, fxVersion: int, numPrograms: int, 
                 prgName: str, chunkSize: int, fxp_header: ByteString, non_xml_data_before: ByteString, 
                 xmlContent: ByteString, non_xml_data_after: ByteString, extracted_xml_data: dict, wavetables: List[ByteString]):
        assert len(prgName.encode('utf-8')) <= 28, "Program name must be at most 28 bytes long"
        
        self.version: int = version
        self.fxId: int = fxId
        self.fxVersion: int = fxVersion
        self.numPrograms: int = numPrograms
        self.prgName: str = prgName
        self.chunkSize: int = chunkSize
        self.fxp_header: ByteString = fxp_header
        self.non_xml_data_before: ByteString = non_xml_data_before
        self.xmlContent: ByteString = xmlContent
        self.non_xml_data_after: ByteString = non_xml_data_after
        self.extracted_xml_data = extracted_xml_data
        self.wavetables: List[ByteString] = wavetables

    def extract_xml_data(self):
        xml_doc = xml.XMLDocument()
        xml_doc.Parse(self.xmlContent.decode(errors='ignore'))
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

    @staticmethod
    @typechecked
    def load(filename: str) -> "FXP":
        with open(filename, 'rb') as f:
            fxp_header: ByteString = f.read(60)
            assert len(fxp_header) == 60, "FXP header size must be 60 bytes"
            content = f.read()
            start = content.find(b"<?xml")
            end = content.find(b"</patch>") + len(b"</patch>")
            non_xml_data_before = content[:start] if start != -1 else b''
            xml_content = content[start:end] if start != -1 and end != -1 else b''
            non_xml_data_after = content[end:] if end != -1 else b''

            # Extract XML data
            fxp_instance = FXP(0, 0, 0, 0, '', 0, fxp_header, non_xml_data_before, xml_content, non_xml_data_after, {}, [])
            extracted_xml_data = fxp_instance.extract_xml_data()

            return FXP(0, 0, 0, 0, '', 0, fxp_header, non_xml_data_before, xml_content, non_xml_data_after, extracted_xml_data, [])

    @typechecked
    def save(self, filename: str) -> None:
        with open(filename, 'wb') as f:
            f.write(self.fxp_header)
            f.write(self.non_xml_data_before)
            f.write(self.xmlContent)
            f.write(self.non_xml_data_after)
            for wt in self.wavetables:
                f.write(wt)

if __name__ == "__main__":
    # Load the original FXP file
    original_fxp = FXP.load(r"C:\Users\Juan\Desktop\Boom.fxp")

    # Save the loaded FXP to a new file
    original_fxp.save(r"C:\Users\Juan\Desktop\new_Boom.fxp")

    # Assert that the contents of the original and new files are identical
    original_fxp_data = open(r"C:\Users\Juan\Desktop\Boom.fxp", "rb").read()
    new_fxp_data = open(r"C:\Users\Juan\Desktop\new_Boom.fxp", "rb").read()
    assert original_fxp_data == new_fxp_data, "The original and new FXP files are not identical"

    # Write the extracted data to a new file
    with open(r"C:\Users\Juan\Desktop\extracted_data.txt", "w") as file:
        for key, value in original_fxp.extracted_xml_data.items():
            if isinstance(value, dict):
                file.write(f"{key}:\n")
                for subkey, subvalue in value.items():
                    file.write(f"    {subkey}: {subvalue}\n")
            else:
                file.write(f"{key}: {value}\n")
