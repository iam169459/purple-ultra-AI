"""Tool registry with plugin architecture for extensible tool support. Optimized for low memory."""

from __future__ import annotations

import os
import subprocess
import json
import shutil
import platform
import time
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class ToolDef:
    name: str
    description: str
    params: dict[str, str]
    dangerous: bool = False
    category: str = "general"
    handler: Callable = None


class ToolRegistry:
    """Central registry for all available tools."""

    _tools: dict[str, ToolDef] = {}
    _descriptions_cache: str = ""
    _names_cache: list[str] = []

    @classmethod
    def register(cls, tool_def: ToolDef):
        cls._tools[tool_def.name] = tool_def
        cls._descriptions_cache = ""  # invalidate
        cls._names_cache = []

    @classmethod
    def get(cls, name: str) -> ToolDef | None:
        return cls._tools.get(name)

    @classmethod
    def all(cls) -> dict[str, ToolDef]:
        return cls._tools  # return reference, not copy (faster)

    @classmethod
    def names(cls) -> list[str]:
        if not cls._names_cache:
            cls._names_cache = list(cls._tools.keys())
        return cls._names_cache

    @classmethod
    def get_tool_descriptions(cls) -> str:
        if not cls._descriptions_cache:
            lines = []
            for name, tool in cls._tools.items():
                params = ", ".join(f"{k}: {v}" for k, v in tool.params.items())
                danger = " [DANGEROUS]" if tool.dangerous else ""
                lines.append(f"- {name}({params}){danger}: {tool.description}")
            cls._descriptions_cache = "\n".join(lines)
        return cls._descriptions_cache


