#!/usr/bin/env python3
"""Build data/references.bib from every OpenAlex id cited in sections/*.tex.

Keys are OpenAlex work ids, looked up in the atlas corpus (cc1/networked_xr/data/processed), so no
citation can be invented: a key absent from the screened, included corpus is reported as an error.
Usage: python3 scripts/make_bib.py [ATLAS_DIR]
"""
import re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ATLAS = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "cc1" / "networked_xr"
sys.path.insert(0, str(ATLAS.parent / "scripts"))
from chunked import read_parquet_parts  # noqa: E402


def tex_escape(s):
    from unidecode import unidecode
    s = unidecode(str(s or ""))
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\^{}")]:
        s = s.replace(a, b)
    return s


def main():
    cited = set()
    for f in sorted((HERE / "sections").glob("*.tex")):
        for m in re.finditer(r"\\cite[pt]?\*?(?:\[[^\]]*\])*\{([^}]*)\}", f.read_text()):
            cited.update(k.strip() for k in m.group(1).split(",") if k.strip())
    ids = {"https://openalex.org/" + k for k in cited}
    df = read_parquet_parts(ATLAS / "data/processed/corpus.parquet",
                            columns=["id", "doi", "title", "year", "venue", "authors", "type"])
    inc = set(read_parquet_parts(ATLAS / "data/processed/included.parquet", columns=["id"]).id)
    df = df[df.id.isin(ids)].drop_duplicates("id")
    out = []
    for r in df.sort_values("id").itertuples():
        key = r.id.rsplit("/", 1)[1]
        al = [a for a in (list(r.authors) if r.authors is not None else []) if a]
        authors = " and ".join(tex_escape(a) for a in al[:6]) + (" and others" if len(al) > 6 else "")
        kind = "inproceedings" if r.type in ("conference-paper", "conference-abstract") else \
               "incollection" if r.type == "book-chapter" else "phdthesis" if r.type == "dissertation" else "article"
        vf = "booktitle" if kind in ("inproceedings", "incollection") else "school" if kind == "phdthesis" else "journal"
        doi = (r.doi if isinstance(r.doi, str) else "").replace("https://doi.org/", "")
        out.append(f"@{kind}{{{key},\n  author = {{{authors or 'Anonymous'}}},\n"
                   f"  title = {{{{{tex_escape(r.title)}}}}},\n  {vf} = {{{tex_escape(r.venue or 'n.p.')}}},\n"
                   f"  year = {{{int(r.year) if r.year == r.year else ''}}},\n"
                   + (f"  doi = {{{doi}}},\n" if doi else "") + "}\n")
    (HERE / "data" / "references.bib").write_text("\n".join(out))
    found = set(df.id)
    missing = sorted(k for k in cited if "https://openalex.org/" + k not in found)
    excluded = sorted(k for k in cited if "https://openalex.org/" + k in found and "https://openalex.org/" + k not in inc)
    print(f"{len(cited)} cited keys; {len(out)} bib entries")
    if missing: print("NOT IN CORPUS (fix these):", " ".join(missing))
    if excluded: print("in corpus but not in the included set (check):", " ".join(excluded))


if __name__ == "__main__":
    main()
