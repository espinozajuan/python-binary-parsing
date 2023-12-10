import struct
import xml.etree.ElementTree as ET
from typing import List, ByteString
from typeguard import typechecked

class FXP:
    @typechecked
    def __init__(self, version: int, fxId: int, fxVersion: int, numPrograms: int,
                 prgName: str, chunkSize: int, xmlContent: ByteString, wavetables: List[ByteString]):
        assert len(prgName.encode('utf-8')) <= 28, "Program name must be at most 28 bytes long"
        
        self.version: int = version
        self.fxId: int = fxId
        self.fxVersion: int = fxVersion
        self.numPrograms: int = numPrograms
        self.prgName: str = prgName
        self.chunkSize: int = chunkSize
        self.xmlContent: ByteString = xmlContent
        self.wavetables: List[ByteString] = wavetables

    @typechecked
    def save(self, filename: str) -> None:
        # Serialize XML content to bytes
        xml_str = self.xmlContent
        fxp_header: ByteString = struct.pack(
            ">4si4siiii28si",
            b'CcnK',
            0,  # Set byteSize to 0 to match the original file
            b'FPCh',
            self.version,
            self.fxId,
            self.fxVersion,
            self.numPrograms,
            self.prgName.encode('utf-8'),
            len(xml_str)
        )

        assert len(fxp_header) == 60, "FXP header size must be 60 bytes"

        wavetable_data: ByteString = b''.join(self.wavetables)

        with open(filename, 'wb') as f:
            f.write(fxp_header)
            f.write(xml_str)
            f.write(wavetable_data)

    @staticmethod
    @typechecked
    def load(filename: str) -> "FXP":
        with open(filename, 'rb') as f:
            fxp_header: ByteString = f.read(60)
            assert len(fxp_header) == 60, "FXP header size must be 60 bytes"

            chunkmagic, byteSize, fxMagic, version, fxId, fxVersion, numPrograms, prgName, chunkSize = struct.unpack(
                ">4si4siiii28si", fxp_header)

            xml_content: ByteString = f.read(chunkSize)
            wavetables: ByteString = f.read()

            assert len(prgName.strip(b'\x00')) <= 28, "Program name must be at most 28 bytes long"

        return FXP(version, fxId, fxVersion, numPrograms, prgName.strip(b'\x00').decode('utf-8'),
                   chunkSize, xml_content, [wavetables])

if __name__ == "__main__":
    fxp = FXP.load(r"C:\ProgramData\Surge XT\patches_3rdparty\A.Liv\Basses\Sqweird.fxp")
    fxp.save(r"C:\Users\Juan\Desktop\new_Sqweird.fxp")
    original_data = open(r"C:\ProgramData\Surge XT\patches_3rdparty\A.Liv\Basses\Sqweird.fxp", "rb").read()
    new_data = open(r"C:\Users\Juan\Desktop\new_Sqweird.fxp", "rb").read()
    assert original_data == new_data, "Files do not match"
