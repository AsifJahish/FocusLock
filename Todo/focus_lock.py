# #!/usr/bin/env python3

# import os
# import subprocess
# import getpass
# import time
# from datetime import datetime, timedelta

# try:
#     from database import save_focus_session
# except ImportError:
#     save_focus_session = None


# # ============================================================
# # CONFIGURATION
# # ============================================================

# HOSTS_FILE = "/etc/hosts"

# BLOCK_IP = "127.0.0.1"

# START_MARKER = "# SOCIAL_LOCK_START"
# END_MARKER = "# SOCIAL_LOCK_END"

# WEBSITES = {
#     "Facebook": [
#         "facebook.com",
#         "www.facebook.com",
#         "m.facebook.com",
#     ],
#     "Instagram": [
#         "instagram.com",
#         "www.instagram.com",
#     ],
#     "TikTok": [
#         "tiktok.com",
#         "www.tiktok.com",
#     ],
#     "Reddit": [
#         "reddit.com",
#         "www.reddit.com",
#         "old.reddit.com",
#     ],
#     "YouTube": [
#         "youtube.com",
#         "www.youtube.com",
#         "m.youtube.com",
#     ],
# }


# # ============================================================
# # ROOT COMMAND
# # ============================================================

# def run_as_root(command):

#     try:

#         result = subprocess.run(
#             [
#                 "sudo",
#                 "-S"
#             ] + command,
#             input="",
#             text=True,
#             capture_output=True
#         )

#         return result.returncode == 0

#     except Exception:

#         return False


# # ============================================================
# # CHECK ROOT ACCESS
# # ============================================================

# def check_sudo():

#     try:

#         result = subprocess.run(
#             [
#                 "sudo",
#                 "-n",
#                 "true"
#             ],
#             capture_output=True,
#             text=True
#         )

#         return result.returncode == 0

#     except Exception:

#         return False


# # ============================================================
# # READ HOSTS FILE
# # ============================================================

# def get_hosts():

#     try:

#         with open(
#             HOSTS_FILE,
#             "r",
#             encoding="utf-8"
#         ) as file:

#             return file.read()

#     except Exception:

#         return ""


# # ============================================================
# # REMOVE OLD SOCIAL LOCK BLOCK
# # ============================================================

# def remove_block_from_text(text):

#     start_index = text.find(
#         START_MARKER
#     )

#     end_index = text.find(
#         END_MARKER
#     )

#     if (
#         start_index == -1
#         or end_index == -1
#     ):

#         return text

#     end_index += len(END_MARKER)

#     new_text = (
#         text[:start_index]
#         + text[end_index:]
#     )

#     return new_text.strip() + "\n"


# # ============================================================
# # CREATE BLOCK
# # ============================================================

# def create_block(selected_sites):

#     lines = [
#         "",
#         START_MARKER
#     ]

#     for site_name in selected_sites:

#         domains = WEBSITES.get(
#             site_name,
#             []
#         )

#         for domain in domains:

#             lines.append(
#                 f"{BLOCK_IP} {domain}"
#             )

#     lines.append(
#         END_MARKER
#     )

#     return "\n".join(lines) + "\n"


# # ============================================================
# # BLOCK WEBSITES
# # ============================================================

# def block_sites(selected_sites):

#     if not selected_sites:

#         return False, "No websites selected."

#     hosts = get_hosts()

#     if not hosts:

#         return False, "Could not read /etc/hosts."

#     hosts = remove_block_from_text(
#         hosts
#     )

#     block = create_block(
#         selected_sites
#     )

#     new_hosts = (
#         hosts.rstrip()
#         + "\n"
#         + block
#     )

#     temporary_file = (
#         "/tmp/social_lock_hosts"
#     )

#     try:

#         with open(
#             temporary_file,
#             "w",
#             encoding="utf-8"
#         ) as file:

#             file.write(new_hosts)

#         result = subprocess.run(
#             [
#                 "sudo",
#                 "cp",
#                 temporary_file,
#                 HOSTS_FILE
#             ],
#             capture_output=True,
#             text=True
#         )

#         try:
#             os.remove(temporary_file)
#         except OSError:
#             pass

#         if result.returncode != 0:

#             return (
#                 False,
#                 result.stderr.strip()
#                 or "Permission denied."
#             )

#         flush_dns()

#         return True, "Websites blocked successfully."

#     except Exception as error:

#         try:
#             os.remove(temporary_file)
#         except OSError:
#             pass

#         return False, str(error)


# # ============================================================
# # REMOVE BLOCK
# # ============================================================

# def remove_block():

#     hosts = get_hosts()

#     if not hosts:

#         return False, "Could not read /etc/hosts."

#     new_hosts = remove_block_from_text(
#         hosts
#     )

#     temporary_file = (
#         "/tmp/social_lock_hosts"
#     )

#     try:

