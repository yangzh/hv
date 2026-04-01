#!/usr/bin/env python3
"""Extract doc comments from Go and Rust source files into mdBook-ready markdown.

Usage:
    python extract.py --go-src <go_hv_dir> --rust-src <rust_hv_dir> --out <docs_api_dir>

This produces one .md file per type (sparkle.md, set.md, etc.) with both
Go and Rust sections. The output is a *seed* — intended to be curated by hand
before publishing.
"""

import argparse
import os
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FuncDoc:
    name: str
    signature: str
    comment: str
    is_method: bool = False
    receiver: str = ""


@dataclass
class TypeDoc:
    name: str
    comment: str
    funcs: list[FuncDoc] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Go extractor
# ---------------------------------------------------------------------------

def extract_go(src_dir: Path) -> dict[str, TypeDoc]:
    """Extract exported types and their doc comments from Go source files."""
    types: dict[str, TypeDoc] = {}
    standalone: list[FuncDoc] = []

    for path in sorted(src_dir.glob("*.go")):
        if path.name.endswith("_test.go"):
            continue
        lines = path.read_text().splitlines()
        i = 0
        while i < len(lines):
            # Collect comment block
            comment_lines = []
            while i < len(lines) and lines[i].startswith("//"):
                comment_lines.append(lines[i].lstrip("/").strip())
                i += 1

            if i >= len(lines):
                break

            line = lines[i]
            comment = "\n".join(comment_lines).strip()

            # Type declaration: type Foo struct
            m = re.match(r"^type\s+([A-Z]\w+)\s+struct\b", line)
            if m:
                name = m.group(1)
                if name not in types:
                    types[name] = TypeDoc(name=name, comment=comment)
                elif comment and not types[name].comment:
                    types[name].comment = comment
                i += 1
                continue

            # Exported function: func FuncName(...) ...
            m = re.match(r"^func\s+([A-Z]\w+)\s*(\(.*)", line)
            if m:
                fname = m.group(1)
                sig = f"func {fname}{m.group(2).split('{')[0].rstrip()}"
                fd = FuncDoc(name=fname, signature=sig, comment=comment)
                # Try to associate with a type by return type or name prefix
                placed = False
                for tname in types:
                    if fname.startswith("New" + tname) or fname.startswith(tname):
                        types[tname].funcs.append(fd)
                        placed = True
                        break
                if not placed:
                    standalone.append(fd)
                i += 1
                continue

            # Method: func (x Type) MethodName(...) ...
            m = re.match(r"^func\s+\(\w+\s+\*?(\w+)\)\s+([A-Z]\w+)\s*(\(.*)", line)
            if m:
                receiver = m.group(1)
                mname = m.group(2)
                sig = f"func ({receiver}) {mname}{m.group(3).split('{')[0].rstrip()}"
                fd = FuncDoc(
                    name=mname, signature=sig, comment=comment,
                    is_method=True, receiver=receiver,
                )
                if receiver in types:
                    types[receiver].funcs.append(fd)
                i += 1
                continue

            i += 1

    # Attach standalone functions that match type names by return type heuristic
    if standalone:
        if "_standalone" not in types:
            types["_standalone"] = TypeDoc(name="Standalone Functions", comment="")
        types["_standalone"].funcs.extend(standalone)

    return types


# ---------------------------------------------------------------------------
# Rust extractor
# ---------------------------------------------------------------------------

def extract_rust(src_dir: Path) -> dict[str, TypeDoc]:
    """Extract pub types and their doc comments from Rust source files."""
    types: dict[str, TypeDoc] = {}

    for path in sorted(src_dir.glob("*.rs")):
        if "test" in path.name:
            continue
        lines = path.read_text().splitlines()
        i = 0
        while i < len(lines):
            # Collect /// comment block
            comment_lines = []
            while i < len(lines) and lines[i].strip().startswith("///"):
                comment_lines.append(lines[i].strip().lstrip("/").strip())
                i += 1

            # Skip attributes
            while i < len(lines) and lines[i].strip().startswith("#["):
                i += 1

            if i >= len(lines):
                break

            line = lines[i].strip()
            comment = "\n".join(comment_lines).strip()

            # pub struct Foo
            m = re.match(r"^pub\s+struct\s+(\w+)", line)
            if m:
                name = m.group(1)
                if name not in types:
                    types[name] = TypeDoc(name=name, comment=comment)
                elif comment and not types[name].comment:
                    types[name].comment = comment
                i += 1
                continue

            # pub fn name(...) inside an impl block — detect impl context
            m = re.match(r"^pub\s+fn\s+(\w+)\s*(\(.*)", line)
            if m:
                fname = m.group(1)
                sig = f"pub fn {fname}{m.group(2).split('{')[0].rstrip()}"
                fd = FuncDoc(name=fname, signature=sig, comment=comment)

                # Look backward for impl block to find receiver type
                receiver = _find_impl_type(lines, i)
                if receiver and receiver in types:
                    fd.is_method = True
                    fd.receiver = receiver
                    types[receiver].funcs.append(fd)
                elif receiver:
                    fd.is_method = True
                    fd.receiver = receiver
                    if receiver not in types:
                        types[receiver] = TypeDoc(name=receiver, comment="")
                    types[receiver].funcs.append(fd)
                i += 1
                continue

            i += 1

    return types


