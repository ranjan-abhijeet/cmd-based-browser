# Web Search CLI (`web-search`)

A command-line internet search tool and terminal text browser built in Python. Designed for quick developer searches and article reading directly inside Command Prompt, PowerShell, or any terminal emulator without requiring API keys.

---

## Features

- **No API Keys Needed**: Free internet search powered by DuckDuckGo with automatic fallback.
- **Direct Terminal Command**: Run `web-search <topic>` directly from any command prompt without typing `python main.py` or wrapping queries in quotes.
- **Rich Terminal UI**: Elegant colored cards displaying titles, links, and snippets.
- **In-Terminal Reader Mode**: Enter any result number (`1`, `2`, ...) to parse the webpage into clean, ad-free Markdown and read it right in the terminal.
- **System Browser Integration**: Open any result in your default browser using `:b <number>`.
- **PEP 8 Compliant & Fully Tested**: Type-annotated, structured as a clean package, with unit test coverage.

---

## Installation

### 1. Install Dependencies & Global CLI Command
From the project folder, run:
```powershell
pip install -e .
```
This registers the global command `web-search` (`web-search.exe`) in your Python environment's Scripts folder.

---

## Making `web-search` Globally Accessible

When installing via `pip` on Windows, `web-search.exe` is typically placed in your user Python Scripts folder:
- **Location**: `C:\Users\<YourUsername>\AppData\Roaming\Python\Python313\Scripts` (or `%APPDATA%\Python\Python313\Scripts`)

To run `web-search <topic>` from **any directory** in PowerShell or Command Prompt, ensure this folder is in your Windows `PATH`.

### Option A: One-Liner in PowerShell (Recommended)
Run this command once in PowerShell:
```powershell
[System.Environment]::SetEnvironmentVariable("PATH", [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";$env:APPDATA\Python\Python313\Scripts", "User")
```
> **Note**: Restart your PowerShell / Command Prompt terminal after running this command for the change to take effect in new sessions.

### Option B: Via Command Prompt (`setx`)
Run this command once in Command Prompt:
```cmd
setx PATH "%PATH%;%APPDATA%\Python\Python313\Scripts"
```
> **Note**: Close and reopen Command Prompt after running.

### Option C: Via Windows Settings GUI
1. Press <kbd>Win</kbd> + <kbd>R</kbd>, type `sysdm.cpl`, and hit <kbd>Enter</kbd>.
2. Switch to the **Advanced** tab and click **Environment Variables**.
3. Under **User variables**, select **Path** and click **Edit...**.
4. Click **New** and paste:
   ```text
   %APPDATA%\Python\Python313\Scripts
   ```
5. Click **OK** on all dialogs, then restart your terminal.

### Verification
Open a brand new PowerShell or Command Prompt window anywhere (e.g. `C:\` or your Desktop) and run:
```powershell
web-search quantum computing
```
You should see formatted search results immediately!

---

### 2. (Optional) Development Dependencies
To run tests and linters:
```powershell
pip install -r requirements-dev.txt
```

---

## Usage Examples

### Direct Search (One-Shot or Interactive)
Search any topic with or without quotes:
```powershell
web-search quantum computing
```
or:
```powershell
web-search "python 3.12 release notes"
```

To output results and exit immediately (without launching the interactive prompt):
```powershell
web-search quantum computing --one-shot
```

Customize the number of results (default is 10):
```powershell
web-search artificial intelligence -n 5
```

### Interactive Mode
Launch `web-search` with no arguments to enter interactive mode:
```powershell
web-search
```

### In-Session Commands
While viewing results or in an interactive session:
| Command | Action |
|---|---|
| `<topic>` | Search for a new topic directly (e.g. `fastapi tutorial`) |
| `<number>` | Read that result's full article cleanly formatted in terminal |
| `:b <number>` | Open that result URL in your default desktop web browser |
| `:h` or `:help` | View help and controls menu |
| `:q` or `exit` | Exit the CLI |

---

## Windows Local Launchers

If you prefer not to install globally, you can also run the bundled convenience scripts in the repository:
- **PowerShell**: `.\web-search.ps1 quantum computing`
- **Command Prompt**: `web-search.cmd quantum computing`

---

## Testing & Quality Assurance

Run the automated test suite:
```powershell
pytest tests/ -v
```

Run PEP 8 lint check:
```powershell
flake8 web_search tests
```