#         with open(
#             temporary_file,
#             "w",
#             encoding="utf-8"
#         ) as file:

#             file.write(new_hosts)

#         result = subprocess.run(
#             [
#                 "sudo",
#                 "cp",
#                 temporary_file,
#                 HOSTS_FILE
#             ],
#             capture_output=True,
#             text=True
#         )

#         try:
#             os.remove(temporary_file)
#         except OSError:
#             pass

#         if result.returncode != 0:

#             return (
#                 False,
#                 result.stderr.strip()
#                 or "Permission denied."
#             )

#         flush_dns()

#         return True, "Website blocking removed."

#     except Exception as error:

#         try:
#             os.remove(temporary_file)
#         except OSError:
#             pass

#         return False, str(error)


# # ============================================================
# # DNS FLUSH
# # ============================================================

# def flush_dns():

#     commands = [
#         [
#             "sudo",
#             "resolvectl",
#             "flush-caches"
#         ],
#         [
#             "sudo",
#             "systemctl",
#             "restart",
#             "NetworkManager"
#         ]
#     ]

#     for command in commands:

#         try:

#             subprocess.run(
#                 command,
#                 capture_output=True,
#                 text=True,
#                 timeout=10
#             )

#         except Exception:

#             pass

#         if command[1] == "resolvectl":
#             break


# # ============================================================
# # FOCUS SESSION
# # ============================================================

# class FocusLock:

#     def __init__(
#         self,
#         selected_sites,
#         duration_minutes
#     ):

#         self.selected_sites = (
#             selected_sites
#         )

#         self.duration_minutes = (
#             duration_minutes
#         )

#         self.start_time = None

#         self.end_time = None

#         self.running = False

#     # --------------------------------------------------------
#     # START
#     # --------------------------------------------------------

#     def start(self):

#         success, message = block_sites(
#             self.selected_sites
#         )

#         if not success:

#             return False, message

#         self.start_time = datetime.now()

#         self.end_time = (
#             self.start_time
#             + timedelta(
#                 minutes=self.duration_minutes
#             )
#         )

#         self.running = True

#         return True, "Focus session started."

#     # --------------------------------------------------------
#     # CHECK
#     # --------------------------------------------------------

#     def is_finished(self):

#         if not self.running:

#             return True

#         return datetime.now() >= self.end_time

#     # --------------------------------------------------------
#     # REMAINING SECONDS
#     # --------------------------------------------------------

#     def remaining_seconds(self):

#         if not self.running:

#             return 0

#         remaining = (
#             self.end_time
#             - datetime.now()
#         ).total_seconds()

#         return max(
#             0,
#             int(remaining)
#         )

#     # --------------------------------------------------------
#     # STOP
#     # --------------------------------------------------------

#     def stop(self):

#         success, message = remove_block()

#         if not success:

#             return False, message

#         self.running = False

#         actual_end = datetime.now()

#         actual_duration = int(
#             (
#                 actual_end
#                 - self.start_time
#             ).total_seconds()
#             / 60
#         ) if self.start_time else 0

#         if save_focus_session:

#             try:

#                 save_focus_session(
#                     self.start_time,
#                     actual_end,
#                     self.selected_sites,
#                     actual_duration
#                 )

#             except Exception:

#                 pass

#         return True, "Focus session ended."

#     # --------------------------------------------------------
#     # AUTOMATIC FINISH
#     # --------------------------------------------------------

#     def update(self):

#         if not self.running:

#             return False

#         if self.is_finished():

#             self.stop()

#             return True

#         return False


# # ============================================================
# # HELPER FUNCTIONS
# # ============================================================

# def format_time(seconds):

#     seconds = max(
#         0,
#         int(seconds)
#     )

#     hours = seconds // 3600

#     minutes = (
#         seconds % 3600
#     ) // 60

#     secs = seconds % 60

#     if hours > 0:

#         return (
#             f"{hours:02d}:"
#             f"{minutes:02d}:"
#             f"{secs:02d}"
#         )

#     return (
#         f"{minutes:02d}:"
#         f"{secs:02d}"
#     )


# def get_available_websites():

#     return list(
#         WEBSITES.keys()
#     )


# # ============================================================
# # TEST
# # ============================================================

# if __name__ == "__main__":

#     print("Social Lock Focus Engine")
#     print()
#     print("Available websites:")

#     for website in get_available_websites():

#         print(
#             f" - {website}"
#         )

#     print()

#     print(
#         "Focus lock module loaded successfully."
#     )


#!/usr/bin/env python3
"""Linux website blocking engine for Social Lock; uses an in-app supplied sudo password."""

import os
import subprocess
import tempfile
from datetime import datetime, timedelta

try:
    from database import save_focus_session
except ImportError:
    save_focus_session = None