def _find_impl_type(lines: list[str], idx: int) -> str | None:
    """Walk backward from idx to find the nearest `impl Foo` block."""
    brace_depth = 0
    for j in range(idx - 1, -1, -1):
        line = lines[j].strip()
        brace_depth -= line.count("}")
        brace_depth += line.count("{")
        m = re.match(r"^impl\s+(?:\w+\s+for\s+)?(\w+)", line)
        if m and brace_depth >= 1:
            return m.group(1)
    return None


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------

# Map Go type names to output filenames
TYPE_FILE_MAP = {
    "Sparkle": "sparkle",
    "Set": "set",
    "Sequence": "sequence",
    "Octopus": "octopus",
    "Knot": "knot",
    "Parcel": "parcel",
    "Cyclone": "cyclone",
    "Learner": "learner",
    "SparseOperation": "model",
    "Model": "model",
}

# Map Rust type names to the same output files
RUST_TYPE_MAP = {
    "Sparkle": "sparkle",
    "Set": "set",
    "Sequence": "sequence",
    "Octopus": "octopus",
    "Knot": "knot",
    "Parcel": "parcel",
    "Cyclone": "cyclone",
    "Learner": "learner",
    "SparseOp": "model",
    "Model": "model",
}

OPERATOR_FUNCS = {
    "Bind", "Release", "BindDirect", "Bundle", "BundleSet", "BundleDirect",
    "NewTemplate", "ReplaceSingle", "Replace",
    "Overlap", "Equal", "Inverse",
    # Rust equivalents
    "bind", "bind_direct", "bind_hb", "bundle_direct", "overlap",
}


def render_section(lang: str, types: dict[str, TypeDoc], type_map: dict) -> dict[str, str]:
    """Render extracted types into per-file markdown sections."""
    files: dict[str, str] = {}

    for tname, tdoc in types.items():
        target = type_map.get(tname)
        if not target:
            # Check if any functions are operators
            if tname == "_standalone":
                target = "operators"
            else:
                continue

        content = files.get(target, "")
        content += f"\n## {lang}\n\n"

        if tdoc.comment:
            content += f"{tdoc.comment}\n\n"

        for fd in tdoc.funcs:
            if fd.name in OPERATOR_FUNCS or target == "operators":
                op_content = files.get("operators", "")
                if f"## {lang}" not in op_content:
                    op_content += f"\n## {lang}\n\n"
                op_content += f"### `{fd.signature}`\n\n"
                if fd.comment:
                    op_content += f"{fd.comment}\n\n"
                files["operators"] = op_content
                continue

            content += f"### `{fd.signature}`\n\n"
            if fd.comment:
                content += f"{fd.comment}\n\n"

        files[target] = content

    return files


def write_files(out_dir: Path, go_sections: dict, rust_sections: dict):
    """Write or update markdown files with Go and Rust sections."""
    all_keys = set(go_sections.keys()) | set(rust_sections.keys())

    for key in sorted(all_keys):
        path = out_dir / f"{key}.md"
        title = key.replace("-", " ").title()

        content = f"# {title}\n"
        if key in go_sections:
            content += go_sections[key]
        if key in rust_sections:
            content += rust_sections[key]

        path.write_text(content)
        print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go-src", type=Path, required=True,
                        help="Path to Go hv/ source directory")
    parser.add_argument("--rust-src", type=Path, required=True,
                        help="Path to Rust hv/ source directory")
    parser.add_argument("--out", type=Path, required=True,
                        help="Output directory for API markdown files")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    print("Extracting Go docs...")
    go_types = extract_go(args.go_src)
    print(f"  found {len(go_types)} types, "
          f"{sum(len(t.funcs) for t in go_types.values())} functions")

    print("Extracting Rust docs...")
    rust_types = extract_rust(args.rust_src)
    print(f"  found {len(rust_types)} types, "
          f"{sum(len(t.funcs) for t in rust_types.values())} functions")

    go_sections = render_section("Go", go_types, TYPE_FILE_MAP)
    rust_sections = render_section("Rust", rust_types, RUST_TYPE_MAP)

    print("Writing markdown files...")
    write_files(args.out, go_sections, rust_sections)
    print("Done. Review and curate the generated files before publishing.")


if __name__ == "__main__":
    main()
