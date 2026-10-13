import pypandoc
from pathlib import Path

readme = r"""# Social Lock

**Social Lock** is a desktop productivity app for Linux that helps you protect your attention, plan your day, and build consistent habits.

It combines website blocking with focus timers and everyday planning tools in one Tkinter interface. The goal is simple: make it easier to start focused work and reduce the temptation to open distracting websites.

## Features

- **Social Media Lock** — block selected websites by adding entries to `/etc/hosts`.
- **In-app authentication** — enter your Ubuntu password in a masked dialog when starting a website lock; the password is not intentionally written to a file.
- **Focus timer** — set a lock duration and see the remaining time.
- **Pomodoro timer** — work in focus intervals followed by breaks.
- **To-do list** — organize tasks and track their status and priority.
- **Calendar** — view dates and plan your schedule.
- **Habit tracker** — record progress on habits.
- **Daily notes** — keep short notes and reflections.
- **Dark and light themes** — choose the appearance that works for you.

> Feature availability depends on which modules are present and connected in your local project version.

## Requirements

- Linux (the website-blocking feature is designed for Ubuntu and similar systems)
- Python 3
- Tkinter
- `sudo` access for the Linux account that runs the app
- The project’s Python modules and database setup

On Ubuntu, install Python and Tkinter if they are not already installed:

```bash
sudo apt update
sudo apt install python3 python3-tk
```

The app may use additional Python packages depending on the other modules in your local project. Install any dependencies listed in your project’s requirements file, if one exists.

## Installation

1. Put the project files in one directory, for example:

   ```text
   ~/Desktop/Khana/Todo/
   ```

2. Confirm that the files imported by your main application are in the expected locations. The project may include modules such as:

   ```text
   Todo/
   ├── main.py
   ├── focus_view.py
   ├── focus_lock.py
   ├── todo_view.py
   ├── calendar_view.py
   ├── habits_view.py
   ├── notes_view.py
   └── database.py
   ```

   Your actual main-file name and module layout may differ. Keep the names consistent with your Python imports.

3. Open a terminal in the project directory:

   ```bash
   cd ~/Desktop/Khana/Todo
   ```

4. Check the syntax of the focus modules:

   ```bash
   python3 -m py_compile focus_view.py focus_lock.py
   ```

5. Start the application using your project’s main Python file. For example, if it is named `main.py`:

   ```bash
   python3 main.py
   ```

   Replace `main.py` with the actual filename of your application entry point.

## Using Social Lock

1. Open the **Focus** page.
2. Choose the websites you want to block.
3. Set the lock duration in hours and minutes, or use a duration shortcut.
4. Select **Start Social Lock**.
5. Confirm that you want to start the lock.
6. Enter your Ubuntu account password in the authentication dialog.
7. Confirm that the app reports a successful start and displays the active countdown.

When the timer expires, the app attempts to remove its entries from `/etc/hosts`.

**Test the feature with a short duration first.** Verify that the selected sites are blocked and that they become accessible again after the timer finishes.

## Using the Pomodoro Timer

1. Set a focus duration and a break duration.
2. Select **Start Focus**.
3. Use **Pause** to pause or resume the timer.
4. Select **Reset** to return to the configured focus duration.

Use a realistic work interval and take breaks as needed. The timer is a productivity aid, not a substitute for a sustainable schedule.

## How website blocking works

Social Lock adds a clearly marked section to `/etc/hosts` using these markers:

```text
# SOCIAL_LOCK_START
# SOCIAL_LOCK_END
```

Selected domains are mapped to `127.0.0.1` inside that section. When the session finishes, the app attempts to remove only the section between its markers.

Because `/etc/hosts` is a system file, changing it requires administrator permission. Social Lock uses `sudo` for the privileged update.

### Important limitations

- Website blocking through `/etc/hosts` is a basic local blocking method, not a complete network filter. Apps, alternate domains, DNS-over-HTTPS, VPNs, proxies, or other network configurations may bypass it.
- Browser DNS caches may delay the effect of a change.
- If the app closes, crashes, or the computer shuts down during a session, the blocking entries may remain in `/etc/hosts`. Check the file and remove only the section marked by Social Lock if needed.
- If the timer expires but the app cannot remove its entries, the selected sites may remain blocked until the file is repaired.
- The app must run under a Linux account authorized to use `sudo`.

## Password and system-file safety

- Never commit your Ubuntu password to source control or place it in a configuration file.
- The focus-lock implementation is intended to pass the password to `sudo` through standard input rather than placing it in the command-line arguments.
- The password may remain temporarily in the running application’s memory so the app can attempt to unlock websites when the timer ends.
- Review the code before using it on a machine where system availability is critical.
- Back up `/etc/hosts` before testing system-file changes:

  ```bash
  sudo cp /etc/hosts /etc/hosts.social-lock-backup
  ```

  Keep this backup in a safe location. Restore it only if needed and after reviewing any changes made since the backup.

## Troubleshooting

### The app says the password or authentication failed

- Confirm that you are entering the password for your Ubuntu user account.
- Check that your account is allowed to use `sudo`.
- Run `sudo -v` in a terminal to check whether your account can authenticate. Do not share your password or terminal authentication details.

### The sites are not blocked immediately

- Confirm that the lock started successfully.
- Check whether the chosen domain is covered by the block list.
- Close and reopen the browser or clear its DNS cache if necessary.
- Remember that this method does not block every possible subdomain, alternate domain, or network route.

### The sites remain blocked after the timer ends

- Check whether the app displayed an unlock error.
- Inspect `/etc/hosts` and look for the section between `# SOCIAL_LOCK_START` and `# SOCIAL_LOCK_END`.
- Do not delete unrelated lines from `/etc/hosts`.
- If you are unsure how to repair the file, make a backup and ask for help before editing it.

### Python reports `ModuleNotFoundError`

- Confirm that the missing module exists in your project.
- Check that you launched the app from the correct directory.
- Install the project’s declared dependencies, if available.
- Make sure Python import names match the actual filenames.

### Tkinter is missing

On Ubuntu, install it with:

```bash
sudo apt install python3-tk
```

## Development

Social Lock is built with Python and Tkinter. The application is organized into separate view modules and supporting logic modules, so individual features can be developed and tested independently.

Before contributing a change:

1. Keep the existing theme and layout conventions consistent.
2. Test the affected feature in both dark and light mode.
3. Check Python syntax before launching the app.
4. Test website blocking and unlocking with a short duration.
5. Avoid changing unrelated lines in `/etc/hosts`.
6. Never commit passwords, personal data, database files, or local configuration containing secrets.

## Project status

Social Lock is a personal productivity project under active development. Some features and setup details may differ between local versions. Check the actual source files in your copy of the project for the current implementation.

## License

No license is specified here. Add a `LICENSE` file before distributing the project if you want to clearly define how others may use, modify, and share it.

---

**Built to help make focused work easier, one session at a time.**
"""

out = Path("/mnt/data/README.md")
pypandoc.convert_text(readme, "md", format="md", outputfile=str(out), extra_args=["--standalone"])
print(f"Created {out} ({out.stat().st_size} bytes).")
