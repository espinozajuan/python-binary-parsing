import struct
from typing import List, ByteString
from typeguard import typechecked

class FXP:
    @typechecked
    def __init__(self, version: int, fxId: int, fxVersion: int, numPrograms: int, 
                 prgName: str, chunkSize: int, xmlContent: ByteString, wavetables: List[ByteString]):
        assert len(prgName.encode('utf-8')) <= 28, f"Program name must be at most 28 bytes long, but is {len(prgName.encode('utf-8'))} bytes"
        
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
            0,  # Set byteSize to 0 as per previous conclusion
            b'FPCh',
            self.version,
            self.fxId,
            self.fxVersion,
            self.numPrograms,
            self.prgName.encode('utf-8'),
            len(self.xmlContent)
        )

        assert len(fxp_header) == 60, f"FXP header size must be 60 bytes, but is {len(fxp_header)} bytes"

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
            assert len(fxp_header) == 60, f"FXP header size must be 60 bytes, but is {len(fxp_header)} bytes"

            chunkmagic, byteSize, fxMagic, version, fxId, fxVersion, numPrograms, prgName, chunkSize = struct.unpack(
                ">4si4siiii28si", fxp_header)

            xml_content: ByteString = f.read(chunkSize)
            wavetables: ByteString = f.read()

            assert len(prgName.strip(b'\x00')) <= 28, f"Program name must be at most 28 bytes long, but is {len(prgName.strip(b'\x00'))} bytes"

            return FXP(version, fxId, fxVersion, numPrograms, prgName.strip(b'\x00').decode('utf-8'), 
                       chunkSize, xml_content, [wavetables])

if __name__ == "__main__":
    fxp = FXP.load("C:/Users/Juan/Desktop/tuba.fxp")
    fxp.save("C:/Users/Juan/Desktop/new_tuba.fxp")
    assert open("C:/Users/Juan/Desktop/new_tuba.fxp", "rb").read() == open("C:/Users/Juan/Desktop/tuba.fxp", "rb").read()