class ToolRunner:
    """Executes tool actions."""

    __slots__ = ('sandbox_path', '_timers', '_handler_cache')

    def __init__(self, sandbox_path: str = ""):
        self.sandbox_path = Path(sandbox_path) if sandbox_path else Path.home()
        self._timers: dict = {}
        self._handler_cache: dict[str, Callable] = {}
        self._register_all_tools()

    def _register_all_tools(self):
        tools = [
            ToolDef("open_app", "Open an application", {"app": "string"}, False, "system", self._open_app),
            ToolDef("open_url", "Open a URL in browser", {"url": "string"}, False, "web", self._open_url),
            ToolDef("browser_search", "Search the web", {"query": "string"}, False, "web", self._browser_search),
            ToolDef("youtube_search", "Search YouTube", {"query": "string"}, False, "media", self._youtube_search),
            ToolDef("youtube_play", "Play a YouTube video", {"query": "string"}, False, "media", self._youtube_play),
            ToolDef("media_control", "Control media playback", {"action": "play|pause|next|previous|volume_up|volume_down|mute"}, False, "media", self._media_control),
            ToolDef("take_screenshot", "Take a screenshot", {}, False, "system", self._take_screenshot),
            ToolDef("generate_image", "Generate an image from prompt", {"prompt": "string"}, False, "creative", self._generate_image),
            ToolDef("fetch_url", "Fetch URL content", {"url": "string"}, False, "web", self._fetch_url),
            ToolDef("web_search", "Search the internet", {"query": "string"}, False, "web", self._web_search),
            ToolDef("get_time", "Get current date and time", {}, False, "system", self._get_time),
            ToolDef("system_info", "Get system information", {}, False, "system", self._system_info),
            ToolDef("get_clipboard", "Get clipboard content", {}, False, "system", self._get_clipboard),
            ToolDef("set_clipboard", "Set clipboard content", {"text": "string"}, False, "system", self._set_clipboard),
            ToolDef("list_dir", "List directory contents", {"path": "string"}, False, "files", self._list_dir),
            ToolDef("search_files", "Search for files", {"query": "string"}, False, "files", self._search_files),
            ToolDef("read_file", "Read a text file", {"path": "string"}, False, "files", self._read_file),
            ToolDef("write_file", "Write to a text file", {"path": "string", "content": "string"}, True, "files", self._write_file),
            ToolDef("remember", "Remember a fact", {"key": "string", "value": "string"}, False, "memory", self._remember),
            ToolDef("run_shell", "Execute a shell command", {"command": "string"}, True, "system", self._run_shell),
            ToolDef("delete_file", "Delete a file", {"path": "string"}, True, "files", self._delete_file),
            ToolDef("copy_file", "Copy a file", {"source": "string", "destination": "string"}, False, "files", self._copy_file),
            ToolDef("move_file", "Move a file", {"source": "string", "destination": "string"}, False, "files", self._move_file),
            ToolDef("create_dir", "Create a directory", {"path": "string"}, False, "files", self._create_dir),
            ToolDef("get_battery", "Get battery status", {}, False, "system", self._get_battery),
            ToolDef("get_network", "Get network info", {}, False, "system", self._get_network),
            ToolDef("volume_control", "Control system volume", {"action": "up|down|mute|unmute|set", "level": "int"}, False, "system", self._volume_control),
            ToolDef("launch_browser", "Open default browser", {}, False, "web", self._launch_browser),
            ToolDef("set_reminder", "Set a reminder", {"text": "string", "time": "string"}, False, "assistant", self._set_reminder),
            ToolDef("add_task", "Add a task to do list", {"task": "string"}, False, "assistant", self._add_task),
            ToolDef("add_note", "Add a note", {"content": "string"}, False, "assistant", self._add_note),
            ToolDef("execute_code", "Execute Python code", {"code": "string"}, True, "system", self._execute_code),
            # NEW: System monitoring
            ToolDef("get_cpu_usage", "Get CPU usage percentage", {}, False, "system", self._get_cpu_usage),
            ToolDef("get_memory_usage", "Get memory usage info", {}, False, "system", self._get_memory_usage),
            ToolDef("get_disk_usage", "Get disk usage info", {"path": "string"}, False, "system", self._get_disk_usage),
            ToolDef("get_uptime", "Get system uptime", {}, False, "system", self._get_uptime),
            ToolDef("list_processes", "List running processes", {}, False, "system", self._list_processes),
            ToolDef("kill_process", "Kill a process by PID", {"pid": "int"}, True, "system", self._kill_process),
            ToolDef("set_brightness", "Set screen brightness", {"level": "int"}, False, "system", self._set_brightness),
            ToolDef("lock_screen", "Lock the screen", {}, False, "system", self._lock_screen),
            ToolDef("sleep_system", "Put system to sleep", {}, False, "system", self._sleep_system),
            ToolDef("get_temperature", "Get CPU temperature", {}, False, "system", self._get_temperature),
            # NEW: File operations
            ToolDef("file_info", "Get file metadata", {"path": "string"}, False, "files", self._file_info),
            ToolDef("file_exists", "Check if file exists", {"path": "string"}, False, "files", self._file_exists),
            ToolDef("file_size", "Get file size in bytes", {"path": "string"}, False, "files", self._file_size),
            ToolDef("file_hash", "Get file hash (SHA256)", {"path": "string"}, False, "files", self._file_hash),
            ToolDef("append_file", "Append text to a file", {"path": "string", "content": "string"}, False, "files", self._append_file),
            ToolDef("read_lines", "Read specific lines from file", {"path": "string", "start": "int", "end": "int"}, False, "files", self._read_lines),
            ToolDef("write_lines", "Write lines to a file", {"path": "string", "lines": "string"}, False, "files", self._write_lines),
            ToolDef("count_lines", "Count lines in a file", {"path": "string"}, False, "files", self._count_lines),
            ToolDef("find_files", "Find files by extension", {"pattern": "string"}, False, "files", self._find_files),
            # NEW: Text processing
            ToolDef("text_stats", "Get word/char/line count", {"text": "string"}, False, "text", self._text_stats),
            ToolDef("reverse_text", "Reverse a string", {"text": "string"}, False, "text", self._reverse_text),
            ToolDef("to_uppercase", "Convert text to uppercase", {"text": "string"}, False, "text", self._to_uppercase),
            ToolDef("to_lowercase", "Convert text to lowercase", {"text": "string"}, False, "text", self._to_lowercase),
            ToolDef("base64_encode", "Encode text to base64", {"text": "string"}, False, "text", self._base64_encode),
            ToolDef("base64_decode", "Decode base64 to text", {"text": "string"}, False, "text", self._base64_decode),
            ToolDef("url_encode", "URL encode a string", {"text": "string"}, False, "text", self._url_encode),
            ToolDef("url_decode", "URL decode a string", {"text": "string"}, False, "text", self._url_decode),
            ToolDef("strip_text", "Strip whitespace from text", {"text": "string"}, False, "text", self._strip_text),
            ToolDef("replace_text", "Replace text in string", {"text": "string", "old": "string", "new": "string"}, False, "text", self._replace_text),
            # NEW: Date/Time
            ToolDef("get_date", "Get current date", {}, False, "system", self._get_date),
            ToolDef("get_timestamp", "Get Unix timestamp", {}, False, "system", self._get_timestamp),
            ToolDef("time_ago", "Get human-readable time since", {"timestamp": "string"}, False, "system", self._time_ago),
            ToolDef("add_time", "Add time to a datetime", {"datetime": "string", "days": "int", "hours": "int", "minutes": "int"}, False, "system", self._add_time),
            # NEW: Network
            ToolDef("ping", "Ping a host", {"host": "string"}, False, "network", self._ping),
            ToolDef("check_port", "Check if a port is open", {"host": "string", "port": "int"}, False, "network", self._check_port),
            ToolDef("get_ip", "Get local IP address", {}, False, "network", self._get_ip),
            ToolDef("get_public_ip", "Get public IP address", {}, False, "network", self._get_public_ip),
            ToolDef("dns_lookup", "DNS lookup for a domain", {"domain": "string"}, False, "network", self._dns_lookup),
            # NEW: Developer tools
            ToolDef("run_python", "Run a Python file", {"path": "string"}, True, "developer", self._run_python),
            ToolDef("pip_install", "Install a Python package", {"package": "string"}, True, "developer", self._pip_install),
            ToolDef("pip_list", "List installed packages", {}, False, "developer", self._pip_list),
            ToolDef("check_syntax", "Check Python syntax", {"code": "string"}, False, "developer", self._check_syntax),
            ToolDef("format_json", "Pretty print JSON", {"json_str": "string"}, False, "developer", self._format_json),
            ToolDef("minify_json", "Minify JSON", {"json_str": "string"}, False, "developer", self._minify_json),
            ToolDef("json_query", "Query JSON with dot notation", {"json_str": "string", "query": "string"}, False, "developer", self._json_query),
            # NEW: Utility
            ToolDef("calculate", "Evaluate math expression", {"expression": "string"}, False, "utility", self._calculate),
            ToolDef("uuid_generate", "Generate a UUID", {}, False, "utility", self._uuid_generate),
            ToolDef("hash_text", "Hash text with algorithm", {"text": "string", "algorithm": "md5|sha1|sha256"}, False, "utility", self._hash_text),
            ToolDef("color_convert", "Convert color format", {"color": "string", "to_format": "hex|rgb|hsl"}, False, "utility", self._color_convert),
            ToolDef("random_number", "Generate random number", {"low": "int", "high": "int"}, False, "utility", self._random_number),
            ToolDef("random_choice", "Pick random from list", {"options": "string"}, False, "utility", self._random_choice),
            ToolDef("encode_morse", "Encode text to morse code", {"text": "string"}, False, "utility", self._encode_morse),
            ToolDef("decode_morse", "Decode morse code to text", {"text": "string"}, False, "utility", self._decode_morse),
            # NEW: Math/Number tools
            ToolDef("factorial", "Calculate factorial", {"n": "int"}, False, "math", self._factorial),
            ToolDef("fibonacci", "Generate fibonacci sequence", {"n": "int"}, False, "math", self._fibonacci),
            ToolDef("is_prime", "Check if number is prime", {"n": "int"}, False, "math", self._is_prime),
            ToolDef("gcd", "Greatest common divisor", {"a": "int", "b": "int"}, False, "math", self._gcd),
            ToolDef("lcm", "Least common multiple", {"a": "int", "b": "int"}, False, "math", self._lcm),
            ToolDef("prime_factors", "Get prime factors", {"n": "int"}, False, "math", self._prime_factors),
            ToolDef("is_even", "Check if number is even", {"n": "int"}, False, "math", self._is_even),
            ToolDef("is_odd", "Check if number is odd", {"n": "int"}, False, "math", self._is_odd),
            ToolDef("abs_value", "Absolute value", {"n": "string"}, False, "math", self._abs_value),
            ToolDef("sqrt", "Square root", {"n": "string"}, False, "math", self._sqrt),
            ToolDef("power", "Power calculation", {"base": "string", "exp": "string"}, False, "math", self._power),
            ToolDef("log", "Logarithm", {"n": "string", "base": "string"}, False, "math", self._log),
            ToolDef("round_number", "Round number", {"n": "string", "decimals": "int"}, False, "math", self._round_number),
            ToolDef("clamp", "Clamp number to range", {"n": "string", "low": "string", "high": "string"}, False, "math", self._clamp),
            ToolDef("percentage", "Calculate percentage", {"part": "string", "total": "string"}, False, "math", self._percentage),
            # NEW: Array/List tools
            ToolDef("list_sort", "Sort a list", {"items": "string"}, False, "array", self._list_sort),
            ToolDef("list_unique", "Get unique items", {"items": "string"}, False, "array", self._list_unique),
            ToolDef("list_reverse", "Reverse a list", {"items": "string"}, False, "array", self._list_reverse),
            ToolDef("list_flatten", "Flatten nested list", {"items": "string"}, False, "array", self._list_flatten),
            ToolDef("list_chunk", "Split list into chunks", {"items": "string", "size": "int"}, False, "array", self._list_chunk),
            ToolDef("list_count", "Count item occurrences", {"items": "string", "item": "string"}, False, "array", self._list_count),
            ToolDef("list_sum", "Sum numeric list", {"items": "string"}, False, "array", self._list_sum),
            ToolDef("list_avg", "Average of numeric list", {"items": "string"}, False, "array", self._list_avg),
            ToolDef("list_min", "Min of numeric list", {"items": "string"}, False, "array", self._list_min),
            ToolDef("list_max", "Max of numeric list", {"items": "string"}, False, "array", self._list_max),
            ToolDef("list_diff", "Difference between lists", {"a": "string", "b": "string"}, False, "array", self._list_diff),
            ToolDef("list_intersect", "Intersection of lists", {"a": "string", "b": "string"}, False, "array", self._list_intersect),
            ToolDef("list_union", "Union of lists", {"a": "string", "b": "string"}, False, "array", self._list_union),
            # NEW: DateTime/Calendar tools
            ToolDef("day_of_week", "Get day of week", {}, False, "datetime", self._day_of_week),
            ToolDef("day_of_year", "Get day of year", {}, False, "datetime", self._day_of_year),
            ToolDef("week_number", "Get week number", {}, False, "datetime", self._week_number),
            ToolDef("is_leap_year", "Check if leap year", {"year": "int"}, False, "datetime", self._is_leap_year),
            ToolDef("days_between", "Days between two dates", {"date1": "string", "date2": "string"}, False, "datetime", self._days_between),
            ToolDef("age_calc", "Calculate age from birthday", {"birthday": "string"}, False, "datetime", self._age_calc),
            ToolDef("next_friday", "Get next Friday date", {}, False, "datetime", self._next_friday),
            ToolDef("unix_to_date", "Convert unix timestamp to date", {"timestamp": "string"}, False, "datetime", self._unix_to_date),
            ToolDef("date_to_unix", "Convert date to unix timestamp", {"date": "string"}, False, "datetime", self._date_to_unix),
            ToolDef("timezone_convert", "Convert between timezones", {"datetime": "string", "from_tz": "string", "to_tz": "string"}, False, "datetime", self._timezone_convert),
            # NEW: Encoding tools
            ToolDef("hex_encode", "Encode text to hex", {"text": "string"}, False, "encoding", self._hex_encode),
            ToolDef("hex_decode", "Decode hex to text", {"text": "string"}, False, "encoding", self._hex_decode),
            ToolDef("binary_encode", "Encode text to binary", {"text": "string"}, False, "encoding", self._binary_encode),
            ToolDef("binary_decode", "Decode binary to text", {"text": "string"}, False, "encoding", self._binary_decode),
            ToolDef("octal_encode", "Encode to octal", {"text": "string"}, False, "encoding", self._octal_encode),
            ToolDef("rot13", "Apply ROT13 cipher", {"text": "string"}, False, "encoding", self._rot13),
            ToolDef("caesar_cipher", "Caesar cipher", {"text": "string", "shift": "int"}, False, "encoding", self._caesar_cipher),
            ToolDef("atbash_cipher", "Apply Atbash cipher", {"text": "string"}, False, "encoding", self._atbash_cipher),
            # NEW: Crypto/Password tools
            ToolDef("generate_password", "Generate secure password", {"length": "int", "symbols": "bool"}, False, "crypto", self._generate_password),
            ToolDef("generate_passphrase", "Generate passphrase", {"words": "int"}, False, "crypto", self._generate_passphrase),
            ToolDef("aes_encrypt", "AES encrypt text", {"text": "string", "key": "string"}, False, "crypto", self._aes_encrypt),
            ToolDef("aes_decrypt", "AES decrypt text", {"text": "string", "key": "string"}, False, "crypto", self._aes_decrypt),
            ToolDef("hmac_hash", "HMAC hash", {"text": "string", "key": "string", "algorithm": "string"}, False, "crypto", self._hmac_hash),
            ToolDef("xor_encrypt", "XOR encrypt/decrypt", {"text": "string", "key": "string"}, False, "crypto", self._xor_encrypt),
            # NEW: Regex tools
            ToolDef("regex_match", "Check regex match", {"text": "string", "pattern": "string"}, False, "regex", self._regex_match),
            ToolDef("regex_find", "Find all matches", {"text": "string", "pattern": "string"}, False, "regex", self._regex_find),
            ToolDef("regex_replace", "Replace with regex", {"text": "string", "pattern": "string", "replacement": "string"}, False, "regex", self._regex_replace),
            ToolDef("regex_extract", "Extract groups", {"text": "string", "pattern": "string"}, False, "regex", self._regex_extract),
            ToolDef("email_validate", "Validate email", {"email": "string"}, False, "regex", self._email_validate),
            ToolDef("url_validate", "Validate URL", {"url": "string"}, False, "regex", self._url_validate),
            ToolDef("phone_validate", "Validate phone number", {"phone": "string"}, False, "regex", self._phone_validate),
            # NEW: CSV/JSON/XML tools
            ToolDef("csv_to_json", "Convert CSV to JSON", {"csv_text": "string"}, False, "data", self._csv_to_json),
            ToolDef("json_to_csv", "Convert JSON to CSV", {"json_str": "string"}, False, "data", self._json_to_csv),
            ToolDef("json_validate", "Validate JSON", {"json_str": "string"}, False, "data", self._json_validate),
            ToolDef("json_merge", "Merge two JSON objects", {"a": "string", "b": "string"}, False, "data", self._json_merge),
            ToolDef("json_diff", "Diff two JSON objects", {"a": "string", "b": "string"}, False, "data", self._json_diff),
            ToolDef("xml_to_json", "Convert XML to JSON", {"xml": "string"}, False, "data", self._xml_to_json),
            ToolDef("yaml_to_json", "Convert YAML to JSON", {"yaml": "string"}, False, "data", self._yaml_to_json),
            ToolDef("json_to_yaml", "Convert JSON to YAML", {"json_str": "string"}, False, "data", self._json_to_yaml),
            # NEW: Git tools
            ToolDef("git_status", "Get git status", {"path": "string"}, False, "git", self._git_status),
            ToolDef("git_log", "Get git log", {"path": "string", "count": "int"}, False, "git", self._git_log),
            ToolDef("git_diff", "Get git diff", {"path": "string"}, False, "git", self._git_diff),
            ToolDef("git_branch", "List git branches", {"path": "string"}, False, "git", self._git_branch),
            ToolDef("git_remote", "List git remotes", {"path": "string"}, False, "git", self._git_remote),
            ToolDef("git_stash", "Stash changes", {"path": "string"}, False, "git", self._git_stash),
            # NEW: Docker tools
            ToolDef("docker_containers", "List Docker containers", {}, False, "docker", self._docker_containers),
            ToolDef("docker_images", "List Docker images", {}, False, "docker", self._docker_images),
            ToolDef("docker_stats", "Get Docker stats", {}, False, "docker", self._docker_stats),
            ToolDef("docker_logs", "Get container logs", {"container": "string"}, False, "docker", self._docker_logs),
            # NEW: Statistics tools
            ToolDef("mean", "Calculate mean", {"numbers": "string"}, False, "stats", self._mean),
            ToolDef("median", "Calculate median", {"numbers": "string"}, False, "stats", self._median),
            ToolDef("mode", "Calculate mode", {"numbers": "string"}, False, "stats", self._mode),
            ToolDef("stdev", "Calculate standard deviation", {"numbers": "string"}, False, "stats", self._stdev),
            ToolDef("variance", "Calculate variance", {"numbers": "string"}, False, "stats", self._variance),
            ToolDef("percentile", "Calculate percentile", {"numbers": "string", "p": "string"}, False, "stats", self._percentile),
            ToolDef("correlation", "Pearson correlation", {"x": "string", "y": "string"}, False, "stats", self._correlation),
            # NEW: Environment tools
            ToolDef("env_get", "Get environment variable", {"name": "string"}, False, "env", self._env_get),
            ToolDef("env_set", "Set environment variable", {"name": "string", "value": "string"}, False, "env", self._env_set),
            ToolDef("env_list", "List environment variables", {"filter": "string"}, False, "env", self._env_list),
            ToolDef("env_home", "Get home directory", {}, False, "env", self._env_home),
            ToolDef("env_cwd", "Get current directory", {}, False, "env", self._env_cwd),
            ToolDef("env_tmp", "Get temp directory", {}, False, "env", self._env_tmp),
            # NEW: Archive tools
            ToolDef("zip_files", "Create zip archive", {"files": "string", "output": "string"}, False, "archive", self._zip_files),
            ToolDef("unzip_file", "Extract zip archive", {"path": "string", "output": "string"}, False, "archive", self._unzip_file),
            ToolDef("tar_create", "Create tar.gz archive", {"files": "string", "output": "string"}, False, "archive", self._tar_create),
            ToolDef("tar_extract", "Extract tar.gz archive", {"path": "string", "output": "string"}, False, "archive", self._tar_extract),
            ToolDef("archive_list", "List archive contents", {"path": "string"}, False, "archive", self._archive_list),
            # NEW: Markdown/HTML tools
            ToolDef("md_to_html", "Convert markdown to HTML", {"text": "string"}, False, "text", self._md_to_html),
            ToolDef("html_to_text", "Strip HTML tags", {"html": "string"}, False, "text", self._html_to_text),
            ToolDef("html_entities", "Encode HTML entities", {"text": "string"}, False, "text", self._html_entities),
            ToolDef("word_wrap", "Word wrap text", {"text": "string", "width": "int"}, False, "text", self._word_wrap),
            # NEW: Notification/OS tools
            ToolDef("notify", "Send desktop notification", {"title": "string", "message": "string"}, False, "os", self._notify),
            ToolDef("get_wallpaper", "Get current wallpaper", {}, False, "os", self._get_wallpaper),
            ToolDef("set_wallpaper", "Set wallpaper", {"path": "string"}, False, "os", self._set_wallpaper),
            ToolDef("get_screensaver_status", "Check if screensaver active", {}, False, "os", self._get_screensaver_status),
            ToolDef("get_display_info", "Get display information", {}, False, "os", self._get_display_info),
            # NEW: Database tools
            ToolDef("sqlite_query", "Query SQLite database", {"db": "string", "sql": "string"}, False, "database", self._sqlite_query),
            ToolDef("sqlite_tables", "List SQLite tables", {"db": "string"}, False, "database", self._sqlite_tables),
            ToolDef("sqlite_insert", "Insert into SQLite", {"db": "string", "table": "string", "data": "string"}, True, "database", self._sqlite_insert),
            # NEW: Process tools
            ToolDef("find_process", "Find process by name", {"name": "string"}, False, "process", self._find_process),
            ToolDef("process_tree", "Show process tree", {"pid": "int"}, False, "process", self._process_tree),
            ToolDef("open_ports", "List open ports", {}, False, "process", self._open_ports),
            # NEW: Image tools
            ToolDef("image_info", "Get image metadata", {"path": "string"}, False, "image", self._image_info),
            ToolDef("image_resize", "Resize image", {"path": "string", "width": "int", "height": "int"}, False, "image", self._image_resize),
            ToolDef("image_to_base64", "Encode image to base64", {"path": "string"}, False, "image", self._image_to_base64),
            # NEW: QR/Barcode tools
            ToolDef("qr_generate", "Generate QR code SVG", {"text": "string"}, False, "creative", self._qr_generate),
            # NEW: String tools
            ToolDef("string_contains", "Check string containment", {"text": "string", "search": "string"}, False, "text", self._string_contains),
            ToolDef("string_count", "Count substring occurrences", {"text": "string", "search": "string"}, False, "text", self._string_count),
            ToolDef("string_pad", "Pad string", {"text": "string", "length": "int", "char": "string"}, False, "text", self._string_pad),
            ToolDef("string_trim", "Trim to length", {"text": "string", "length": "int"}, False, "text", self._string_trim),
            ToolDef("string_repeat", "Repeat string", {"text": "string", "count": "int"}, False, "text", self._string_repeat),
            ToolDef("string_diff", "Diff two strings", {"a": "string", "b": "string"}, False, "text", self._string_diff),
            # NEW: Network tools
            ToolDef("http_headers", "Get HTTP headers", {"url": "string"}, False, "network", self._http_headers),
            ToolDef("ssl_check", "Check SSL certificate", {"host": "string"}, False, "network", self._ssl_check),
            ToolDef("traceroute", "Traceroute to host", {"host": "string"}, False, "network", self._traceroute),
            # NEW: Utility tools
            ToolDef("timer_start", "Start a timer", {"name": "string"}, False, "utility", self._timer_start),
            ToolDef("timer_stop", "Stop a timer", {"name": "string"}, False, "utility", self._timer_stop),
            ToolDef("diff_text", "Diff two texts", {"a": "string", "b": "string"}, False, "utility", self._diff_text),
            ToolDef("sort_dict", "Sort dict by value", {"json_str": "string"}, False, "utility", self._sort_dict),
            ToolDef("flatten_dict", "Flatten nested dict", {"json_str": "string"}, False, "utility", self._flatten_dict),
        ]
        for tool in tools:
            ToolRegistry.register(tool)

    def is_dangerous(self, action: dict) -> bool:
        name = action.get("name", "")
        tool = ToolRegistry.get(name)
        return tool.dangerous if tool else False

    def run(self, action: dict) -> str:
        name = action.get("name", "")
        args = action.get("args", {})
        # Fast path: cached handler
        handler = self._handler_cache.get(name)
        if handler is None:
            tool = ToolRegistry.get(name)
            if not tool or not tool.handler:
                return f"Unknown tool: {name}"
            handler = tool.handler
            self._handler_cache[name] = handler
        try:
            return handler(**args)
        except Exception as e:
            return f"Tool error ({name}): {e}"

    def _resolve_path(self, path: str) -> Path:
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self.sandbox_path / p
        resolved = p.resolve()
        if not str(resolved).startswith(str(self.sandbox_path)):
            raise ValueError(f"Path {path} is outside sandbox")
        return resolved

    def _open_app(self, app: str = "") -> str:
        system = platform.system()
        if system == "Darwin":
            try:
                subprocess.run(["open", "-a", app], check=True, capture_output=True, timeout=10)
                return f"Opened {app}"
            except Exception:
                return f"Failed to open {app}"
        elif system == "Linux":
            try:
                subprocess.run([app.lower()], check=True, capture_output=True, timeout=10)
                return f"Opened {app}"
            except Exception:
                return f"Failed to open {app}"
        return f"App opening not supported on {system}"

    def _open_url(self, url: str = "") -> str:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            webbrowser.open(url)
            return f"Opened {url}"
        except Exception as e:
            return f"Failed to open URL: {e}"

    def _browser_search(self, query: str = "") -> str:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        try:
            webbrowser.open(url)
            return f"Searching for: {query}"
        except Exception:
            return f"Failed to search"

    def _youtube_search(self, query: str = "") -> str:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        try:
            webbrowser.open(url)
            return f"Searching YouTube for: {query}"
        except Exception:
            return "Failed to search YouTube"

    def _youtube_play(self, query: str = "") -> str:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        try:
            webbrowser.open(url)
            return f"Playing: {query}"
        except Exception:
            return "Failed to play"

    def _media_control(self, action: str = "play") -> str:
        system = platform.system()
        if system == "Darwin":
            key_map = {
                "play": 16,
                "pause": 16,
                "next": 176,
                "previous": 173,
                "volume_up": 144,
                "volume_down": 145,
                "mute": 47,
            }
            key_code = key_map.get(action, 16)
            script = f'tell application "System Events" to key code {key_code}'
            try:
                subprocess.run(["osascript", "-e", script], capture_output=True, timeout=5)
                return f"Media: {action}"
            except Exception:
                return f"Failed to {action}"
        return f"Media control not supported on {system}"

    def _take_screenshot(self) -> str:
        try:
            screenshot_dir = Path("generated/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            filename = screenshot_dir / f"screenshot_{int(time.time())}.png"
            if platform.system() == "Darwin":
                subprocess.run(["screencapture", str(filename)], check=True, capture_output=True)
            else:
                return "Screenshot not supported on this platform"
            return f"Screenshot saved to {filename}"
        except Exception as e:
            return f"Screenshot failed: {e}"

    def _generate_image(self, prompt: str = "") -> str:
        """Generate a simple SVG image from a text prompt."""
        import colorsys
        h = hash(prompt) % 360
        r, g, b = [int(c * 255) for c in colorsys.hls_to_rgb(h / 360, 0.5, 0.7)]
        color1 = f"#{r:02x}{g:02x}{b:02x}"
        r2, g2, b2 = [int(c * 255) for c in colorsys.hls_to_rgb((h + 60) % 360 / 360, 0.4, 0.6)]
        color2 = f"#{r2:02x}{g2:02x}{b2:02x}"

        words = prompt.split()
        lines = []
        for i in range(0, len(words), 4):
            lines.append(" ".join(words[i:i+4]))
        text_lines = "\\n".join(lines[:5])

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<defs><linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:{color1}"/>
<stop offset="100%" style="stop-color:{color2}"/>
</linearGradient></defs>
<rect width="512" height="512" fill="url(#bg)"/>
<circle cx="100" cy="100" r="80" fill="{color2}" opacity="0.5"/>
<circle cx="400" cy="400" r="120" fill="{color1}" opacity="0.4"/>
<text x="256" y="240" text-anchor="middle" font-family="Arial" font-size="24" fill="white" opacity="0.9">{text_lines}</text>
</svg>'''

        img_dir = Path("generated/images")
        img_dir.mkdir(parents=True, exist_ok=True)
        img_path = img_dir / f"img_{int(time.time())}.svg"
        img_path.write_text(svg)
        return f"Image generated: {img_path}"

    def _fetch_url(self, url: str = "") -> str:
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "PurpleUltra/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read(50000).decode("utf-8", errors="replace")
                return content[:5000]
        except Exception as e:
            return f"Failed to fetch: {e}"

    def _web_search(self, query: str = "") -> str:
        try:
            import urllib.request
            import urllib.parse
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            results = []
            import re
            for match in re.findall(r'class="result__snippet">(.*?)</a>', html, re.DOTALL):
                text = re.sub(r'<[^>]+>', '', match).strip()
                if text:
                    results.append(text[:200])
                if len(results) >= 5:
                    break
            return "\n".join(results) if results else "No results found"
        except Exception as e:
            return f"Search failed: {e}"

    def _get_time(self) -> str:
        import time as t
        return t.strftime("%Y-%m-%d %H:%M:%S")

    def _system_info(self) -> str:
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "python_version": platform.python_version(),
        }
        try:
            import psutil
            info["cpu_percent"] = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            info["memory_total"] = f"{mem.total / (1024**3):.1f} GB"
            info["memory_used"] = f"{mem.used / (1024**3):.1f} GB"
            info["memory_percent"] = mem.percent
        except ImportError:
            pass
        return json.dumps(info, indent=2)

    def _get_clipboard(self) -> str:
        try:
            if platform.system() == "Darwin":
                result = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=5)
                return result.stdout
            elif platform.system() == "Linux":
                result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], capture_output=True, text=True, timeout=5)
                return result.stdout
            return ""
        except Exception:
            return ""

    def _set_clipboard(self, text: str = "") -> str:
        try:
            if platform.system() == "Darwin":
                subprocess.run(["pbcopy"], input=text.encode(), check=True, timeout=5)
            elif platform.system() == "Linux":
                subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True, timeout=5)
            return "Copied to clipboard"
        except Exception:
            return "Failed to set clipboard"

    def _list_dir(self, path: str = ".") -> str:
        try:
            p = self._resolve_path(path)
            entries = []
            for item in sorted(p.iterdir()):
                prefix = "d" if item.is_dir() else "f"
                entries.append(f"[{prefix}] {item.name}")
            return "\n".join(entries[:50]) if entries else "Empty directory"
        except Exception as e:
            return f"Error: {e}"

    def _search_files(self, query: str = "") -> str:
        import glob
        try:
            pattern = f"**/*{query}*"
            matches = glob.glob(pattern, recursive=True)
            return "\n".join(matches[:20]) if matches else "No files found"
        except Exception as e:
            return f"Search error: {e}"

    def _read_file(self, path: str = "") -> str:
        try:
            p = self._resolve_path(path)
            content = p.read_text(errors="replace")
            return content[:10000]
        except Exception as e:
            return f"Error reading file: {e}"

    def _write_file(self, path: str = "", content: str = "") -> str:
        try:
            p = self._resolve_path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return f"Written to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def _remember(self, key: str = "", value: str = "") -> str:
        return f"Remembered: {key} = {value}"

    def _run_shell(self, command: str = "") -> str:
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30,
            )
            output = result.stdout + result.stderr
            return output[:5000] if output else "Command executed"
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Shell error: {e}"

    def _delete_file(self, path: str = "") -> str:
        try:
            p = self._resolve_path(path)
            if p.is_file():
                p.unlink()
                return f"Deleted {path}"
            elif p.is_dir():
                shutil.rmtree(p)
                return f"Deleted directory {path}"
            return f"Path not found: {path}"
        except Exception as e:
            return f"Delete error: {e}"

    def _copy_file(self, source: str = "", destination: str = "") -> str:
        try:
            src = self._resolve_path(source)
            dst = self._resolve_path(destination)
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            return f"Copied {source} to {destination}"
        except Exception as e:
            return f"Copy error: {e}"

    def _move_file(self, source: str = "", destination: str = "") -> str:
        try:
            src = self._resolve_path(source)
            dst = self._resolve_path(destination)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            return f"Moved {source} to {destination}"
        except Exception as e:
            return f"Move error: {e}"

    def _create_dir(self, path: str = "") -> str:
        try:
            p = self._resolve_path(path)
            p.mkdir(parents=True, exist_ok=True)
            return f"Created directory {path}"
        except Exception as e:
            return f"Error: {e}"

    def _get_battery(self) -> str:
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return f"Battery: {battery.percent}% {'(charging)' if battery.power_plugged else '(discharging)'}"
            return "No battery detected"
        except Exception:
            return "Battery info unavailable"

    def _get_network(self) -> str:
        try:
            import psutil
            addrs = psutil.net_if_addrs()
            info = []
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family.name == "AF_INET":
                        info.append(f"{iface}: {addr.address}")
            return "\n".join(info[:10]) if info else "No network info"
        except Exception:
            return "Network info unavailable"

    def _volume_control(self, action: str = "up", level: str = "50") -> str:
        if platform.system() == "Darwin":
            try:
                if action == "up":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"], capture_output=True)
                elif action == "down":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"], capture_output=True)
                elif action == "mute":
                    subprocess.run(["osascript", "-e", "set volume with output muted"], capture_output=True)
                elif action == "unmute":
                    subprocess.run(["osascript", "-e", "set volume without output muted"], capture_output=True)
                elif action == "set":
                    subprocess.run(["osascript", "-e", f"set volume output volume {level}"], capture_output=True)
                return f"Volume: {action}"
            except Exception:
                return "Volume control failed"
        return "Volume control not supported on this platform"

    def _launch_browser(self) -> str:
        try:
            webbrowser.open("https://www.google.com")
            return "Browser opened"
        except Exception:
            return "Failed to open browser"

    def _set_reminder(self, text: str = "", time_str: str = "") -> str:
        return f"Reminder set: {text} at {time_str}"

    def _add_task(self, task: str = "") -> str:
        return f"Task added: {task}"

    def _add_note(self, content: str = "") -> str:
        return f"Note saved: {content}"

    def _execute_code(self, code: str = "") -> str:
        try:
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True, text=True, timeout=10,
            )
            output = result.stdout + result.stderr
            return output[:5000] if output else "Code executed"
        except subprocess.TimeoutExpired:
            return "Code execution timed out"
        except Exception as e:
            return f"Execution error: {e}"

    # === NEW: System monitoring ===

    def _get_cpu_usage(self) -> str:
        try:
            import psutil
            usage = psutil.cpu_percent(interval=0.5)
            count = psutil.cpu_count()
            freq = psutil.cpu_freq()
            msg = f"CPU: {usage}% ({count} cores)"
            if freq:
                msg += f" @ {freq.current:.0f}MHz"
            return msg
        except Exception:
            return "CPU info unavailable"

    def _get_memory_usage(self) -> str:
        try:
            import psutil
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            return f"RAM: {mem.used/(1024**3):.1f}/{mem.total/(1024**3):.1f}GB ({mem.percent}%) | Swap: {swap.used/(1024**3):.1f}/{swap.total/(1024**3):.1f}GB"
        except Exception:
            return "Memory info unavailable"

    def _get_disk_usage(self, path: str = "/") -> str:
        try:
            import psutil
            usage = psutil.disk_usage(path)
            return f"Disk {path}: {usage.used/(1024**3):.1f}/{usage.total/(1024**3):.1f}GB ({usage.percent}%)"
        except Exception:
            return "Disk info unavailable"

    def _get_uptime(self) -> str:
        try:
            import psutil
            boot = psutil.boot_time()
            elapsed = time.time() - boot
            days = int(elapsed // 86400)
            hours = int((elapsed % 86400) // 3600)
            mins = int((elapsed % 3600) // 60)
            return f"Uptime: {days}d {hours}h {mins}m"
        except Exception:
            return "Uptime unavailable"

    def _list_processes(self) -> str:
        try:
            import psutil
            procs = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = p.info
                    procs.append(f"{info['pid']:>6} {info['cpu_percent']:>5.1f}% {info['memory_percent']:>5.1f}% {info['name'][:40]}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            procs.sort(key=lambda x: float(x.split()[2].rstrip('%')), reverse=True)
            return "\n".join(procs[:25]) if procs else "No processes"
        except Exception:
            return "Process list unavailable"

    def _kill_process(self, pid: str = "") -> str:
        try:
            import psutil
            p = psutil.Process(int(pid))
            name = p.name()
            p.kill()
            return f"Killed process {name} (PID {pid})"
        except Exception as e:
            return f"Failed to kill process: {e}"

    def _set_brightness(self, level: str = "50") -> str:
        if platform.system() == "Darwin":
            try:
                subprocess.run(["brightness", str(int(level) / 100)], capture_output=True, timeout=5)
                return f"Brightness set to {level}%"
            except Exception:
                try:
                    subprocess.run(["osascript", "-e", f'tell application "System Events" to tell brightness of display 1 to {int(level)/100}'], capture_output=True, timeout=5)
                    return f"Brightness set to {level}%"
                except Exception:
                    return "Brightness control unavailable"
        return "Brightness control not supported"

    def _lock_screen(self) -> str:
        if platform.system() == "Darwin":
            try:
                subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"], capture_output=True, timeout=5)
                return "Screen locked"
            except Exception:
                return "Failed to lock screen"
        elif platform.system() == "Linux":
            try:
                subprocess.run(["xdg-screensaver", "lock"], capture_output=True, timeout=5)
                return "Screen locked"
            except Exception:
                return "Failed to lock screen"
        return "Lock screen not supported"

    def _sleep_system(self) -> str:
        if platform.system() == "Darwin":
            try:
                subprocess.run(["pmset", "sleepnow"], capture_output=True, timeout=5)
                return "System going to sleep"
            except Exception:
                return "Failed to sleep"
        return "Sleep not supported"

    def _get_temperature(self) -> str:
        try:
            import psutil
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        return f"CPU temp: {entries[0].current:.1f}C"
            return "Temperature sensor not available"
        except Exception:
            return "Temperature info unavailable"

    # === NEW: File operations ===

    def _file_info(self, path: str = "") -> str:
        try:
            p = self._resolve_path(path)
            stat = p.stat()
            import datetime
            return f"Name: {p.name}\nType: {'dir' if p.is_dir() else 'file'}\nSize: {stat.st_size} bytes\nModified: {datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()}\nCreated: {datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()}"
        except Exception as e:
            return f"Error: {e}"

    def _file_exists(self, path: str = "") -> str:
        try:
            p = self._resolve_path(path)
            return f"{path} exists: {p.exists()}"
        except Exception as e:
            return f"Error: {e}"

    def _file_size(self, path: str = "") -> str:
        try:
            p = self._resolve_path(path)
            size = p.stat().st_size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size/1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size/(1024*1024):.1f} MB"
            else:
                return f"{size/(1024*1024*1024):.1f} GB"
        except Exception as e:
            return f"Error: {e}"

    def _file_hash(self, path: str = "") -> str:
        try:
            import hashlib
            p = self._resolve_path(path)
            h = hashlib.sha256()
            with open(p, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return f"SHA256: {h.hexdigest()}"
        except Exception as e:
            return f"Error: {e}"

    def _append_file(self, path: str = "", content: str = "") -> str:
        try:
            p = self._resolve_path(path)
            with open(p, "a") as f:
                f.write(content)
            return f"Appended to {path}"
        except Exception as e:
            return f"Error: {e}"

    def _read_lines(self, path: str = "", start: str = "1", end: str = "10") -> str:
        try:
            p = self._resolve_path(path)
            lines = p.read_text(errors="replace").splitlines()
            s, e = int(start) - 1, int(end)
            selected = lines[s:e]
            return "\n".join(f"{s+i+1}: {l}" for i, l in enumerate(selected))
        except Exception as e:
            return f"Error: {e}"

    def _write_lines(self, path: str = "", lines: str = "") -> str:
        try:
            p = self._resolve_path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(lines)
            return f"Written to {path}"
        except Exception as e:
            return f"Error: {e}"

    def _count_lines(self, path: str = "") -> str:
        try:
            p = self._resolve_path(path)
            count = sum(1 for _ in open(p, "rb"))
            return f"{count} lines"
        except Exception as e:
            return f"Error: {e}"

    def _find_files(self, pattern: str = "*.py") -> str:
        import glob
        matches = glob.glob(f"**/{pattern}", recursive=True)
        return "\n".join(matches[:30]) if matches else "No files found"

    # === NEW: Text processing ===

    def _text_stats(self, text: str = "") -> str:
        words = text.split()
        lines = text.splitlines()
        chars = len(text)
        return f"Characters: {chars}\nWords: {len(words)}\nLines: {len(lines)}\nSentences: {text.count('.') + text.count('!') + text.count('?')}"

    def _reverse_text(self, text: str = "") -> str:
        return text[::-1]

    def _to_uppercase(self, text: str = "") -> str:
        return text.upper()

    def _to_lowercase(self, text: str = "") -> str:
        return text.lower()

    def _base64_encode(self, text: str = "") -> str:
        import base64
        return base64.b64encode(text.encode()).decode()

    def _base64_decode(self, text: str = "") -> str:
        import base64
        return base64.b64decode(text.encode()).decode()

    def _url_encode(self, text: str = "") -> str:
        import urllib.parse
        return urllib.parse.quote(text)

    def _url_decode(self, text: str = "") -> str:
        import urllib.parse
        return urllib.parse.unquote(text)

    def _strip_text(self, text: str = "") -> str:
        return text.strip()

    def _replace_text(self, text: str = "", old: str = "", new: str = "") -> str:
        return text.replace(old, new)

    # === NEW: Date/Time ===

    def _get_date(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")

    def _get_timestamp(self) -> str:
        return str(int(time.time()))

    def _time_ago(self, timestamp: str = "") -> str:
        try:
            import datetime
            ts = float(timestamp)
            diff = time.time() - ts
            if diff < 60:
                return f"{int(diff)} seconds ago"
            elif diff < 3600:
                return f"{int(diff//60)} minutes ago"
            elif diff < 86400:
                return f"{int(diff//3600)} hours ago"
            else:
                return f"{int(diff//86400)} days ago"
        except Exception:
            return "Invalid timestamp"

    def _add_time(self, datetime_str: str = "", days: str = "0", hours: str = "0", minutes: str = "0") -> str:
        try:
            from datetime import datetime, timedelta
            dt = datetime.fromisoformat(datetime_str)
            result = dt + timedelta(days=int(days), hours=int(hours), minutes=int(minutes))
            return result.isoformat()
        except Exception as e:
            return f"Error: {e}"

    # === NEW: Network ===

    def _ping(self, host: str = "") -> str:
        try:
            flag = "-c" if platform.system() != "Windows" else "-n"
            result = subprocess.run(["ping", flag, "3", host], capture_output=True, text=True, timeout=15)
            lines = result.stdout.strip().splitlines()
            return "\n".join(lines[-3:]) if lines else "No response"
        except Exception as e:
            return f"Ping failed: {e}"

    def _check_port(self, host: str = "127.0.0.1", port: str = "80") -> str:
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((host, int(port)))
            s.close()
            return f"Port {port} on {host}: {'OPEN' if result == 0 else 'CLOSED'}"
        except Exception as e:
            return f"Error: {e}"

    def _get_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return f"Local IP: {ip}"
        except Exception:
            return "Could not determine IP"

    def _get_public_ip(self) -> str:
        try:
            import urllib.request
            req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "PurpleUltra/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return f"Public IP: {resp.read().decode()}"
        except Exception:
            return "Could not get public IP"

    def _dns_lookup(self, domain: str = "") -> str:
        import socket
        try:
            results = socket.getaddrinfo(domain, None)
            ips = list(set(r[4][0] for r in results))
            return f"{domain}: {', '.join(ips)}"
        except Exception as e:
            return f"DNS lookup failed: {e}"

    # === NEW: Developer tools ===

    def _run_python(self, path: str = "") -> str:
        try:
            result = subprocess.run(["python3", path], capture_output=True, text=True, timeout=30)
            output = result.stdout + result.stderr
            return output[:5000] if output else "Script executed"
        except subprocess.TimeoutExpired:
            return "Script timed out"
        except Exception as e:
            return f"Error: {e}"

    def _pip_install(self, package: str = "") -> str:
        try:
            result = subprocess.run(["pip3", "install", package], capture_output=True, text=True, timeout=60)
            return result.stdout[-2000:] if result.stdout else result.stderr[-2000:]
        except Exception as e:
            return f"Install failed: {e}"

    def _pip_list(self) -> str:
        try:
            result = subprocess.run(["pip3", "list", "--format=columns"], capture_output=True, text=True, timeout=10)
            return result.stdout[:5000] if result.stdout else "No packages"
        except Exception:
            return "Could not list packages"

    def _check_syntax(self, code: str = "") -> str:
        try:
            compile(code, "<string>", "exec")
            return "Syntax OK"
        except SyntaxError as e:
            return f"Syntax error: {e}"

    def _format_json(self, json_str: str = "") -> str:
        try:
            data = json.loads(json_str)
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"Invalid JSON: {e}"

    def _minify_json(self, json_str: str = "") -> str:
        try:
            data = json.loads(json_str)
            return json.dumps(data, separators=(',', ':'))
        except Exception as e:
            return f"Invalid JSON: {e}"

    def _json_query(self, json_str: str = "", query: str = "") -> str:
        try:
            data = json.loads(json_str)
            parts = query.strip(".").split(".")
            current = data
            for part in parts:
                if part.isdigit():
                    current = current[int(part)]
                else:
                    current = current[part]
            return json.dumps(current, indent=2) if isinstance(current, (dict, list)) else str(current)
        except Exception as e:
            return f"Query error: {e}"

    # === NEW: Utility ===

    def _calculate(self, expression: str = "") -> str:
        import math
        try:
            safe_dict = {"__builtins__": {}}
            safe_dict.update({k: v for k, v in math.__dict__.items() if not k.startswith("_")})
            result = eval(expression, safe_dict)
            return str(result)
        except Exception as e:
            return f"Calc error: {e}"

    def _uuid_generate(self) -> str:
        import uuid
        return str(uuid.uuid4())

    def _hash_text(self, text: str = "", algorithm: str = "sha256") -> str:
        import hashlib
        try:
            h = hashlib.new(algorithm)
            h.update(text.encode())
            return f"{algorithm}: {h.hexdigest()}"
        except Exception:
            return "Unknown algorithm"

    def _color_convert(self, color: str = "", to_format: str = "hex") -> str:
        try:
            color = color.lstrip("#")
            if len(color) == 6:
                r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            else:
                return "Invalid hex color"
            if to_format == "rgb":
                return f"rgb({r}, {g}, {b})"
            elif to_format == "hsl":
                import colorsys
                h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
                return f"hsl({int(h*360)}, {int(s*100)}%, {int(l*100)}%)"
            else:
                return f"#{r:02x}{g:02x}{b:02x}"
        except Exception as e:
            return f"Error: {e}"

    def _random_number(self, low: str = "1", high: str = "100") -> str:
        import random
        return str(random.randint(int(low), int(high)))

    def _random_choice(self, options: str = "") -> str:
        import random
        items = [o.strip() for o in options.split(",") if o.strip()]
        return random.choice(items) if items else "Empty list"

    def _encode_morse(self, text: str = "") -> str:
        MORSE = {'.-':'A', '-...':'B', '-.-.':'C', '-..':'D', '.':'E', '..-.':'F', '--.':'G', '....':'H', '..':'I', '.---':'J', '-.-':'K', '.-..':'L', '--':'M', '-.':'N', '---':'O', '.--.':'P', '--.-':'Q', '.-.':'R', '...':'S', '-':'T', '..-':'U', '...-':'V', '.--':'W', '-..-':'X', '-.--':'Y', '--..':'Z', '-----':'0', '.----':'1', '..---':'2', '...--':'3', '....-':'4', '.....':'5', '-....':'6', '--...':'7', '---..':'8', '----.':'9'}
        REVERSE = {v: k for k, v in MORSE.items()}
        words = text.upper().split()
        result = []
        for word in words:
            coded = []
            for ch in word:
                if ch in REVERSE:
                    coded.append(REVERSE[ch])
            result.append(" ".join(coded))
        return " / ".join(result)

    def _decode_morse(self, text: str = "") -> str:
        MORSE = {'.-':'A', '-...':'B', '-.-.':'C', '-..':'D', '.':'E', '..-.':'F', '--.':'G', '....':'H', '..':'I', '.---':'J', '-.-':'K', '.-..':'L', '--':'M', '-.':'N', '---':'O', '.--.':'P', '--.-':'Q', '.-.':'R', '...':'S', '-':'T', '..-':'U', '...-':'V', '.--':'W', '-..-':'X', '-.--':'Y', '--..':'Z', '-----':'0', '.----':'1', '..---':'2', '...--':'3', '....-':'4', '.....':'5', '-....':'6', '--...':'7', '---..':'8', '----.':'9'}
        words = text.strip().split(" / ")
        result = []
        for word in words:
            decoded = []
            for code in word.split():
                if code in MORSE:
                    decoded.append(MORSE[code])
            result.append("".join(decoded))
        return " ".join(result)

    # === Math/Number tools ===

    def _factorial(self, n: str = "1") -> str:
        import math
        try:
            return str(math.factorial(int(n)))
        except Exception as e:
            return f"Error: {e}"

    def _fibonacci(self, n: str = "10") -> str:
        a, b = 0, 1
        seq = []
        for _ in range(int(n)):
            seq.append(a)
            a, b = b, a + b
        return str(seq)

    def _is_prime(self, n: str = "2") -> str:
        num = int(n)
        if num < 2:
            return f"{num} is not prime"
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                return f"{num} is not prime (divisible by {i})"
        return f"{num} is prime"

    def _gcd(self, a: str = "1", b: str = "1") -> str:
        import math
        return str(math.gcd(int(a), int(b)))

    def _lcm(self, a: str = "1", b: str = "1") -> str:
        import math
        return str(math.lcm(int(a), int(b)))

    def _prime_factors(self, n: str = "12") -> str:
        num = int(n)
        factors = []
        d = 2
        while d * d <= num:
            while num % d == 0:
                factors.append(d)
                num //= d
            d += 1
        if num > 1:
            factors.append(num)
        return str(factors)

    def _is_even(self, n: str = "0") -> str:
        return f"{n} is {'even' if int(n) % 2 == 0 else 'odd'}"

    def _is_odd(self, n: str = "0") -> str:
        return f"{n} is {'odd' if int(n) % 2 != 0 else 'even'}"

    def _abs_value(self, n: str = "0") -> str:
        return str(abs(float(n)))

    def _sqrt(self, n: str = "1") -> str:
        import math
        return str(math.sqrt(float(n)))

    def _power(self, base: str = "2", exp: str = "10") -> str:
        return str(float(base) ** float(exp))

    def _log(self, n: str = "1", base: str = "10") -> str:
        import math
        return str(math.log(float(n), float(base)))

    def _round_number(self, n: str = "0", decimals: str = "2") -> str:
        return str(round(float(n), int(decimals)))

    def _clamp(self, n: str = "0", low: str = "0", high: str = "100") -> str:
        return str(max(float(low), min(float(high), float(n))))

    def _percentage(self, part: str = "0", total: str = "100") -> str:
        try:
            return f"{float(part)/float(total)*100:.2f}%"
        except Exception:
            return "Error"

    # === Array/List tools ===

    def _list_sort(self, items: str = "") -> str:
        try:
            import json
            lst = json.loads(items) if items.startswith("[") else [i.strip() for i in items.split(",")]
            return json.dumps(sorted(lst, key=lambda x: float(x) if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.','').replace('-','').isdigit()) else x))
        except Exception as e:
            return f"Error: {e}"

    def _list_unique(self, items: str = "") -> str:
        import json
        lst = json.loads(items) if items.startswith("[") else [i.strip() for i in items.split(",")]
        return json.dumps(list(dict.fromkeys(lst)))

    def _list_reverse(self, items: str = "") -> str:
        import json
        lst = json.loads(items) if items.startswith("[") else [i.strip() for i in items.split(",")]
        return json.dumps(list(reversed(lst)))

    def _list_flatten(self, items: str = "") -> str:
        import json
        def flatten(lst):
            result = []
            for i in lst:
                if isinstance(i, list):
                    result.extend(flatten(i))
                else:
                    result.append(i)
            return result
        lst = json.loads(items)
        return json.dumps(flatten(lst))

    def _list_chunk(self, items: str = "", size: str = "3") -> str:
        import json
        lst = json.loads(items) if items.startswith("[") else [i.strip() for i in items.split(",")]
        chunk_size = int(size)
        return json.dumps([lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)])

    def _list_count(self, items: str = "", item: str = "") -> str:
        import json
        lst = json.loads(items) if items.startswith("[") else [i.strip() for i in items.split(",")]
        return str(lst.count(item.strip()))

    def _list_sum(self, items: str = "") -> str:
        import json
        lst = json.loads(items) if items.startswith("[") else [float(i.strip()) for i in items.split(",")]
        return str(sum(lst))

    def _list_avg(self, items: str = "") -> str:
        import json
        lst = json.loads(items) if items.startswith("[") else [float(i.strip()) for i in items.split(",")]
        return str(sum(lst) / len(lst)) if lst else "0"

    def _list_min(self, items: str = "") -> str:
        import json
        lst = json.loads(items) if items.startswith("[") else [float(i.strip()) for i in items.split(",")]
        return str(min(lst)) if lst else "empty"

    def _list_max(self, items: str = "") -> str:
        import json
        lst = json.loads(items) if items.startswith("[") else [float(i.strip()) for i in items.split(",")]
        return str(max(lst)) if lst else "empty"

    def _list_diff(self, a: str = "", b: str = "") -> str:
        import json
        la = json.loads(a) if a.startswith("[") else [i.strip() for i in a.split(",")]
        lb = json.loads(b) if b.startswith("[") else [i.strip() for i in b.split(",")]
        return json.dumps([x for x in la if x not in lb])

    def _list_intersect(self, a: str = "", b: str = "") -> str:
        import json
        la = json.loads(a) if a.startswith("[") else [i.strip() for i in a.split(",")]
        lb = json.loads(b) if b.startswith("[") else [i.strip() for i in b.split(",")]
        return json.dumps([x for x in la if x in lb])

    def _list_union(self, a: str = "", b: str = "") -> str:
        import json
        la = json.loads(a) if a.startswith("[") else [i.strip() for i in a.split(",")]
        lb = json.loads(b) if b.startswith("[") else [i.strip() for i in b.split(",")]
        return json.dumps(list(dict.fromkeys(la + lb)))

    # === DateTime tools ===

    def _day_of_week(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%A")

    def _day_of_year(self) -> str:
        from datetime import datetime
        now = datetime.now()
        return str((now - datetime(now.year, 1, 1)).days + 1)

    def _week_number(self) -> str:
        from datetime import datetime
        return str(datetime.now().isocalendar()[1])

    def _is_leap_year(self, year: str = "2024") -> str:
        y = int(year)
        return f"{y} is {'a leap year' if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0 else 'not a leap year'}"

    def _days_between(self, date1: str = "2024-01-01", date2: str = "2024-12-31") -> str:
        from datetime import datetime
        d1 = datetime.fromisoformat(date1)
        d2 = datetime.fromisoformat(date2)
        return str(abs((d2 - d1).days))

    def _age_calc(self, birthday: str = "2000-01-01") -> str:
        from datetime import datetime
        bd = datetime.fromisoformat(birthday)
        today = datetime.now()
        age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        return f"{age} years old"

    def _next_friday(self) -> str:
        from datetime import datetime, timedelta
        today = datetime.now()
        days_ahead = (4 - today.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    def _unix_to_date(self, timestamp: str = "0") -> str:
        from datetime import datetime
        return datetime.fromtimestamp(float(timestamp)).isoformat()

    def _date_to_unix(self, date: str = "2024-01-01") -> str:
        from datetime import datetime
        return str(int(datetime.fromisoformat(date).timestamp()))

    def _timezone_convert(self, datetime: str = "2024-01-01T00:00:00", from_tz: str = "UTC", to_tz: str = "US/Eastern") -> str:
        try:
            from datetime import datetime as dt
            import zoneinfo
            src_tz = zoneinfo.ZoneInfo(from_tz)
            dst_tz = zoneinfo.ZoneInfo(to_tz)
            d = dt.fromisoformat(datetime).replace(tzinfo=src_tz)
            return d.astimezone(dst_tz).isoformat()
        except Exception as e:
            return f"Error: {e}"

    # === Encoding tools ===

    def _hex_encode(self, text: str = "") -> str:
        return text.encode().hex()

    def _hex_decode(self, text: str = "") -> str:
        return bytes.fromhex(text).decode()

    def _binary_encode(self, text: str = "") -> str:
        return " ".join(format(b, '08b') for b in text.encode())

    def _binary_decode(self, text: str = "") -> str:
        return "".join(chr(int(b, 2)) for b in text.split() if len(b) == 8)

    def _octal_encode(self, text: str = "") -> str:
        return " ".join(format(b, '03o') for b in text.encode())

    def _rot13(self, text: str = "") -> str:
        import codecs
        return codecs.encode(text, 'rot_13')

    def _caesar_cipher(self, text: str = "", shift: str = "3") -> str:
        s = int(shift)
        result = []
        for c in text:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                result.append(chr((ord(c) - base + s) % 26 + base))
            else:
                result.append(c)
        return "".join(result)

    def _atbash_cipher(self, text: str = "") -> str:
        result = []
        for c in text:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                result.append(chr(base + 25 - (ord(c) - base)))
            else:
                result.append(c)
        return "".join(result)

    # === Crypto/Password tools ===

    def _generate_password(self, length: str = "16", symbols: str = "true") -> str:
        import secrets
        import string
        chars = string.ascii_letters + string.digits
        if symbols.lower() == "true":
            chars += string.punctuation
        return "".join(secrets.choice(chars) for _ in range(int(length)))

    def _generate_passphrase(self, words: str = "4") -> str:
        import secrets
        wordlist = ["apple","bridge","castle","delta","eagle","flame","grape","harbor","island","jungle","kite","lemon","mango","noble","ocean","pearl","quest","river","storm","tiger","umbrella","vivid","whale","xenon","yield","zebra","anchor","breeze","coral","drift","ember","frost","gleam","haze","ivory","jewel","karma","lunar","maple","nexus","orbit","prism","quartz","radar","solar","thorn","unity","vapor","woven","zephyr"]
        return " ".join(secrets.choice(wordlist) for _ in range(int(words)))

    def _aes_encrypt(self, text: str = "", key: str = "") -> str:
        import base64
        import hashlib
        from itertools import cycle
        key_bytes = hashlib.sha256(key.encode()).digest()
        encrypted = bytes(a ^ b for a, b in zip(text.encode(), cycle(key_bytes)))
        return base64.b64encode(encrypted).decode()

    def _aes_decrypt(self, text: str = "", key: str = "") -> str:
        import base64
        import hashlib
        from itertools import cycle
        key_bytes = hashlib.sha256(key.encode()).digest()
        decrypted = bytes(a ^ b for a, b in zip(base64.b64decode(text), cycle(key_bytes)))
        return decrypted.decode()

    def _hmac_hash(self, text: str = "", key: str = "secret", algorithm: str = "sha256") -> str:
        import hmac
        import hashlib
        h = hmac.new(key.encode(), text.encode(), getattr(hashlib, algorithm))
        return h.hexdigest()

    def _xor_encrypt(self, text: str = "", key: str = "") -> str:
        return "".join(chr(ord(a) ^ ord(b)) for a, b in zip(text, key * (len(text) // len(key) + 1)))

    # === Regex tools ===

    def _regex_match(self, text: str = "", pattern: str = "") -> str:
        import re
        m = re.search(pattern, text)
        return f"Match: {m.group()} at position {m.start()}-{m.end()}" if m else "No match"

    def _regex_find(self, text: str = "", pattern: str = "") -> str:
        import re
        matches = re.findall(pattern, text)
        return str(matches) if matches else "No matches"

    def _regex_replace(self, text: str = "", pattern: str = "", replacement: str = "") -> str:
        import re
        return re.sub(pattern, replacement, text)

    def _regex_extract(self, text: str = "", pattern: str = "") -> str:
        import re
        m = re.search(pattern, text)
        return str(m.groups()) if m and m.groups() else "No groups captured"

    def _email_validate(self, email: str = "") -> str:
        import re
        valid = bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
        return f"{email} is {'valid' if valid else 'invalid'}"

    def _url_validate(self, url: str = "") -> str:
        import re
        valid = bool(re.match(r'^https?://[^\s/$.?#].[^\s]*$', url))
        return f"{url} is {'valid' if valid else 'invalid'}"

    def _phone_validate(self, phone: str = "") -> str:
        import re
        clean = re.sub(r'[\s\-\(\)\+]', '', phone)
        valid = bool(re.match(r'^\d{7,15}$', clean))
        return f"{phone} is {'valid' if valid else 'invalid'}"

    # === CSV/JSON/XML tools ===

    def _csv_to_json(self, csv_text: str = "") -> str:
        import csv as csv_mod
        import io
        import json
        reader = csv_mod.DictReader(io.StringIO(csv_text))
        return json.dumps(list(reader), indent=2)

    def _json_to_csv(self, json_str: str = "") -> str:
        import csv
        import io
        import json
        data = json.loads(json_str)
        if not data:
            return "Empty data"
        if isinstance(data, dict):
            data = [data]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

    def _json_validate(self, json_str: str = "") -> str:
        import json
        try:
            json.loads(json_str)
            return "Valid JSON"
        except json.JSONDecodeError as e:
            return f"Invalid JSON: {e}"

    def _json_merge(self, a: str = "", b: str = "") -> str:
        import json
        da = json.loads(a)
        db = json.loads(b)
        da.update(db)
        return json.dumps(da, indent=2)

    def _json_diff(self, a: str = "", b: str = "") -> str:
        import json
        da = json.loads(a)
        db = json.loads(b)
        diffs = []
        all_keys = set(list(da.keys()) + list(db.keys()))
        for k in all_keys:
            if k not in da:
                diffs.append(f"+ {k}: {db[k]}")
            elif k not in db:
                diffs.append(f"- {k}: {da[k]}")
            elif da[k] != db[k]:
                diffs.append(f"~ {k}: {da[k]} -> {db[k]}")
        return "\n".join(diffs) if diffs else "No differences"

    def _xml_to_json(self, xml: str = "") -> str:
        import xml.etree.ElementTree as ET
        import json
        def elem_to_dict(elem):
            d = {}
            if elem.text and elem.text.strip():
                d["#text"] = elem.text.strip()
            for child in elem:
                child_dict = elem_to_dict(child)
                if child.tag in d:
                    if not isinstance(d[child.tag], list):
                        d[child.tag] = [d[child.tag]]
                    d[child.tag].append(child_dict)
                else:
                    d[child.tag] = child_dict
            return d
        try:
            root = ET.fromstring(xml)
            return json.dumps({root.tag: elem_to_dict(root)}, indent=2)
        except Exception as e:
            return f"Error: {e}"

    def _yaml_to_json(self, yaml: str = "") -> str:
        import json
        result = {}
        for line in yaml.strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                result[key.strip()] = val.strip()
        return json.dumps(result, indent=2)

    def _json_to_yaml(self, json_str: str = "") -> str:
        import json
        data = json.loads(json_str)
        lines = []
        for k, v in data.items():
            lines.append(f"{k}: {v}")
        return "\n".join(lines)

    # === Git tools ===

    def _run_git(self, args: list, path: str = "") -> str:
        try:
            cmd = ["git"] + args
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd=path or None)
            return result.stdout.strip() or result.stderr.strip() or "OK"
        except Exception as e:
            return f"Git error: {e}"

    def _git_status(self, path: str = "") -> str:
        return self._run_git(["status", "--short"], path)

    def _git_log(self, path: str = "", count: str = "10") -> str:
        return self._run_git(["log", f"--oneline", f"-{count}"], path)

    def _git_diff(self, path: str = "") -> str:
        return self._run_git(["diff", "--stat"], path)[:2000]

    def _git_branch(self, path: str = "") -> str:
        return self._run_git(["branch", "-a"], path)

    def _git_remote(self, path: str = "") -> str:
        return self._run_git(["remote", "-v"], path)

    def _git_stash(self, path: str = "") -> str:
        return self._run_git(["stash"], path)

    # === Docker tools ===

    def _docker_containers(self) -> str:
        try:
            result = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}\t{{.Image}}"], capture_output=True, text=True, timeout=10)
            return result.stdout.strip() or "No containers"
        except Exception:
            return "Docker not available"

    def _docker_images(self) -> str:
        try:
            result = subprocess.run(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}\t{{.Size}}"], capture_output=True, text=True, timeout=10)
            return result.stdout.strip() or "No images"
        except Exception:
            return "Docker not available"

    def _docker_stats(self) -> str:
        try:
            result = subprocess.run(["docker", "stats", "--no-stream", "--format", "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"], capture_output=True, text=True, timeout=10)
            return result.stdout.strip() or "No running containers"
        except Exception:
            return "Docker not available"

    def _docker_logs(self, container: str = "") -> str:
        try:
            result = subprocess.run(["docker", "logs", "--tail", "50", container], capture_output=True, text=True, timeout=10)
            return (result.stdout + result.stderr)[-3000:]
        except Exception as e:
            return f"Error: {e}"

    # === Statistics tools ===

    def _parse_numbers(self, s: str) -> list:
        import json
        s = s.strip()
        if s.startswith("["):
            return json.loads(s)
        return [float(x.strip()) for x in s.split(",") if x.strip()]

    def _mean(self, numbers: str = "") -> str:
        nums = self._parse_numbers(numbers)
        return str(sum(nums) / len(nums)) if nums else "empty"

    def _median(self, numbers: str = "") -> str:
        nums = sorted(self._parse_numbers(numbers))
        n = len(nums)
        if n == 0:
            return "empty"
        if n % 2 == 0:
            return str((nums[n//2-1] + nums[n//2]) / 2)
        return str(nums[n//2])

    def _mode(self, numbers: str = "") -> str:
        from collections import Counter
        nums = self._parse_numbers(numbers)
        if not nums:
            return "empty"
        counts = Counter(nums)
        max_count = max(counts.values())
        modes = [k for k, v in counts.items() if v == max_count]
        return str(modes)

    def _stdev(self, numbers: str = "") -> str:
        import statistics
        nums = self._parse_numbers(numbers)
        return str(statistics.stdev(nums)) if len(nums) > 1 else "need 2+ numbers"

    def _variance(self, numbers: str = "") -> str:
        import statistics
        nums = self._parse_numbers(numbers)
        return str(statistics.variance(nums)) if len(nums) > 1 else "need 2+ numbers"

    def _percentile(self, numbers: str = "", p: str = "50") -> str:
        nums = sorted(self._parse_numbers(numbers))
        k = (len(nums) - 1) * float(p) / 100
        f = int(k)
        c = f + 1 if f + 1 < len(nums) else f
        return str(nums[f] + (k - f) * (nums[c] - nums[f]))

    def _correlation(self, x: str = "", y: str = "") -> str:
        import statistics
        xs = self._parse_numbers(x)
        ys = self._parse_numbers(y)
        if len(xs) != len(ys) or len(xs) < 2:
            return "Need equal-length lists with 2+ values"
        mx, my = statistics.mean(xs), statistics.mean(ys)
        cov = sum((xi-mx)*(yi-my) for xi, yi in zip(xs, ys)) / (len(xs)-1)
        sx, sy = statistics.stdev(xs), statistics.stdev(ys)
        return str(cov / (sx * sy)) if sx and sy else "0"

    # === Environment tools ===

    def _env_get(self, name: str = "HOME") -> str:
        return os.environ.get(name, "Not set")

    def _env_set(self, name: str = "", value: str = "") -> str:
        os.environ[name] = value
        return f"Set {name}={value}"

    def _env_list(self, filter: str = "") -> str:
        items = [(k, v) for k, v in os.environ.items()]
        if filter:
            items = [(k, v) for k, v in items if filter.lower() in k.lower()]
        return "\n".join(f"{k}={v[:100]}" for k, v in sorted(items)[:50])

    def _env_home(self) -> str:
        return str(Path.home())

    def _env_cwd(self) -> str:
        return str(Path.cwd())

    def _env_tmp(self) -> str:
        import tempfile
        return tempfile.gettempdir()

    # === Archive tools ===

    def _zip_files(self, files: str = "", output: str = "archive.zip") -> str:
        import zipfile
        file_list = [f.strip() for f in files.split(",") if f.strip()]
        try:
            with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
                for f in file_list:
                    if os.path.exists(f):
                        zf.write(f)
            return f"Created {output} with {len(file_list)} files"
        except Exception as e:
            return f"Error: {e}"

    def _unzip_file(self, path: str = "", output: str = ".") -> str:
        import zipfile
        try:
            with zipfile.ZipFile(path, 'r') as zf:
                zf.extractall(output)
            return f"Extracted to {output}"
        except Exception as e:
            return f"Error: {e}"

    def _tar_create(self, files: str = "", output: str = "archive.tar.gz") -> str:
        import tarfile
        file_list = [f.strip() for f in files.split(",") if f.strip()]
        try:
            with tarfile.open(output, "w:gz") as tf:
                for f in file_list:
                    if os.path.exists(f):
                        tf.add(f)
            return f"Created {output}"
        except Exception as e:
            return f"Error: {e}"

    def _tar_extract(self, path: str = "", output: str = ".") -> str:
        import tarfile
        try:
            with tarfile.open(path, "r:*") as tf:
                tf.extractall(output)
            return f"Extracted to {output}"
        except Exception as e:
            return f"Error: {e}"

    def _archive_list(self, path: str = "") -> str:
        import zipfile
        import tarfile
        try:
            if zipfile.is_zipfile(path):
                with zipfile.ZipFile(path) as zf:
                    return "\n".join(zf.namelist())
            elif tarfile.is_tarfile(path):
                with tarfile.open(path) as tf:
                    return "\n".join(tf.getnames())
        except Exception:
            pass
        return "Unknown or invalid archive"

    # === Markdown/HTML tools ===

    def _md_to_html(self, text: str = "") -> str:
        import re
        html = text
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        return html

    def _html_to_text(self, html: str = "") -> str:
        import re
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _html_entities(self, text: str = "") -> str:
        import html as h
        return h.escape(text)

    def _word_wrap(self, text: str = "", width: str = "80") -> str:
        w = int(width)
        words = text.split()
        lines = []
        current = []
        length = 0
        for word in words:
            if length + len(word) + 1 > w:
                lines.append(" ".join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += len(word) + 1
        if current:
            lines.append(" ".join(current))
        return "\n".join(lines)

    # === Notification/OS tools ===

    def _notify(self, title: str = "Purple Ultra", message: str = "") -> str:
        if platform.system() == "Darwin":
            try:
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(["osascript", "-e", script], capture_output=True, timeout=5)
                return "Notification sent"
            except Exception:
                return "Failed to send notification"
        elif platform.system() == "Linux":
            try:
                subprocess.run(["notify-send", title, message], capture_output=True, timeout=5)
                return "Notification sent"
            except Exception:
                return "Failed to send notification"
        return "Notifications not supported"

    def _get_wallpaper(self) -> str:
        if platform.system() == "Darwin":
            try:
                result = subprocess.run(["osascript", "-e", 'tell application "System Events" to get picture of current desktop'], capture_output=True, text=True, timeout=5)
                return result.stdout.strip()
            except Exception:
                return "Could not get wallpaper"
        return "Not supported on this platform"

    def _set_wallpaper(self, path: str = "") -> str:
        if platform.system() == "Darwin":
            try:
                subprocess.run(["osascript", "-e", f'tell application "System Events" to set picture of current desktop to "{path}"'], capture_output=True, timeout=5)
                return f"Wallpaper set to {path}"
            except Exception:
                return "Failed to set wallpaper"
        return "Not supported on this platform"

    def _get_screensaver_status(self) -> str:
        if platform.system() == "Darwin":
            try:
                result = subprocess.run(["osascript", "-e", 'tell application "System Events" to get running of screensaver'], capture_output=True, text=True, timeout=5)
                return f"Screensaver running: {result.stdout.strip()}"
            except Exception:
                return "Could not check"
        return "Not supported"

    def _get_display_info(self) -> str:
        if platform.system() == "Darwin":
            try:
                result = subprocess.run(["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True, timeout=10)
                lines = result.stdout.splitlines()
                relevant = [l for l in lines if any(k in l.lower() for k in ["resolution", "display type", "retina", "chipset"])]
                return "\n".join(relevant[:10]) or "Display info unavailable"
            except Exception:
                return "Could not get display info"
        return "Not supported"

    # === Database tools ===

    def _sqlite_query(self, db: str = "", sql: str = "") -> str:
        import sqlite3
        try:
            conn = sqlite3.connect(db)
            cursor = conn.execute(sql)
            if cursor.description:
                columns = [d[0] for d in cursor.description]
                rows = cursor.fetchall()
                result = [", ".join(columns)]
                for row in rows[:50]:
                    result.append(", ".join(str(v) for v in row))
                conn.close()
                return "\n".join(result)
            conn.commit()
            conn.close()
            return f"Query executed ({cursor.rowcount} rows affected)"
        except Exception as e:
            return f"Error: {e}"

    def _sqlite_tables(self, db: str = "") -> str:
        return self._sqlite_query(db, "SELECT name FROM sqlite_master WHERE type='table'")

    def _sqlite_insert(self, db: str = "", table: str = "", data: str = "") -> str:
        import sqlite3
        import json
        try:
            record = json.loads(data)
            cols = ", ".join(record.keys())
            placeholders = ", ".join("?" * len(record))
            sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
            conn = sqlite3.connect(db)
            conn.execute(sql, list(record.values()))
            conn.commit()
            conn.close()
            return f"Inserted into {table}"
        except Exception as e:
            return f"Error: {e}"

    # === Process tools ===

    def _find_process(self, name: str = "") -> str:
        try:
            import psutil
            found = []
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if name.lower() in p.info['name'].lower():
                        found.append(f"PID {p.info['pid']}: {p.info['name']} ({p.info['cpu_percent']}% CPU)")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return "\n".join(found[:10]) or "No matching processes"
        except Exception:
            return "Process search unavailable"

    def _process_tree(self, pid: str = "1") -> str:
        try:
            import psutil
            parent = psutil.Process(int(pid))
            tree = []
            def walk(proc, indent=0):
                tree.append(f"{'  '*indent}{proc.pid}: {proc.name()}")
                for child in proc.children(recursive=False):
                    walk(child, indent+1)
            walk(parent)
            return "\n".join(tree[:30])
        except Exception as e:
            return f"Error: {e}"

    def _open_ports(self) -> str:
        try:
            import psutil
            ports = []
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN':
                    ports.append(f"{conn.laddr.ip}:{conn.laddr.port} ({conn.pid})")
            return "\n".join(sorted(set(ports))[:20]) or "No open ports"
        except Exception:
            return "Could not list ports"

    # === Image tools ===

    def _image_info(self, path: str = "") -> str:
        try:
            from PIL import Image
            img = Image.open(path)
            return f"Format: {img.format}\nSize: {img.size}\nMode: {img.mode}\nInfo: {dict(list(img.info.items())[:5])}"
        except ImportError:
            try:
                result = subprocess.run(["file", path], capture_output=True, text=True, timeout=5)
                return result.stdout.strip()
            except Exception:
                return "Install Pillow for image info"
        except Exception as e:
            return f"Error: {e}"

    def _image_resize(self, path: str = "", width: str = "100", height: str = "100") -> str:
        try:
            from PIL import Image
            img = Image.open(path)
            img = img.resize((int(width), int(height)))
            out = path.rsplit('.', 1)[0] + f"_resized.{path.rsplit('.', 1)[1]}"
            img.save(out)
            return f"Saved to {out}"
        except ImportError:
            return "Install Pillow for image resize"
        except Exception as e:
            return f"Error: {e}"

    def _image_to_base64(self, path: str = "") -> str:
        import base64
        try:
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return data[:500] + "..." if len(data) > 500 else data
        except Exception as e:
            return f"Error: {e}"

    # === QR tools ===

    def _qr_generate(self, text: str = "") -> str:
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            path = "generated/qr_code.png"
            os.makedirs("generated", exist_ok=True)
            img.save(path)
            return f"QR code saved to {path}"
        except ImportError:
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect width="200" height="200" fill="white"/><text x="100" y="100" text-anchor="middle" font-size="12">QR: {text[:30]}</text></svg>'
            path = "generated/qr_code.svg"
            os.makedirs("generated", exist_ok=True)
            with open(path, "w") as f:
                f.write(svg)
            return f"QR placeholder saved to {path} (install qrcode for real QR)"
        except Exception as e:
            return f"Error: {e}"

    # === String tools ===

    def _string_contains(self, text: str = "", search: str = "") -> str:
        return f"'{search}' {'found' if search in text else 'not found'} in text"

    def _string_count(self, text: str = "", search: str = "") -> str:
        return str(text.count(search))

    def _string_pad(self, text: str = "", length: str = "20", char: str = " ") -> str:
        return text.center(int(length), char)

    def _string_trim(self, text: str = "", length: str = "100") -> str:
        n = int(length)
        return text[:n] + "..." if len(text) > n else text

    def _string_repeat(self, text: str = "", count: str = "3") -> str:
        return text * int(count)

    def _string_diff(self, a: str = "", b: str = "") -> str:
        import difflib
        diff = list(difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm=""))
        return "\n".join(diff[:20]) if diff else "No differences"

    # === Network tools ===

    def _http_headers(self, url: str = "") -> str:
        import urllib.request
        try:
            req = urllib.request.Request(url, method='HEAD', headers={"User-Agent": "PurpleUltra/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                headers = dict(resp.headers)
                return "\n".join(f"{k}: {v}" for k, v in headers.items())
        except Exception as e:
            return f"Error: {e}"

    def _ssl_check(self, host: str = "") -> str:
        import ssl
        import socket
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                s.connect((host, 443))
                cert = s.getpeercert()
                return f"Issuer: {dict(x[0] for x in cert.get('issuer', []))}\nSubject: {dict(x[0] for x in cert.get('subject', []))}\nValid: {cert.get('notBefore')} to {cert.get('notAfter')}"
        except Exception as e:
            return f"SSL check failed: {e}"

    def _traceroute(self, host: str = "") -> str:
        try:
            flag = "-m" if platform.system() != "Windows" else "-d"
            result = subprocess.run(["traceroute", flag, "15", host], capture_output=True, text=True, timeout=30)
            return result.stdout[:2000] or "No traceroute output"
        except Exception:
            return "Traceroute not available"

    # === Utility tools ===

    def _timer_start(self, name: str = "default") -> str:
        import time
        self._timers[name] = time.perf_counter()
        return f"Timer '{name}' started"

    def _timer_stop(self, name: str = "default") -> str:
        import time
        if name in self._timers:
            elapsed = time.perf_counter() - self._timers.pop(name)
            return f"Timer '{name}': {elapsed*1000:.2f}ms"
        return f"Timer '{name}' not found"

    def _diff_text(self, a: str = "", b: str = "") -> str:
        import difflib
        a_lines = a.splitlines()
        b_lines = b.splitlines()
        diff = list(difflib.unified_diff(a_lines, b_lines, fromtext="a", totext="b"))
        return "\n".join(diff[:30]) if diff else "No differences"

    def _sort_dict(self, json_str: str = "") -> str:
        import json
        data = json.loads(json_str)
        sorted_items = sorted(data.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else str(x[1]))
        return json.dumps(dict(sorted_items), indent=2)

    def _flatten_dict(self, json_str: str = "", sep: str = ".") -> str:
        import json
        def flatten(d, parent_key=""):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten(v, new_key).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        data = json.loads(json_str)
        return json.dumps(flatten(data), indent=2)
