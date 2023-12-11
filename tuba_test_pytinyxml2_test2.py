import struct
from typing import List, ByteString
from typeguard import typechecked
import pytinyxml2 as xml

class FXP:
    @typechecked
    def __init__(self, version: int, fxId: int, fxVersion: int, numPrograms: int, 
                 prgName: str, byteSize: int, xmlContent: ByteString, wavetables: List[ByteString]):
        assert len(prgName.encode('utf-8')) <= 28, "Program name must be at most 28 bytes long"
        
        self.version = version
        self.fxId = fxId
        self.fxVersion = fxVersion
        self.numPrograms = numPrograms
        self.prgName = prgName
        self.byteSize = byteSize
        self.xmlContent = xmlContent
        self.wavetables = wavetables

    def save(self, filename: str) -> None:
        # Decode and parse the XML content
        xml_string_content = self.xmlContent.decode('utf-8')

        # Parse and serialize XML content using pytinyxml2 without extra formatting
        doc = xml.XMLDocument()
        doc.Parse(xml_string_content)

        # Initialize XMLPrinter without arguments
        printer = xml.XMLPrinter()
        
        # Use compact mode for printing (if available in pytinyxml2)
        # Note: If pytinyxml2 doesn't support setting compact mode, 
        #       you might need to handle compact serialization manually.
        # printer.SetCompact(True)

        doc.Print(printer)
        serialized_xml = printer.CStr().encode('utf-8')

        # Calculate total size for header
        total_size = len(serialized_xml) + sum(len(wt) for wt in self.wavetables)

        # Pack the header
        fxp_header = struct.pack(
            ">4si4siiii28si",
            b'CcnK',
            total_size,
            b'FPCh',
            self.version,
            self.fxId,
            self.fxVersion,
            self.numPrograms,
            self.prgName.encode('utf-8'),
            len(serialized_xml)
        )

        # Write to file
        with open(filename, 'wb') as f:
            f.write(fxp_header)
            f.write(serialized_xml)
            for wt in self.wavetables:
                f.write(wt)

        # Debug prints
        print("Serialized XML Size:", len(serialized_xml))
        print("Total wavetable data size:", sum(len(wt) for wt in self.wavetables))
        print("Header byte size field:", len(fxp_header))
            
    @staticmethod
    def format_xml_string(xml_string):
        # Custom XML formatting logic goes here
        return xml_string.replace('\n', '').replace('\t', '')

    @staticmethod
    def load(filename: str) -> "FXP":
        with open(filename, 'rb') as f:
            fxp_header = f.read(60)
            _, byteSize, _, version, fxId, fxVersion, numPrograms, prgName, chunkSize = struct.unpack(
                ">4si4siiii28si", fxp_header)

            file_content = f.read()
            xml_start = file_content.find(b'<?xml')
            xml_end = file_content.find(b'</patch>') + len(b'</patch>')
            xml_content = file_content[xml_start:xml_end]
            wavetables = [file_content[xml_end:]]

            prgName = prgName.strip(b'\x00').decode('utf-8')

            # Debugging: Output the sizes of the parts being read
            print("XML Content Size:", len(xml_content))
            print("Wavetable Content Size:", len(wavetables[0]))

            return FXP(version, fxId, fxVersion, numPrograms, prgName, byteSize, xml_content, wavetables)

if __name__ == "__main__":
    fxp = FXP.load("C:/Users/Juan/Desktop/SpaceViola.fxp")
    fxp.save("C:/Users/Juan/Desktop/new_SpaceViola.fxp")

    original_data = open("C:/Users/Juan/Desktop/SpaceViola.fxp", "rb").read()
    new_data = open("C:/Users/Juan/Desktop/new_SpaceViola.fxp", "rb").read()

    # Extended debugging: Compare larger portions of the files
    print("Original File Size:", len(original_data))
    print("New File Size:", len(new_data))
    print("Original File Sample:", original_data[:200])  # Increased sample size
    print("New File Sample:", new_data[:200])            # Increased sample size

    # Detailed comparison of the header fields
    for i in range(60):  # Assuming header size is 60 bytes
        if original_data[i] != new_data[i]:
            print(f"Difference in header at byte {i}: Original {original_data[i]}, New {new_data[i]}")

    # Compare beyond the header
    for i in range(60, 300):  # Compare further into the file
        if original_data[i] != new_data[i]:
            print(f"Difference at byte {i}: Original {original_data[i]}, New {new_data[i]}")

    assert original_data == new_data, "Files are not identical"
