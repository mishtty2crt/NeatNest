# NeatNest — Smart File Cleanup & Duplicate Detective

A beginner-friendly, local-first file organization dashboard built with Python and Streamlit.

## Features

- Scan a selected folder, with optional subfolder scanning
- Categorize files into Images, PDFs, Spreadsheets, Documents, Presentations, Videos, Audio, Archives, Code, and Other
- Preview proposed organization before moving files into category folders
- Detect exact duplicate contents using SHA-256 hashes, even when filenames differ
- Display file sizes, modification dates, largest files, and file-type statistics
- Show hover summaries (15 words maximum) for PDFs, Excel workbooks, Word documents, TXT, Markdown, and CSV
- Search and filter files
- No automatic deletion; duplicate findings are informational
- Local-first: file contents are not uploaded to an external service by this app

## Requirements

- Windows, macOS, or Linux
- Python 3.10 or newer recommended
- VS Code (optional but helpful)

## Run on Windows

1. Install Python from https://www.python.org/downloads/windows/ and VS Code from https://code.visualstudio.com/download.
2. Download or clone this repository.
3. Open the project folder in VS Code.
4. Open **Terminal → New Terminal**.
5. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

6. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt terminal and run:

   ```bat
   .venv\Scripts\activate.bat
   ```

7. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

8. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

9. Streamlit will open a local browser tab. Paste a folder path in the sidebar, for example:

   ```text
   C:\Users\YourName\Downloads
   ```

   Replace `YourName` with your Windows account folder name. Start with a test folder, not your whole drive.

## How to use

1. Enter a folder path in the sidebar and click **Scan folder**.
2. View the overview statistics.
3. Open **Duplicate detective** and click **Find exact duplicates**.
4. Open **File insights** and hover over a supported document card.
5. Open **Organize files**, build a preview, review it, check the confirmation box, then apply the moves.

## Safety notes

- Test using copies of files first.
- The app does not delete duplicates automatically.
- Organization moves files into category folders under the scanned folder. Review the preview before applying.
- File moves may not be reversible from the app in this MVP. Back up important files first.
- PDFs that are scanned images, encrypted documents, and complex spreadsheets may not produce useful summaries.
- Summaries use lightweight offline text selection, not a full semantic AI model. They are capped at 15 words.
- The app reads local files on the machine where Streamlit is running. Do not share screenshots containing private file paths or document contents.

## Project structure

```text
NeatNest/
├── app.py
├── file_helpers.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Future improvements

- Undo support for organization moves
- Image OCR for scanned PDFs
- Smarter semantic summaries
- Drag-and-drop folder selection
- Exportable scan reports
- Automated tests and accessibility improvements

## License

Choose a license before publishing publicly (MIT is a common option for small open-source projects).

## Security model and limitations

NeatNest is a **local desktop-style Streamlit app**. It has no user accounts, admin routes, database, API keys, or application-managed upload endpoint, so authentication/role-based access, database access rules, API spend caps, and per-route rate limiting are not applicable to this version. Do not expose it to the public internet or run it as a shared multi-user service without adding an authentication layer and a deployment security review.

### Security hardening included

- Streamlit binds to `127.0.0.1` through `.streamlit/config.toml`, so it is intended to be reachable only from the same computer.
- Streamlit XSRF protection and CORS protections are enabled; static file serving is disabled; anonymous usage statistics are disabled.
- Folder scans do not follow symbolic links, skip common repository/virtual-environment folders, and stop at 5,000 files.
- Document previews are skipped for files larger than 20 MiB; duplicate hashing skips files larger than 2 GiB.
- File moves revalidate source/destination paths, reject symlinks and out-of-root paths, and refuse to overwrite an existing destination.
- `.gitignore` excludes environment files, Streamlit secrets, and common private key files. This does not remove secrets already committed to Git history.
- User-provided filenames and extracted summaries are HTML-escaped where inserted into custom HTML.

### Before publishing or deploying

1. Review `git status` and inspect every file before committing. Never commit `.env`, `secrets.toml`, private keys, personal documents, or test data. If a secret was ever committed, revoke/rotate it; deleting the file in a later commit is not enough.
2. Run `python -m pip install -r requirements.txt` and periodically update dependencies after checking compatibility. Consider adding a dependency scanner such as `pip-audit` to CI.
3. Run locally only. If deployed remotely, use a maintained HTTPS reverse proxy, authentication/authorization, server-side rate limits, request/resource limits, security headers, logging/monitoring, and a threat model. HTTPS is not configured by this local app; TLS should terminate at the trusted reverse proxy.
4. This app operates with the permissions of the OS account running it. Run it as a normal, non-administrator user and select only the folder you intend to manage.
5. The file-move workflow is not a backup system and has no undo feature. Test with copies and back up important data before applying moves.

Security hardening reduces risk but is not a guarantee that the application is vulnerability-free. Re-audit after significant changes and before any internet-facing deployment.
