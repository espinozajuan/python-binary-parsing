import struct
from typing import List, ByteString
from typeguard import typechecked
import pytinyxml2 as xml

class FXP:
    @typechecked
    def __init__(self, version: int, fxId: int, fxVersion: int, numPrograms: int, 
                 prgName: str, byteSize: int, xmlContent: ByteString, wavetables: List[ByteString]):
        assert len(prgName.encode('utf-8')) <= 28, "Program name must be at most 28 bytes long"
        
        self.version: int = version
        self.fxId: int = fxId
        self.fxVersion: int = fxVersion
        self.numPrograms: int = numPrograms
        self.prgName: str = prgName
        self.byteSize: int = byteSize
        self.xmlContent: ByteString = xmlContent
        self.wavetables: List[ByteString] = wavetables

    def save(self, filename: str) -> None:
        # Parse and serialize XML content using pytinyxml2
        doc = xml.XMLDocument()
        doc.Parse(self.xmlContent.decode('latin1'))
        printer = xml.XMLPrinter()
        doc.Print(printer)
        serialized_xml = printer.CStr().encode('latin1')

        # Adjust byteSize to account for any change in the size of the XML content
        adjusted_byteSize = self.byteSize + (len(serialized_xml) - len(self.xmlContent))

        fxp_header: ByteString = struct.pack(
            ">4si4siiii28si",
            b'CcnK',
            adjusted_byteSize,
            b'FPCh',
            self.version,
            self.fxId,
            self.fxVersion,
            self.numPrograms,
            self.prgName.encode('utf-8'),
            len(serialized_xml)
        )

        assert len(fxp_header) == 60, "FXP header size must be 60 bytes"

        with open(filename, 'wb') as f:
            f.write(fxp_header)
            f.write(serialized_xml)
            f.write(self.wavetables[0])

    @staticmethod
    def load(filename: str) -> "FXP":
        with open(filename, 'rb') as f:
            fxp_header: ByteString = f.read(60)
            chunkmagic, byteSize, fxMagic, version, fxId, fxVersion, numPrograms, prgName, chunkSize = struct.unpack(
                ">4si4siiii28si", fxp_header)

            xml_content: ByteString = f.read(chunkSize)
            wavetables: ByteString = f.read()

            return FXP(version, fxId, fxVersion, numPrograms, prgName.strip(b'\x00').decode('utf-8'), 
                       byteSize, xml_content, [wavetables])

if __name__ == "__main__":
    fxp = FXP.load("C:/Users/Juan/Desktop/SpaceViola.fxp")
    fxp.save("C:/Users/Juan/Desktop/new_SpaceViola.fxp")

    original_data = open("C:/Users/Juan/Desktop/SpaceViola.fxp", "rb").read()
    new_data = open("C:/Users/Juan/Desktop/new_SpaceViola.fxp", "rb").read()

    # Debugging: Print sizes and content samples
    print("Original File Size:", len(original_data))
    print("New File Size:", len(new_data))
    print("Original File Sample:", original_data[:100])
    print("New File Sample:", new_data[:100])

    assert original_data == new_data, "Files are not identical"
