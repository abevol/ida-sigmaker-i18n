"""Convert .po to .mo binary format using Python only."""
import struct
import sys
import re


def po_to_mo(po_path: str, mo_path: str) -> None:
    with open(po_path, "r", encoding="utf-8") as f:
        text = f.read()

    entries = _parse_po(text)

    num = len(entries)
    header = struct.pack("<IIIIIII", 0x950412DE, 0, num, 28, 28 + num * 8, 0, 0)

    # First pass: compute all orig/trans byte data
    orig_pairs: list[tuple[bytes, bytes]] = []
    total_orig = 0
    total_trans = 0
    for msgid, msgstr in entries:
        ob = msgid.encode("utf-8") + b"\0"
        sb = msgstr.encode("utf-8") + b"\0"
        orig_pairs.append((ob, sb))
        total_orig += len(ob)
        total_trans += len(sb)

    data_start = 28 + num * 8 + num * 8
    orig_tbl = bytearray()
    trans_tbl = bytearray()
    orig_data = bytearray()
    trans_data = bytearray()

    orig_off = 0
    trans_off = 0
    for ob, sb in orig_pairs:
        # Length excludes null terminator (GNU gettext convention)
        orig_tbl += struct.pack("<II", len(ob) - 1, data_start + orig_off)
        orig_data += ob
        orig_off += len(ob)

        trans_tbl += struct.pack("<II", len(sb) - 1, data_start + total_orig + trans_off)
        trans_data += sb
        trans_off += len(sb)

    with open(mo_path, "wb") as f:
        f.write(header)
        f.write(bytes(orig_tbl))
        f.write(bytes(trans_tbl))
        f.write(bytes(orig_data))
        f.write(bytes(trans_data))


def _parse_po(text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    blocks = re.split(r'\n(?=msgid )', text)
    for block in blocks:
        if not block.strip():
            continue
        msgid = _extract_field(block, "msgid")
        msgstr = _extract_field(block, "msgstr")
        if msgid is not None:
            entries.append((msgid, msgstr or ""))
    return entries


def _extract_field(chunk: str, field: str) -> str | None:
    lines = chunk.strip().split("\n")
    parts: list[str] = []
    found = False
    pat = re.compile(r'^' + re.escape(field) + r'\s+"(.*)"\s*$')
    cont_pat = re.compile(r'^"(.*)"\s*$')
    for line in lines:
        m = pat.match(line)
        if m:
            found = True
            parts.append(_unescape(m.group(1)))
            continue
        if found:
            m = cont_pat.match(line)
            if m:
                parts.append(_unescape(m.group(1)))
            else:
                break
    if not found:
        return None
    return "".join(parts)


def _unescape(s: str) -> str:
    return s.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")


if __name__ == "__main__":
    po_path = sys.argv[1]
    mo_path = sys.argv[2] if len(sys.argv) > 2 else po_path.replace(".po", ".mo")
    po_to_mo(po_path, mo_path)
    print(f"Wrote {mo_path}")
