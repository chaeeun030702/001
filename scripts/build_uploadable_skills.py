#!/usr/bin/env python3
"""Package office skills into claude.ai-uploadable .zip files.

Cleans the SKILL.md frontmatter down to the fields the claude.ai custom-skill
uploader accepts (name, description, license) and zips each skill folder.
"""
import os
import re
import shutil
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, ".claude", "skills")
BUILD = os.path.join(REPO, "dist", ".skill-build")
DIST = os.path.join(REPO, "dist", "uploadable-skills")

SKILLS = [
    "resume-tailor", "cover-letter", "job-description", "offer-letter",
    "applicant-screening", "deep-research", "web-search", "academic-search",
    "competitive-analysis", "news-monitor", "image-generation",
    "diagram-creator", "chart-designer", "infographic", "ppt-visual",
    "korean-proofreader",
]


def split_frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("no frontmatter")
    return m.group(1), m.group(2)


def grab(field, fm):
    # match `field: value` (value may be quoted), ignoring comment lines
    m = re.search(r"(?m)^%s:\s*(.+?)\s*$" % re.escape(field), fm)
    if not m:
        return None
    val = m.group(1).strip()
    if (val.startswith('"') and val.endswith('"')) or (
        val.startswith("'") and val.endswith("'")
    ):
        val = val[1:-1]
    return val


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def main():
    shutil.rmtree(BUILD, ignore_errors=True)
    os.makedirs(BUILD)
    os.makedirs(DIST, exist_ok=True)
    # remove previously built zips only; keep README and other files
    for fn in os.listdir(DIST):
        if fn.endswith(".zip"):
            os.remove(os.path.join(DIST, fn))

    for slug in SKILLS:
        src_dir = os.path.join(SRC, slug)
        out_dir = os.path.join(BUILD, slug)
        os.makedirs(out_dir)

        with open(os.path.join(src_dir, "SKILL.md"), encoding="utf-8") as f:
            fm, body = split_frontmatter(f.read())

        name = slug  # force a valid slug that matches the folder
        desc = grab("description", fm) or ""
        license_ = grab("license", fm) or "MIT"

        clean_fm = f'name: {name}\ndescription: "{esc(desc)}"\nlicense: {license_}\n'
        with open(os.path.join(out_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(f"---\n{clean_fm}---\n{body}")

        # copy any supporting files (e.g. README.md, references/)
        for entry in os.listdir(src_dir):
            if entry == "SKILL.md":
                continue
            s = os.path.join(src_dir, entry)
            dst = os.path.join(out_dir, entry)
            if os.path.isdir(s):
                shutil.copytree(s, dst)
            else:
                shutil.copy2(s, dst)

        # zip with the skill folder as the top-level directory inside the archive
        zip_path = os.path.join(DIST, f"{slug}.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(out_dir):
                for fn in files:
                    full = os.path.join(root, fn)
                    arc = os.path.join(slug, os.path.relpath(full, out_dir))
                    z.write(full, arc)
        print(f"built {slug}.zip  (name={name}, desc={len(desc)} chars)")


if __name__ == "__main__":
    main()
