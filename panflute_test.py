import argparse
import glob
import os
import struct
import tempfile
import json
import base64
from typing import ByteString, List

import pytinyxml2 as xml
from tqdm import tqdm
from typeguard import typechecked


@typechecked
class FXPBinaryData:
    def __init__(
        self,
        prgName: str,
        chunkSize: int,
        fxp_header: ByteString,
        non_xml_data_before: ByteString,
        xml_content: ByteString,
        non_xml_data_after: ByteString,
        wavetables: List[ByteString],
    ):
        assert (
            len(prgName.encode("utf-8")) <= 28
        ), "Program name must be at most 28 bytes long"
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
            return FXPBinaryData(
                prgName="",
                chunkSize=0,
                fxp_header=fxp_header,
                non_xml_data_before=non_xml_data_before,
                xml_content=xml_content,
                non_xml_data_after=non_xml_data_after,
                wavetables=wavetables,
            )

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
    def __init__(self, extracted_xml_data, wavetables):
        self.extracted_xml_data = extracted_xml_data
        self.wavetables = wavetables

    @classmethod
    def from_xml(cls, xml_content: ByteString, wavetables: List[ByteString]):
        xml_doc = xml.XMLDocument()
        xml_doc.Parse(xml_content.decode())
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
            extracted_data["parameters"][name] = {
                "type": param_type,
                "value": param_value,
            }
            param = param.NextSiblingElement()
        return cls(extracted_data, wavetables)

    def to_json(self):
        data = {
            "extracted_xml_data": self.extracted_xml_data,
            "wavetables": [base64.b64encode(wt).decode() for wt in self.wavetables],
        }
        return json.dumps(data, indent=4)

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        extracted_xml_data = data["extracted_xml_data"]
        wavetables = [base64.b64decode(wt) for wt in data["wavetables"]]
        return cls(extracted_xml_data, wavetables)


def check_parsing(fxp_file: str):
    try:
        binary_data = FXPBinaryData.load(fxp_file)

        # Create FXPHumanReadable instance with extracted XML data and wavetables
        human_readable = FXPHumanReadable.from_xml(
            binary_data.xml_content, binary_data.wavetables
        )

        # Convert human-readable data to JSON and save it
        json_data = human_readable.to_json()
        with open(os.path.splitext(fxp_file)[0] + ".json", "w") as json_file:
            json_file.write(json_data)

        # Load human-readable data from JSON
        with open(os.path.splitext(fxp_file)[0] + ".json", "r") as json_file:
            loaded_json_data = json_file.read()
        loaded_human_readable = FXPHumanReadable.from_json(loaded_json_data)

        # Convert back to binary FXP format using a temporary file for comparison
        with tempfile.TemporaryFile() as tmp_file:
            binary_data.wavetables = (
                loaded_human_readable.wavetables
            )  # Update wavetables
            binary_data.save(tmp_file)
            tmp_file.seek(0)
            saved_data = tmp_file.read()

        # Load the original data for in-memory comparison
        with open(fxp_file, "rb") as original_file:
            original_data = original_file.read()

        # Verify the original and saved data are identical
        assert (
            original_data == saved_data
        ), "The original and new FXP files are not identical"
        print(f"Processed {fxp_file}")
    except Exception as e:
        print(f"Error processing {fxp_file}: {e}")


def check_parsing_strict(fxp_file: str):
    # DO NOT MODIFY THIS FUNCTION
    try:
        binary_data = FXPBinaryData.load(fxp_file)

        human_readable = FXPHumanReadable.from_binary_data(binary_data)

        json_data = human_readable.to_json()
        with open(os.path.splitext(fxp_file)[0] + ".json", "w") as json_file:
            json_file.write(json_data)

        # Load human-readable data from JSON
        with open(os.path.splitext(fxp_file)[0] + ".json", "r") as json_file:
            loaded_json_data = json_file.read()
        loaded_human_readable = FXPHumanReadable.from_json(loaded_json_data)

        loaded_binary_data = FXPBinaryData.from_human_readable(loaded_human_readable)

        # Convert back to binary FXP format using a temporary file for comparison
        with tempfile.TemporaryFile() as tmp_file:
            loaded_binary_data.save(tmp_file)
            tmp_file.seek(0)
            saved_data = tmp_file.read()

        # Load the original data for in-memory comparison
        with open(fxp_file, "rb") as original_file:
            original_data = original_file.read()

        # Verify the original and saved data are identical
        assert (
            original_data == saved_data
        ), "The original and new FXP files are not identical"
        print(f"Processed {fxp_file}")
    except Exception as e:
        print(f"Error processing {fxp_file}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .fxp files.")
    parser.add_argument(
        "surge_path", type=str, help="Path to the directory containing .fxp files"
    )
    args = parser.parse_args()
    fxp_files = glob.glob(os.path.join(args.surge_path, "**/*.fxp"), recursive=True)
    for fxp_file in tqdm(fxp_files):
        check_parsing(fxp_file)

    for fxp_file in tqdm(fxp_files):
        check_parsing_strict(fxp_file)
