from pathlib import Path
from datetime import datetime
import hashlib
import html
import shutil
import os
import streamlit as st
import streamlit.components.v1 as components

from file_helpers import (
    classify_file, format_bytes, get_file_summary, sha256_file,
    scan_folder, SAFE_CATEGORIES
)

st.set_page_config(
    page_title="NeatNest | Smart File Cleanup",
    page_icon=":material/folder:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Friendly, high-contrast styling with responsive cards and accessible controls.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,500,0,0&display=swap');
:root { --navy:#030164; --indigo:#363199; --blue:#2D7495; --yellow:#E8E085; --paper:#fffef6; --ink:#030164; --muted:#363199; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
.stApp { background:#fffef6; color:var(--ink); }
h1,h2,h3,h4 { font-family:'Manrope',sans-serif !important; color:var(--navy) !important; letter-spacing:-.025em; }
p, li, label, .stMarkdown, [data-testid="stCaptionContainer"] { color:var(--ink); }
.block-container { padding-top:1.8rem; max-width:1450px; }
/* Sidebar: deliberately light yellow with dark navy text for reliable contrast. */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
  background:var(--yellow) !important;
  border-right:3px solid var(--indigo) !important;
}
[data-testid="stSidebar"], [data-testid="stSidebar"] * {
  color:var(--navy) !important;
  opacity:1 !important;
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color:var(--navy) !important;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="input"] {
  background:#fffef6 !important;
  color:var(--navy) !important;
  -webkit-text-fill-color:var(--navy) !important;
  border:2px solid var(--indigo) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  background:transparent !important;
  color:var(--navy) !important;
  border-radius:8px;
  padding:4px 7px;
}
[data-testid="stSidebar"] [data-testid="stCheckbox"] label,
[data-testid="stSidebar"] [data-testid="stCheckbox"] label p {
  color:var(--navy) !important;
}
.hero { padding:1.5rem 1.7rem; border-radius:20px; color:#fff; background:linear-gradient(115deg,var(--navy),var(--indigo) 60%,var(--blue)); border:2px solid var(--yellow); box-shadow:0 12px 30px #03016420; margin-bottom:1rem; }
.hero h1 { color:#fff !important; font-size:2.4rem; margin:0; }
.hero p { color:#fff !important; font-size:1.02rem; margin:.45rem 0 0; }
.metric-card { background:#fffef6; border:2px solid #d8d5a0; border-radius:16px; padding:1rem 1.1rem; box-shadow:0 4px 14px #0301640c; min-height:110px; }
.metric-label { color:var(--indigo); font-size:.88rem; font-weight:700; }
.metric-value { color:var(--navy); font-family:'Manrope',sans-serif; font-size:1.8rem; font-weight:800; margin-top:.25rem; }
.metric-icon { color:var(--blue); font-family:"Material Symbols Rounded"; font-size:1.25rem; vertical-align:middle; }
.file-card { border:1px solid #d8d5a0; background:#fffef6; border-radius:13px; padding:13px 14px; margin:7px 0; }
.file-name { font-weight:700; color:var(--navy); overflow-wrap:anywhere; }
.file-meta { color:#4e4d70; font-size:12px; margin-top:4px; }
div[data-testid="stButton"] button, .stDownloadButton button { border-radius:10px; font-weight:700; min-height:2.6rem; border:1px solid var(--indigo); }
div[data-testid="stButton"] button[kind="primary"] { background:var(--indigo); color:#fff; border:2px solid var(--yellow); }
div[data-testid="stButton"] button[kind="primary"]:hover { background:var(--blue); color:#fff; }
.stDownloadButton button { background:var(--indigo); color:#fff; }
div[data-testid="stAlert"] { border-radius:12px; }
[data-testid="stExpander"] { background:#fffef6; border:1px solid #d8d5a0; border-radius:12px; }
.stProgress > div > div { background:var(--blue); }
/* Keep native panels readable regardless of Streamlit's theme defaults. */
[data-testid="stAlert"], [data-testid="stExpander"] summary, [data-testid="stExpander"] details,
[data-testid="stDataFrame"], [data-testid="stTable"] { color:var(--navy) !important; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input, [data-testid="stSelectbox"] [data-baseweb="select"] {
  color:var(--navy) !important; background:#fffef6 !important; border-color:var(--blue) !important;
}
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] p { color:var(--ink) !important; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color:#030164 !important; }
*:focus-visible { outline:3px solid var(--yellow) !important; outline-offset:2px !important; }
.stApp a { color:var(--blue) !important; }

.small-note { color:var(--muted); font-size:.88rem; }
code { color:var(--navy) !important; background:#f0efcf !important; }
</style>
""", unsafe_allow_html=True)

if "scan_results" not in st.session_state:
    st.session_state.scan_results = []
if "last_scanned_path" not in st.session_state:
    st.session_state.last_scanned_path = ""
if "summaries" not in st.session_state:
    st.session_state.summaries = {}
if "duplicate_hashes" not in st.session_state:
    st.session_state.duplicate_hashes = {}

def safe_mtime(path):
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).strftime("%d %b %Y, %I:%M %p")
    except OSError:
        return "Unknown"

def get_summary_cached(path_string):
    if path_string not in st.session_state.summaries:
        st.session_state.summaries[path_string] = get_file_summary(Path(path_string))
    return st.session_state.summaries[path_string]

def metric_card(icon, label, value, hint=""):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label"><span class="metric-icon">{html.escape(icon)}</span> &nbsp;{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(str(value))}</div>'
        f'<div class="small-note">{html.escape(hint)}</div></div>',
        unsafe_allow_html=True
    )

with st.sidebar:
    st.markdown("## :material/folder_open: NeatNest")
    st.caption("Your friendly file cleanup assistant")
    page = st.radio(
        "Navigate",
        ["Overview", "Organize files", "Duplicate detective", "File insights", "Safety & help"],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("### :material/folder: Choose a folder")
    folder_input = st.text_input(
        "Folder path on this computer",
        placeholder=r"C:\Users\YourName\Downloads",
        help="Paste the full path of the folder you want to scan. Start with a test folder."
    )
    include_subfolders = st.checkbox("Include subfolders", value=True)
    scan_clicked = st.button(":material/search: Scan folder", type="primary", use_container_width=True)
    st.caption("Tip: test with a folder containing copies of a few files first.")

if scan_clicked:
    # Local-only guard: never accept remote clients by accident.
    # Also cap scans in file_helpers.py and do not follow symlinks.
    if not folder_input.strip():
        st.error("Enter a folder path first.")
    else:
        raw_path = folder_input.strip().strip('"')
        try:
            chosen = Path(raw_path).expanduser().resolve(strict=True)
        except (OSError, RuntimeError):
            chosen = None
        if chosen is None or not chosen.is_dir():
            st.error("That folder could not be found or accessed. Check the path and try again.")
        else:
            with st.spinner("Scanning files and calculating file details…"):
                results, errors = scan_folder(chosen, recursive=include_subfolders)
                st.session_state.scan_results = results
                st.session_state.last_scanned_path = str(chosen)
                st.session_state.duplicate_hashes = {}
                st.session_state.summaries = {}
            st.success(f"Scan complete — found {len(results)} files.")
            if errors:
                st.warning(f"{len(errors)} item(s) could not be read. They were skipped.")

results = st.session_state.scan_results
scanned_path = st.session_state.last_scanned_path

st.markdown("""
<div class="hero">
  <h1>NeatNest </h1>
  <p>Less clutter, more clarity. Organize files, spot duplicates, and understand documents at a glance.</p>
</div>
""", unsafe_allow_html=True)

if page == "Overview":
    st.subheader("Your folder at a glance")
    if not results:
        st.info("Welcome! Enter a folder path in the left sidebar, then select **Scan folder** to get started.")
        st.markdown("#### What NeatNest can do")
        a,b,c = st.columns(3)
        with a:
            st.markdown("### :material/cleaning_services: Smart sorting")
            st.write("Preview how files can be grouped into clear, useful categories.")
        with b:
            st.markdown("### :material/content_copy: Duplicate detective")
            st.write("Find identical file contents, even when filenames are different.")
        with c:
            st.markdown("### :material/lightbulb: Quick insights")
            st.write("Hover over supported documents to see a short content summary.")
    else:
        total_size = sum(item["size"] for item in results)
        categories = {}
        for item in results:
            categories[item["category"]] = categories.get(item["category"], 0) + 1
        duplicate_count = sum(1 for item in results if item.get("duplicate"))
        c1,c2,c3,c4 = st.columns(4)
        with c1: metric_card("description","Files scanned",len(results),"Files in selected folder")
        with c2: metric_card("storage","Total size",format_bytes(total_size),"Combined file size")
        with c3: metric_card("fingerprint","Duplicate files",duplicate_count,"After content-hash scan")
        with c4: metric_card("category","File categories",len(categories),"Types of files detected")
        st.markdown("")
        left,right = st.columns([1.1,1])
        with left:
            st.markdown("### File types")
            for category,count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                st.write(f"**{category}** · {count} file(s)")
                st.progress(count / max(len(results),1))
        with right:
            st.markdown("### Largest files")
            largest = sorted(results, key=lambda x:x["size"], reverse=True)[:6]
            for item in largest:
                st.markdown(
                    f'<div class="file-card"><div class="file-name">{html.escape(item["name"])}</div>'
                    f'<div class="file-meta">{html.escape(item["category"])} · {format_bytes(item["size"])}</div></div>',
                    unsafe_allow_html=True
                )
        st.caption(f"Scanned folder: `{scanned_path}`")

elif page == "Organize files":
    st.subheader(":material/cleaning_services: Organize files")
    st.write("Review the proposed categories first. NeatNest never moves files until you press the apply button.")
    if not results:
        st.info("Scan a folder from the sidebar to see organization suggestions.")
    else:
        category_options = ["All"] + sorted({item["category"] for item in results})
        selected_category = st.selectbox("Filter by category", category_options)
        query = st.text_input("Search filenames", placeholder="e.g. report, holiday, invoice")
        filtered = [item for item in results if (selected_category == "All" or item["category"] == selected_category) and query.lower() in item["name"].lower()]
        st.caption(f"Showing {len(filtered)} of {len(results)} files")
        for item in filtered[:250]:
            st.markdown(
                f'<div class="file-card"><div class="file-name">{html.escape(item["name"])}</div>'
                f'<div class="file-meta">:material/folder: {html.escape(item["category"])} &nbsp;·&nbsp; {format_bytes(item["size"])} &nbsp;·&nbsp; Modified {html.escape(item["modified"])}</div></div>',
                unsafe_allow_html=True
            )
        if len(filtered) > 250:
            st.caption("Only the first 250 matching files are shown in this list.")
        st.divider()
        st.markdown("#### Preview organization")
        st.write("Files will be moved into category folders inside the folder you scanned.")
        if st.button("Build organization preview"):
            preview = []
            root = Path(scanned_path)
            for item in results:
                src = Path(item["path"])
                target = root / item["category"] / src.name
                if src.parent != target.parent:
                    if target.exists():
                        target = root / item["category"] / f"{src.stem}_organized{src.suffix}"
                    preview.append((src, target))
            st.session_state["organization_preview"] = [(str(a),str(b)) for a,b in preview]
        preview = st.session_state.get("organization_preview", [])
        if preview:
            st.info(f"{len(preview)} file(s) would be moved. Review a sample below.")
            for src,dst in preview[:12]:
                st.code(f"{Path(src).name}  →  {Path(dst).parent.name}/{Path(dst).name}", language="text")
            if len(preview) > 12:
                st.caption(f"…and {len(preview)-12} more.")
            confirm = st.checkbox("I reviewed the preview and want to move these files.")
            if st.button("Apply organization", type="primary", disabled=not confirm):
                moved, failed = 0, []
                root = Path(scanned_path)
                for src_s,dst_s in preview:
                    src, dst = Path(src_s), Path(dst_s)
                    try:
                        # Revalidate all paths at action time; session state is not trusted as authorization.
                        root_real = root.resolve(strict=True)
                        src_real = src.resolve(strict=True)
                        dst_parent_real = dst.parent.resolve(strict=False)
                        if src.is_symlink() or not src_real.is_relative_to(root_real):
                            failed.append(f"{src.name}: source is outside the selected folder or is a link")
                            continue
                        if dst.parent.name not in SAFE_CATEGORIES and dst.parent.name != "Other":
                            failed.append(f"{src.name}: invalid destination category")
                            continue
                        if not dst_parent_real.is_relative_to(root_real):
                            failed.append(f"{src.name}: destination is outside the selected folder")
                            continue
                        if not src_real.is_file() or src_real == dst_parent_real:
                            failed.append(f"{src.name}: source is not a regular file")
                            continue
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        # Recheck after mkdir to prevent overwrites and avoid moving a file onto itself.
                        if dst.exists() or dst.is_symlink():
                            failed.append(f"{src.name}: destination already exists")
                            continue
                        if src_real == dst.resolve(strict=False):
                            continue
                        shutil.move(str(src_real), str(dst))
                        moved += 1
                    except (OSError, RuntimeError, ValueError):
                        failed.append(f"{src.name}: could not safely move this file")
                st.success(f"Moved {moved} file(s). Please scan the folder again to refresh the dashboard.")
                if failed:
                    st.warning(f"{len(failed)} file(s) could not be moved. First issue: {failed[0]}")
                st.session_state.organization_preview = []

elif page == "Duplicate detective":
    st.subheader(":material/content_copy: Duplicate detective")
    st.write("Files are considered duplicates only when their contents match exactly. NeatNest does not delete anything automatically.")
    if not results:
        st.info("Scan a folder first.")
    else:
        if st.button("Find exact duplicates", type="primary"):
            groups = {}
            errors = 0
            progress = st.progress(0)
            for idx,item in enumerate(results):
                try:
                    candidate = Path(item["path"])
                    root_real = Path(scanned_path).resolve(strict=True)
                    candidate_real = candidate.resolve(strict=True)
                    if candidate.is_symlink() or not candidate_real.is_relative_to(root_real):
                        errors += 1
                        continue
                    if candidate_real.stat().st_size > 2 * 1024 * 1024 * 1024:
                        errors += 1
                        continue
                    digest = sha256_file(candidate_real)
                    groups.setdefault(digest, []).append(item)
                except (OSError, RuntimeError, ValueError):
                    errors += 1
                progress.progress((idx+1)/max(len(results),1))
            duplicates = {digest:items for digest,items in groups.items() if len(items)>1}
            st.session_state.duplicate_hashes = duplicates
            st.session_state.duplicate_scan_done = True
            progress.empty()
            if errors:
                st.warning(f"Could not hash {errors} file(s).")
        if st.session_state.get("duplicate_scan_done"):
            duplicates = st.session_state.duplicate_hashes
            duplicate_files = sum(len(group)-1 for group in duplicates.values())
            reclaimable = sum(item["size"] for group in duplicates.values() for item in group[1:])
            c1,c2,c3 = st.columns(3)
            with c1: metric_card("library_books","Duplicate groups",len(duplicates),"Groups with identical contents")
            with c2: metric_card("description","Extra copies",duplicate_files,"Copies beyond one per group")
            with c3: metric_card("savings","Potential savings",format_bytes(reclaimable),"If extra copies are removed")
            if not duplicates:
                st.success("No exact duplicate files found in this scan.")
            else:
                st.warning("For safety, this MVP identifies duplicates but does not delete them. Check each group before removing copies.")
                for n,(digest,group) in enumerate(duplicates.items(), start=1):
                    with st.expander(f"Duplicate group {n} · {len(group)} matching files · {format_bytes(group[0]['size'])} each"):
                        st.caption(f"SHA-256: {digest}")
                        for item in group:
                            st.markdown(f"- **{item['name']}** — `{item['path']}`")
                        st.caption("Suggestion: keep one copy and review the others in File Explorer before deleting.")
        else:
            st.info("Select **Find exact duplicates** to compare file contents. Large folders may take a little time.")

elif page == "File insights":
    st.subheader(":material/lightbulb: File insights")
    st.write("Hover over a file card to preview a short summary. PDF, Excel, Word, and text documents are supported.")
    if not results:
        st.info("Scan a folder first.")
    else:
        query = st.text_input("Find a file", placeholder="Search by filename")
        supported = [item for item in results if Path(item["path"]).suffix.lower() in {".pdf",".xlsx",".xlsm",".xltx",".xltm",".docx",".txt",".md",".csv"}]
        filtered = [item for item in supported if query.lower() in item["name"].lower()]
        st.caption(f"{len(filtered)} supported document(s) match")
        if not filtered:
            st.info("No supported documents found. Try PDF, XLSX, DOCX, TXT, Markdown, or CSV files.")
        for item in filtered[:100]:
            summary = get_summary_cached(item["path"])
            summary_safe = html.escape(summary)
            name_safe = html.escape(item["name"])
            ext = Path(item["path"]).suffix.lower().lstrip(".").upper() or "FILE"
            card_html = f"""
            <div style="font-family:Arial,sans-serif;position:relative;margin:7px 0;">
              <div class="ff-card" tabindex="0" aria-label="{name_safe}. Hover or focus for file summary."
                   style="position:relative;display:flex;align-items:center;gap:13px;background:#fffef6;border:2px solid #2D7495;border-radius:15px;padding:14px 16px;cursor:help;outline:2px solid transparent;outline-offset:3px;">
                <div style="width:43px;height:43px;border-radius:12px;background:#E8E085;color:#030164;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:11px;">{html.escape(ext[:4])}</div>
                <div style="flex:1;min-width:0;">
                  <div style="font-weight:700;color:#030164;overflow-wrap:anywhere;">{name_safe}</div>
                  <div style="font-size:12px;color:#363199;margin-top:4px;">{format_bytes(item['size'])} · Modified {html.escape(item['modified'])}</div>
                </div>
                <div style="color:#030164;font-size:12px;font-weight:700;">Hover for insight</div>
                <div class="ff-tooltip" role="tooltip"
                  style="visibility:hidden;opacity:0;position:absolute;z-index:99;left:8px;right:8px;top:4px;padding:10px 12px;background:#030164;color:#ffffff;border:2px solid #E8E085;border-radius:12px;box-shadow:0 10px 28px #03016433;transition:opacity .15s;pointer-events:none;">
                  <div style="font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:#E8E085;font-weight:700;margin-bottom:6px;">QUICK FILE INSIGHT · MAX 15 WORDS</div>
                  <div style="font-size:14px;line-height:1.5;">{summary_safe}</div>
                </div>
              </div>
            </div>
            <style>
              .ff-card:hover .ff-tooltip,.ff-card:focus .ff-tooltip,.ff-card:focus-within .ff-tooltip {{visibility:visible!important;opacity:1!important;}}
            </style>
            """
            components.html(card_html, height=82, scrolling=False)

elif page == "Safety & help":
    st.subheader(":material/shield: Safety, privacy & help")
    st.markdown("""
**Your files stay local.** NeatNest scans the folder on the computer where the Python app is running.

- **No automatic deletion:** duplicate detection only reports matches.
- **Preview before moving:** review the organization plan and confirm before any files move.
- **Start small:** test with a temporary folder containing copies of sample files.
- **Encrypted files and scanned documents:** text extraction may not work for password-protected PDFs, image-only scans, or unsupported file formats.
- **Excel summaries:** based on visible cell values and sheet/column information; complex workbooks may need a deeper parser.
- **15-word rule:** summaries are trimmed to at most 15 words.
- **Privacy:** don't scan folders containing sensitive material when sharing screenshots or screen recordings.
""")
    st.markdown("### Suggested test")
    st.code("Create a test folder → copy 5–10 harmless files into it → scan the test folder → review duplicates → preview organization.", language="text")
    st.markdown("### Common fixes")
    st.markdown("""
- If a folder path fails, use the full Windows path, for example `C:\\Users\\YourName\\Downloads`.
- If a package is missing, activate your virtual environment and run `pip install -r requirements.txt`.
- If the dashboard looks stale after moving files, scan the folder again.
""")

st.markdown("---")
st.caption("NeatNest · Built with Python and Streamlit · Local-first file cleanup")
