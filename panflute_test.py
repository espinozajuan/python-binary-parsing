import struct
import pytinyxml2 as xml
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
        fxp_header: ByteString = struct.pack(
            ">4si4siiii28si",
            b'CcnK',
            0,
            b'FPCh',
            self.version,
            self.fxId,
            self.fxVersion,
            self.numPrograms,
            self.prgName.encode('utf-8'),
            len(self.xmlContent)
        )

        assert len(fxp_header) == 60, "FXP header size must be 60 bytes"

        wavetable_data: ByteString = b''.join(self.wavetables)

        with open(filename, 'wb') as f:
            f.write(fxp_header)
            f.write(self.xmlContent)
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
    # Load the original FXP file
    original_fxp = FXP.load(r"C:\Users\Juan\Desktop\Boom.fxp")

    # Save the loaded FXP to a new file
    original_fxp.save(r"C:\Users\Juan\Desktop\new_Boom.fxp")

    # Read the contents of the original and new FXP files
    original_fxp_data = open(r"C:\Users\Juan\Desktop\Boom.fxp", "rb").read()
    new_fxp_data = open(r"C:\Users\Juan\Desktop\new_Boom.fxp", "rb").read()

    # Export the contents to .txt files for comparison
    with open(r"C:\Users\Juan\Desktop\original_Boom.txt", "wb") as file:
        file.write(original_fxp_data)

    with open(r"C:\Users\Juan\Desktop\new_Boom.txt", "wb") as file:
        file.write(new_fxp_data)

    # Assert that the contents are the same
    assert original_fxp_data == new_fxp_data, "The original and new FXP files are not identical"

