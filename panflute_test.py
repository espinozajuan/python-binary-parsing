import argparse
import glob
import os
import struct
import tempfile
from typing import ByteString, List

import pytinyxml2 as xml
from tqdm import tqdm
from typeguard import typechecked

@typechecked
class FXPBinaryData:
    def __init__(self, prgName: str, chunkSize: int, fxp_header: ByteString, non_xml_data_before: ByteString, xml_content: ByteString, non_xml_data_after: ByteString, wavetables: List[ByteString]):
        assert len(prgName.encode('utf-8')) <= 28, "Program name must be at most 28 bytes long"
        self.prgName = prgName
        self.chunkSize = chunkSize
        self.fxp_header = fxp_header
        self.non_xml_data_before = non_xml_data_before
        self.xml_content = xml_content
        self.non_xml_data_after = non_xml_data_after
        self.wavetables = wavetables

    @staticmethod
    def parse_header(fxp_header: ByteString) -> dict:
        header_format = ">4s i 4s i i i i 28s i"
        fields = struct.unpack(header_format, fxp_header)
        header = {
            "File Signature": fields[0].decode(),
            "Version": fields[1],
            "Type": fields[2].decode(),
            "Sub-Version": fields[3],
            "Timestamp": fields[4],
            "Number of Records": fields[5],
            "Record Size": fields[6],
            "Payload": fields[7].decode().rstrip("\x00"),
            "Checksum": fields[8],
        }
        return header

    @staticmethod
    def load(filename: str) -> "FXPBinaryData":
        with open(filename, "rb") as f:
            fxp_header = f.read(60)
            assert len(fxp_header) == 60, "FXP header size must be 60 bytes"
            parsed_header = FXPBinaryData.parse_header(fxp_header)
            print("Parsed Header:", parsed_header)
            content = f.read()
            start = content.find(b"<?xml")
            end = content.find(b"</patch>") + len(b"</patch>")
            non_xml_data_before = content[:start] if start != -1 else b""
            xml_content = content[start:end] if start != -1 and end != -1 else b""
            non_xml_data_after = content[end:] if end != -1 else b""
            wavetables = []  # Logic to extract wavetables (if applicable)
            return FXPBinaryData(prgName='', chunkSize=0, fxp_header=fxp_header, non_xml_data_before=non_xml_data_before, xml_content=xml_content, non_xml_data_after=non_xml_data_after, wavetables=wavetables)

    def save(self, file) -> None:
        if isinstance(file, str):
            with open(file, "wb") as f:
                self._write_to_file(f)
        else:
            self._write_to_file(file)

    def _write_to_file(self, f):
        f.write(self.fxp_header)
        f.write(self.non_xml_data_before)
        f.write(self.xml_content)
        f.write(self.non_xml_data_after)
        for wt in self.wavetables:
            f.write(wt)

class FXPHumanReadable:
    def __init__(self, binary_data: FXPBinaryData):
        self.binary_data = binary_data
        self.extracted_xml_data = self.extract_xml_data()

    def extract_xml_data(self):
        xml_doc = xml.XMLDocument()
        xml_doc.Parse(self.binary_data.xml_content.decode())
        extracted_data = {}
        meta = xml_doc.FirstChildElement("patch").FirstChildElement("meta")
        if meta is not None:
            extracted_data["meta"] = {
                "name": meta.Attribute("name"),
                "category": meta.Attribute("category"),
                "comment": meta.Attribute("comment"),
                "author": meta.Attribute("author"),
            }
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

def check_parsing(fxp_file: str):
    try:
        binary_data = FXPBinaryData.load(fxp_file)
        human_readable = FXPHumanReadable(binary_data)
        # Save the human-readable data to a new file for demonstration
        with open(os.path.splitext(fxp_file)[0] + "_extracted_data.txt", "w") as file:
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
            tmp_file.seek(0) # Rewind to the beginning of the tempfile
            saved_data = tmp_file.read()
        # Load the original data for in-memory comparison
        with open(fxp_file, "rb") as original_file:
            original_data = original_file.read()
        # Verify the original and saved data are identical
        assert original_data == saved_data, "The original and new FXP files are not identical"
        print(f"Processed {fxp_file}")
    except Exception as e:
        print(f"Error processing {fxp_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .fxp files.")
    parser.add_argument("surge_path", type=str, help="Path to the directory containing .fxp files")
    args = parser.parse_args()
    fxp_files = glob.glob(os.path.join(args.surge_path, "**/*.fxp"), recursive=True)
    for fxp_file in tqdm(fxp_files):
        check_parsing(fxp_file)
