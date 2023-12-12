import struct
import pytinyxml2 as xml
from typing import List, ByteString
from typeguard import typechecked

class FXP:
    @typechecked
    def __init__(self, version: int, fxId: int, fxVersion: int, numPrograms: int, 
                 prgName: str, chunkSize: int, fxp_header: ByteString, non_xml_data_before: ByteString, 
                 xmlContent: ByteString, non_xml_data_after: ByteString, wavetables: List[ByteString]):
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
        self.wavetables: List[ByteString] = wavetables

    @typechecked
    def save(self, filename: str) -> None:
        with open(filename, 'wb') as f:
            f.write(self.fxp_header)
            f.write(self.non_xml_data_before)
            f.write(self.xmlContent)
            f.write(self.non_xml_data_after)
            for wt in self.wavetables:
                f.write(wt)  # Write wavetable data

    @staticmethod
    @typechecked
    def load(filename: str) -> "FXP":
        with open(filename, 'rb') as f:
            # Read the FXP header
            fxp_header: ByteString = f.read(60)
            assert len(fxp_header) == 60, "FXP header size must be 60 bytes"

            # Read the entire content after the header
            content = f.read()

            # Find the start and end of the XML part
            start = content.find(b"<?xml")
            end = content.find(b"</patch>") + len(b"</patch>")

            # Separate the file into parts
            non_xml_data_before = content[:start] if start != -1 else b''
            xml_content = content[start:end] if start != -1 and end != -1 else b''
            non_xml_data_after = content[end:] if end != -1 else b''

            # Dummy values for version, fxId, etc. (update as needed)
            return FXP(0, 0, 0, 0, '', 0, fxp_header, non_xml_data_before, xml_content, non_xml_data_after, [])

if __name__ == "__main__":
    # Load the original FXP file
    original_fxp = FXP.load(r"C:\Users\Juan\Desktop\Siren.fxp")

    # Save the loaded FXP to a new file
    original_fxp.save(r"C:\Users\Juan\Desktop\new_Siren.fxp")

    # Read the contents of the original and new FXP files
    original_fxp_data = open(r"C:\Users\Juan\Desktop\Siren.fxp", "rb").read()
    new_fxp_data = open(r"C:\Users\Juan\Desktop\new_Siren.fxp", "rb").read()

    # Export the contents to .txt files for comparison
    with open(r"C:\Users\Juan\Desktop\original_Siren.txt", "wb") as file:
        file.write(original_fxp_data)

    with open(r"C:\Users\Juan\Desktop\new_Siren.txt", "wb") as file:
        file.write(new_fxp_data)

    # Assert that the contents are the same
    assert original_fxp_data == new_fxp_data, "The original and new FXP files are not identical"
