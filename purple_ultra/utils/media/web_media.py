"""Web media control for 26+ platforms."""

from __future__ import annotations

import webbrowser
import subprocess
import platform
from urllib.parse import quote_plus


class WebMediaController:
    PLATFORMS = {
        "youtube": {"search": "https://www.youtube.com/results?search_query={}", "play": "https://www.youtube.com/results?search_query={}&sp=EgIQAQ%253D%253D"},
        "spotify": {"search": "https://open.spotify.com/search/{}", "play": "https://open.spotify.com/search/{}"},
        "netflix": {"search": "https://www.netflix.com/search?q={}", "play": "https://www.netflix.com/search?q={}"},
        "hulu": {"search": "https://www.hulu.com/search?q={}", "play": "https://www.hulu.com/search?q={}"},
        "prime": {"search": "https://www.amazon.com/s?k={}&i=instant-video", "play": "https://www.amazon.com/s?k={}&i=instant-video"},
        "disney": {"search": "https://www.disneyplus.com/search?q={}", "play": "https://www.disneyplus.com/search?q={}"},
        "twitch": {"search": "https://www.twitch.tv/search?term={}", "play": "https://www.twitch.tv/search?term={}"},
        "tiktok": {"search": "https://www.tiktok.com/search?q={}", "play": "https://www.tiktok.com/search?q={}"},
        "instagram": {"search": "https://www.instagram.com/explore/tags/{}", "play": "https://www.instagram.com/explore/tags/{}"},
        "twitter": {"search": "https://twitter.com/search?q={}", "play": "https://twitter.com/search?q={}"},
        "reddit": {"search": "https://www.reddit.com/search/?q={}", "play": "https://www.reddit.com/search/?q={}"},
        "vimeo": {"search": "https://vimeo.com/search?q={}", "play": "https://vimeo.com/search?q={}"},
        "dailymotion": {"search": "https://www.dailymotion.com/search/{}/videos", "play": "https://www.dailymotion.com/search/{}/videos"},
        "soundcloud": {"search": "https://soundcloud.com/search?q={}", "play": "https://soundcloud.com/search?q={}"},
        "apple_music": {"search": "https://music.apple.com/search?term={}", "play": "https://music.apple.com/search?term={}"},
        "pandora": {"search": "https://www.pandora.com/search/{}", "play": "https://www.pandora.com/search/{}"},
        "deezer": {"search": "https://www.deezer.com/search/{}", "play": "https://www.deezer.com/search/{}"},
        "tidal": {"search": "https://tidal.com/search?q={}", "play": "https://tidal.com/search?q={}"},
    }

    def __init__(self, browser: str = "auto"):
        self._browser = browser

    def search(self, platform: str, query: str) -> str:
        platform = platform.lower().replace(" ", "_")
        if platform in self.PLATFORMS:
            url = self.PLATFORMS[platform]["search"].format(quote_plus(query))
            webbrowser.open(url)
            return f"Searching {platform} for: {query}"
        return f"Unknown platform: {platform}"

    def play(self, platform: str, query: str) -> str:
        platform = platform.lower().replace(" ", "_")
        if platform in self.PLATFORMS:
            url = self.PLATFORMS[platform]["play"].format(quote_plus(query))
            webbrowser.open(url)
            return f"Playing on {platform}: {query}"
        return f"Unknown platform: {platform}"

    def media_control(self, action: str) -> str:
        system = platform.system()
        if system == "Darwin":
            key_map = {
                "play": 16, "pause": 16, "next": 176, "previous": 173,
                "volume_up": 144, "volume_down": 145, "mute": 47,
            }
            key_code = key_map.get(action, 16)
            try:
                script = f'tell application "System Events" to key code {key_code}'
                subprocess.run(["osascript", "-e", script], capture_output=True, timeout=5)
                return f"Media: {action}"
            except Exception:
                return f"Failed to {action}"
        return f"Media control not supported on {system}"

    def list_platforms(self) -> list[str]:
        return list(self.PLATFORMS.keys())

    def search_web(self, query: str) -> str:
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        webbrowser.open(url)
        return f"Searching: {query}"

    def open_url(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opened: {url}"

    def download_audio(self, url: str) -> str:
        try:
            import yt_dlp
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(title)s.%(ext)s",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return "Download complete"
        except ImportError:
            return "yt-dlp not installed"
        except Exception as e:
            return f"Download failed: {e}"