HOSTS_FILE = "/etc/hosts"
BLOCK_IP = "127.0.0.1"
START_MARKER = "# SOCIAL_LOCK_START"
END_MARKER = "# SOCIAL_LOCK_END"

WEBSITES = {
    "Facebook": ["facebook.com", "www.facebook.com", "m.facebook.com"],
    "Instagram": ["instagram.com", "www.instagram.com"],
    "TikTok": ["tiktok.com", "www.tiktok.com"],
    "Reddit": ["reddit.com", "www.reddit.com", "old.reddit.com"],
    "YouTube": ["youtube.com", "www.youtube.com", "m.youtube.com"],
}


def run_sudo(command, password, timeout=20):
    """Run a single sudo command; password is passed on stdin, never in argv."""
    try:
        result = subprocess.run(
            ["sudo", "-S", "-p", ""] + command,
            input=password + "\n",
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            error = result.stderr.strip() or "Administrator authentication or command failed."
            if "sorry, try again" in error.lower() or "incorrect password" in error.lower():
                error = "Incorrect Ubuntu password or sudo authentication failed."
            return False, error
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "The administrator command timed out."
    except OSError as exc:
        return False, str(exc)


def get_hosts():
    try:
        with open(HOSTS_FILE, "r", encoding="utf-8") as file:
            return file.read(), None
    except OSError as exc:
        return None, str(exc)


def remove_block_from_text(text):
    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if start == -1 and end == -1:
        return text
    if start == -1 or end == -1 or end < start:
        raise ValueError("Social Lock markers in /etc/hosts are incomplete. Please inspect the file.")
    end += len(END_MARKER)
    return (text[:start] + text[end:]).rstrip() + "\n"


def create_block(selected_sites):
    lines = ["", START_MARKER]
    for site in selected_sites:
        for domain in WEBSITES.get(site, []):
            lines.append(f"{BLOCK_IP} {domain}")
    lines.append(END_MARKER)
    return "\n".join(lines) + "\n"


def write_hosts(text, password):
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", prefix="social_lock_", delete=False
        ) as file:
            file.write(text)
            temp_path = file.name
        success, message = run_sudo(
            ["install", "-o", "root", "-g", "root", "-m", "644", temp_path, HOSTS_FILE],
            password,
        )
        if not success:
            return False, message
        flush_dns()
        return True, "Updated /etc/hosts."
    except OSError as exc:
        return False, str(exc)
    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except OSError:
                pass


def flush_dns():
    # Best effort: /etc/hosts takes effect without restarting NetworkManager.
    try:
        subprocess.run(["resolvectl", "flush-caches"], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        pass


def block_sites(selected_sites, password):
    if not selected_sites:
        return False, "No websites selected."
    invalid = [site for site in selected_sites if site not in WEBSITES]
    if invalid:
        return False, "Unknown website selection: " + ", ".join(invalid)
    hosts, error = get_hosts()
    if hosts is None:
        return False, error
    try:
        hosts = remove_block_from_text(hosts)
    except ValueError as exc:
        return False, str(exc)
    new_hosts = hosts.rstrip() + "\n" + create_block(selected_sites)
    return write_hosts(new_hosts, password)


def remove_block(password):
    hosts, error = get_hosts()
    if hosts is None:
        return False, error
    try:
        new_hosts = remove_block_from_text(hosts)
    except ValueError as exc:
        return False, str(exc)
    if new_hosts == hosts:
        return True, "No Social Lock block was present."
    return write_hosts(new_hosts, password)


class FocusLock:
    def __init__(self, selected_sites, duration_minutes, password):
        self.selected_sites = list(selected_sites)
        self.duration_minutes = int(duration_minutes)
        self._password = password
        self.start_time = None
        self.end_time = None
        self.running = False

    def start(self):
        success, message = block_sites(self.selected_sites, self._password)
        if not success:
            self._password = None
            return False, message
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=self.duration_minutes)
        self.running = True
        return True, "Focus session started."

    def is_finished(self):
        return not self.running or datetime.now() >= self.end_time

    def remaining_seconds(self):
        if not self.running:
            return 0
        return max(0, int((self.end_time - datetime.now()).total_seconds()))

    def stop(self):
        success, message = remove_block(self._password)
        if not success:
            return False, message
        self.running = False
        actual_end = datetime.now()
        actual_duration = int((actual_end - self.start_time).total_seconds() / 60) if self.start_time else 0
        if save_focus_session:
            try:
                save_focus_session(self.start_time, actual_end, self.selected_sites, actual_duration)
            except Exception:
                pass
        self._password = None
        return True, "Focus session ended."


def format_time(seconds):
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


def get_available_websites():
    return list(WEBSITES.keys())


if __name__ == "__main__":
    print("Social Lock Focus Engine")
    print("Available websites:")
    for website in get_available_websites():
        print(f" - {website}")
    print("Focus lock module loaded successfully.")
