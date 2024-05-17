import requests
import base64


class ImageDescrambler:
    IMAGE_DATA_SEPARATOR = b"\x00\x00\x00\x00scramble:"
    MIME_LENGTH = 20
    SUBSTITUTE_MIN_LENGTH = 10000

    @staticmethod
    def descramble_url(url: str, offset: int, to: str) -> None:
        response = requests.get(url)
        response.raise_for_status()
        data = bytearray(response.content)
        descrambled_data = ImageDescrambler.descramble(data, offset)
        with open(to, "wb") as file:
            file.write(base64.b64decode(descrambled_data))

    @staticmethod
    def descramble(data: bytearray, offset: int) -> str:
        offset_position = ImageDescrambler.find_encoded_image_bytes_offset(data)
        print(offset_position)
        if offset_position == 0:
            raise ValueError("Cannot find separator in the image data")
        return ImageDescrambler.decode_image_bytes(data, offset_position, offset)

    @staticmethod
    def decode_image_bytes(data: bytearray, start: int, offset: int) -> str:
        mime_type = "".join(
            [chr(b) for b in data[start : start + ImageDescrambler.MIME_LENGTH] if b > 0]
        )
        from pprint import pprint
        pprint(data[start : start + ImageDescrambler.MIME_LENGTH])
        print("type: {}".format(mime_type))
        scramble_type = data[start + ImageDescrambler.MIME_LENGTH]
        data = data[start + ImageDescrambler.MIME_LENGTH + 1 :]

        if scramble_type == 1:
            data = bytearray((byte - offset) % 256 for byte in data)

        parts = [data[i : i + 5000] for i in range(0, len(data), 5000)]
        combined = b"".join(parts)
        return base64.b64encode(combined).decode("ascii")

    @staticmethod
    def find_encoded_image_bytes_offset(data: bytearray) -> int:
        i = data.find(ImageDescrambler.IMAGE_DATA_SEPARATOR, ImageDescrambler.SUBSTITUTE_MIN_LENGTH)
        if i > 0:
            k = i + len(ImageDescrambler.IMAGE_DATA_SEPARATOR)
            return k
        else:
            return 0

        return i + ImageDescrambler.SUBSTITUTE_MIN_LENGTH
        separator = list(ImageDescrambler.IMAGE_DATA_SEPARATOR)
        first_byte = separator[0]

        for i in range(ImageDescrambler.SUBSTITUTE_MIN_LENGTH, len(data)):
            if data[i] == first_byte:
                if data[i : i + len(separator)] == separator:
                    return i + len(separator)
        return 0
