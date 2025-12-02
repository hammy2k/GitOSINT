# GitOSINT

GitOSINT is a command-line OSINT tool that extracts email addresses from GitHub commit patches. It can scan a single repository or all repositories belonging to a GitHub user. The tool works by fetching repository lists, commit histories, and `.patch` files, then searching them for email addresses.

---

## Features

- Extracts emails from commit patch files
- Scans a single repository or all repositories of a user
- Optional commit-limit per repository
- Saves results to a file
- Handles GitHub API pagination
- Includes delay logic to avoid rate limits

---

## Requirements

Python 3.7 or newer.

Python packages required:
- `requests`
- `beautifulsoup4`

Install them with:

```bash
pip install requests beautifulsoup4
```

---

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/GitOSINT
cd GitOSINT
```

Make the script executable (optional):

```bash
chmod +x github_email_extractor.py
```

---

## Usage

Run:

```bash
python github_email_extractor.py [options] <target>
```

Where `<target>` is either:
- A GitHub repository URL
- A GitHub username when used with the `--user` flag

### Examples

**Extract from a single repository**

```bash
python github_email_extractor.py https://github.com/google/googletest
```

**Save the results:**

```bash
python github_email_extractor.py https://github.com/blackrock/aladdinsdk -o emails.txt
```

**Limit commit scanning:**

```bash
python github_email_extractor.py https://github.com/user/repo -m 50
```

**Extract from all repositories of a user**

```bash
python github_email_extractor.py torvalds --user
```

**Limit commits and save output:**

```bash
python github_email_extractor.py valvesoftware --user -m 25 -o emails.txt
```

---

## Command Line Options

| Option | Description |
|--------|-------------|
| `-u`, `--user` | Treat target as a username and scan all repositories |
| `-o FILE`, `--output FILE` | Save extracted emails to a file |
| `-m N`, `--max-commits N` | Limit scanning to N commits per repository |
| `-v`, `--verbose` | Enable verbose output |

---

## Output

All discovered emails are printed in sorted order. If `--output` is used, they are also saved to the specified file.

---

## Notes

- This script uses unauthenticated GitHub API requests. For heavy or repeated usage, consider adding token support.
- Delays are included to reduce the likelihood of triggering rate limits.
- Only publicly available commit data can be scanned.

---

## License

Add your preferred licensing information here.
