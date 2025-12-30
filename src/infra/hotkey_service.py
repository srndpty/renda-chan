"""Global hotkey registration service."""

from __future__ import annotations

from collections.abc import Callable

try:  # pragma: no cover - optional dependency
    from pynput import keyboard as pynput_keyboard
except ImportError:  # pragma: no cover - optional dependency
    pynput_keyboard = None

try:  # pragma: no cover - optional dependency
    import keyboard as keyboard_module
except ImportError:  # pragma: no cover - optional dependency
    keyboard_module = None


_ESCAPE_TOKENS = {"esc", "escape"}
_MODIFIER_ALIASES = {
    "control": "ctrl",
    "ctl": "ctrl",
    "command": "meta",
    "cmd": "meta",
    "win": "meta",
    "windows": "meta",
    "option": "alt",
}


class HotkeyService:
    """Register and manage a global start/stop hotkey."""

    def __init__(self, on_trigger: Callable[[], None]) -> None:
        if pynput_keyboard is None and keyboard_module is None:
            raise RuntimeError("pynput または keyboard のいずれかをインストールしてください。")
        self._on_trigger = on_trigger
        self._backend = "pynput" if pynput_keyboard is not None else "keyboard"
        self._listener: object | None = None
        self._keyboard_handle: int | None = None

    @property
    def backend_name(self) -> str:
        """Return the backend in use."""
        return self._backend

    def register(self, hotkey: str) -> None:
        """Register a global hotkey, replacing any existing registration."""
        self.unregister()

        hotkey = hotkey.strip()
        if not hotkey:
            return

        tokens = _tokenize_hotkey(hotkey)
        if not tokens:
            raise ValueError("ホットキーが空です。")
        if any(token in _ESCAPE_TOKENS for token in tokens):
            raise ValueError("Esc キーはホットキーに利用できません。")
        if not _has_non_modifier(tokens):
            raise ValueError("修飾キーのみのホットキーは登録できません。")

        formatted = _format_hotkey(tokens, self._backend)
        if self._backend == "pynput":
            listener = pynput_keyboard.GlobalHotKeys({formatted: self._on_trigger})
            listener.start()
            self._listener = listener
        else:
            self._keyboard_handle = keyboard_module.add_hotkey(formatted, self._on_trigger)

    def unregister(self) -> None:
        """Remove any existing hotkey registration."""
        if self._backend == "pynput":
            listener = self._listener
            if listener is not None:
                listener.stop()
                self._listener = None
        else:
            if self._keyboard_handle is not None:
                keyboard_module.remove_hotkey(self._keyboard_handle)
                self._keyboard_handle = None


def _tokenize_hotkey(hotkey: str) -> list[str]:
    normalized = (
        hotkey.replace("⌘", "Meta")
        .replace("⌥", "Alt")
        .replace("⇧", "Shift")
        .replace("⌃", "Ctrl")
    )
    return [token.strip().lower() for token in normalized.replace("-", "+").split("+") if token.strip()]


def _has_non_modifier(tokens: list[str]) -> bool:
    return any(token not in {"ctrl", "alt", "shift", "meta"} for token in tokens)


def _format_hotkey(tokens: list[str], backend: str) -> str:
    modifiers: list[str] = []
    keys: list[str] = []
    for token in tokens:
        normalized = _MODIFIER_ALIASES.get(token, token)
        if normalized in {"ctrl", "alt", "shift", "meta"}:
            modifiers.append(normalized)
        else:
            keys.append(normalized)

    if backend == "keyboard":
        modifier_map = {
            "ctrl": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "meta": "windows",
        }
    else:
        modifier_map = {
            "ctrl": "<ctrl>",
            "alt": "<alt>",
            "shift": "<shift>",
            "meta": "<cmd>",
        }

    parts = [modifier_map[mod] for mod in modifiers] + keys
    return "+".join(parts)
