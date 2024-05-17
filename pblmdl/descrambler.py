from pathlib import Path
import requests
import base64


class ImageDescrambler:
    IMAGE_DATA_SEPARATOR = b"\x00\x00\x00\x00scramble:"
    MIME_LENGTH = 20
    SUBSTITUTE_MIN_LENGTH = 10000

    @staticmethod
    def descramble_url(url: str, offset: int, to: Path) -> None:
        response = requests.get(url)
        response.raise_for_status()
        data = bytearray(response.content)
        ImageDescrambler.descramble(data, offset, to)

    @staticmethod
    def descramble(data: bytearray, offset: int, to: Path) -> None:
        offset_position = ImageDescrambler.find_encoded_image_bytes_offset(data)
        if offset_position == 0:
            print("Cannot find separator in the image data")
            with open(to, "wb") as file:
                file.write(data)
        else:
            ImageDescrambler.decode_image_bytes(data, offset_position, offset, to)

    @staticmethod
    def decode_image_bytes(data: bytearray, start: int, offset: int, to: Path) -> None:
        mime_type = "".join(
            [
                chr(b)
                for b in data[start: start + ImageDescrambler.MIME_LENGTH]
                if b > 0
            ]
        )
        print("type: {}".format(mime_type))
        scramble_type = data[start + ImageDescrambler.MIME_LENGTH]
        data = data[start + ImageDescrambler.MIME_LENGTH + 1:]

        if scramble_type == 1:
            data = bytearray((byte - offset) % 256 for byte in data)

        parts = [data[i: i + 5000] for i in range(0, len(data), 5000)]
        combined = b"".join(parts)

        ext = mime_type.replace("image/", "", 1)
        to = to.with_suffix(".{}".format(ext))
        with open(to, "wb") as file:
            file.write(combined)

    @staticmethod
    def find_encoded_image_bytes_offset(data: bytearray) -> int:
        i = data.find(
            ImageDescrambler.IMAGE_DATA_SEPARATOR,
            ImageDescrambler.SUBSTITUTE_MIN_LENGTH,
        )
        if i > 0:
            k = i + len(ImageDescrambler.IMAGE_DATA_SEPARATOR)
            return k
        else:
            return 0
