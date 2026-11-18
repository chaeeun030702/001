"""template.html + img/*.jpg -> index.html (이미지를 data URI로 넣은 완전한 HTML 한 파일)."""
import base64
import pathlib
import re

here = pathlib.Path(__file__).parent
html = (here / "template.html").read_text(encoding="utf-8")


def embed(m):
    data = (here / "img" / f"{m.group(1)}.jpg").read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


out = re.sub(r"\{\{IMG_(\w+)\}\}", embed, html)
(here / "index.html").write_text(out, encoding="utf-8")
print("wrote", here / "index.html", len(out), "bytes")
