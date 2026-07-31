import gzip
import html
import json
from pathlib import Path

from google.protobuf import json_format

import index_pb2

REPO_DIR = Path.cwd()

PB_FILE = REPO_DIR / "index.pb"
JSON_FILE = REPO_DIR / "index.json"
MIN_JSON_FILE = REPO_DIR / "index.min.json"
HTML_FILE = REPO_DIR / "index.html"

# قراءة index.pb
with gzip.open(PB_FILE, "rb") as f:
    index = index_pb2.Index()
    index.ParseFromString(f.read())

before = len(index.extensionList.extensions)

# حذف إضافات NSFW
filtered = [
    ext
    for ext in index.extensionList.extensions
    if ext.contentWarning != index_pb2.CONTENT_WARNING_NSFW
]

after = len(filtered)

# تحديث القائمة
del index.extensionList.extensions[:]
index.extensionList.extensions.extend(filtered)

# كتابة index.json
with JSON_FILE.open("w", encoding="utf-8") as f:
    f.write(
        json_format.MessageToJson(
            index,
            preserving_proto_field_name=True,
            always_print_fields_with_no_presence=False,
        )
    )

# كتابة index.min.json
with MIN_JSON_FILE.open("w", encoding="utf-8") as f:
    json.dump(
        json.loads(
            json_format.MessageToJson(
                index,
                preserving_proto_field_name=True,
                always_print_fields_with_no_presence=False,
            )
        ),
        f,
        separators=(",", ":"),
        ensure_ascii=False,
    )

# كتابة index.pb
with PB_FILE.open("wb") as f:
    f.write(gzip.compress(index.SerializeToString(deterministic=True)))

# إعادة إنشاء index.html
with HTML_FILE.open("w", encoding="utf-8") as f:
    f.write(
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        '<meta charset="UTF-8">\n'
        "<title>Extensions</title>\n"
        "</head>\n"
        "<body>\n"
        "<pre>\n"
    )

    for ext in index.extensionList.extensions:
        url = html.escape(ext.resources.apkUrl)
        name = html.escape(f"Tachiyomi: {ext.name}")
        f.write(f'<a href="{url}">{name}</a>\n')

    f.write("</pre>\n</body>\n</html>\n")

print(f"Extensions before: {before}")
print(f"Extensions after : {after}")
print(f"Removed          : {before-after}")
