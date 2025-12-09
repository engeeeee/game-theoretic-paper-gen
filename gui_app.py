"""
Premium Academic Paper Generator GUI
Gray frosted glass effect with auto AI model detection
"""

import asyncio
import os
import sys
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import customtkinter as ctk
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent / ".env.example"
if env_path.exists():
    load_dotenv(env_path)
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Windows blur effect constants
try:
    from ctypes import windll, byref, c_int, sizeof, Structure, POINTER, c_byte
    from ctypes.wintypes import DWORD, ULONG
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

# ============================================================================
# CONSTANTS & THEME
# ============================================================================

class Theme:
    """Premium GRAY frosted glass theme"""
    # Base colors - TRUE GRAY tones for frosted glass
    BG_DARK = "#2d2d2d"      # Dark gray
    BG_MEDIUM = "#3a3a3a"    # Medium gray
    BG_LIGHT = "#4a4a4a"     # Light gray
    BG_GLASS = "#383838"     # Glass panel gray
    
    # Accent colors
    ACCENT = "#6366f1"       # Modern indigo
    ACCENT_HOVER = "#818cf8"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    
    # Text colors
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a1a1aa"
    TEXT_MUTED = "#71717a"
    
    # Glass effect - semi-transparent gray
    GLASS_BG = "#404040"     # Gray glass background
    GLASS_BORDER = "#525252" # Gray border
    GLASS_ALPHA = 0.75       # Transparency level
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_TITLE = 24
    FONT_SIZE_HEADER = 16
    FONT_SIZE_BODY = 13
    FONT_SIZE_SMALL = 11


# ============================================================================
# API PROVIDERS
# ============================================================================

class APIProvider(Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    XAI = "xai"
    MOONSHOT = "moonshot"
    ZHIPU = "zhipu"
    QWEN = "qwen"


# Default models for each provider - COMPLETE LATEST 2025 MODELS (Web Researched)
DEFAULT_MODELS = {
    APIProvider.OPENAI: [
        # ========== GPT-5.1 Series (November 2025) ==========
        "gpt-5.1", "gpt-5.1-chat-latest", "gpt-5.1-thinking", "gpt-5.1-pro",
        "gpt-5.1-auto", "gpt-5.1-instant", "gpt-5.1-codex-max",
        # ========== GPT-5 Series (August 2025) ==========
        "gpt-5", "gpt-5-chat", "gpt-5-mini", "gpt-5-nano",
        # ========== O-Series Reasoning ==========
        "o4-mini", "o4-mini-high",
        "o3", "o3-mini", "o3-pro",
        "o1", "o1-preview", "o1-mini", "o1-pro",
        # ========== GPT-4.1 Series ==========
        "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
        # ========== GPT-4.5 Series ==========
        "gpt-4.5", "gpt-4.5-turbo",
        # ========== GPT-4o Series ==========
        "gpt-4o", "gpt-4o-2024-11-20", "gpt-4o-mini", "gpt-4o-audio-preview",
        # ========== Image Generation ==========
        "gpt-image-1",
        # ========== Legacy ==========
        "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo",
    ],
    APIProvider.GOOGLE: [
        # ========== Gemini 3.0 (November 2025) ==========
        "gemini-3.0-pro", "gemini-3.0-pro-deep-think",
        # ========== Gemini 2.5 (June-September 2025) ==========
        "gemini-2.5-pro", "gemini-2.5-pro-exp", "gemini-2.5-flash",
        "gemini-2.5-flash-lite-preview",
        # ========== Gemini 2.0 (December 2024 - February 2025) ==========
        "gemini-2.0-flash-exp", "gemini-2.0-flash", "gemini-2.0-flash-lite",
        "gemini-2.0-pro-exp", "gemini-2.0-flash-thinking-exp",
        # ========== Experimental ==========
        "gemini-exp-1206", "gemini-exp-1121",
        # ========== Gemini 1.5 Series ==========
        "gemini-1.5-pro", "gemini-1.5-pro-002", "gemini-1.5-flash", "gemini-1.5-flash-8b",
    ],
    APIProvider.ANTHROPIC: [
        # ========== Claude Opus 4.5 (November 2025) ==========
        "claude-opus-4.5", "claude-opus-4.5-latest",
        # ========== Claude Sonnet 4.5 (September 2025) ==========
        "claude-sonnet-4.5", "claude-sonnet-4.5-latest",
        # ========== Claude Haiku 4.5 (October 2025) ==========
        "claude-haiku-4.5", "claude-haiku-4.5-latest",
        # ========== Claude Opus 4.1 (August 2025) ==========
        "claude-opus-4.1",
        # ========== Claude 4 (May 2025) ==========
        "claude-opus-4", "claude-sonnet-4",
        # ========== Claude 3.5 (2024) ==========
        "claude-3-5-sonnet-20241022", "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-20241022", "claude-3-5-haiku-latest",
        # ========== Claude 3 Series ==========
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307",
    ],
    APIProvider.DEEPSEEK: [
        # ========== DeepSeek V3.2 (December 2025) ==========
        "deepseek-chat",             # V3.2 general tasks
        "deepseek-reasoner",         # V3.2 reasoning mode
        "deepseek-v3.2-speciale",    # Competition-grade reasoning (temporary)
        # ========== R1 Series ==========
        "deepseek-r1", "deepseek-r1-distill",
        # ========== Specialized ==========
        "deepseek-coder", "deepseek-coder-v2",
    ],
    APIProvider.XAI: [
        # ========== Grok 4.1 (November 2025) ==========
        "grok-4.1", "grok-4.1-fast",
        # ========== Grok 4 (July 2025) ==========
        "grok-4", "grok-4-heavy", "grok-4-code", "grok-4-fast",
        # ========== Grok 3 (April 2025) ==========
        "grok-3", "grok-3-mini", "grok-3-fast",
        # ========== Grok 2 (2024) ==========
        "grok-2", "grok-2-latest", "grok-2-mini",
        "grok-beta", "grok-beta-vision",
    ],
    APIProvider.MOONSHOT: [
        # ========== Kimi K2 (July 2025) ==========
        "kimi-k2-instruct", "kimi-k2-base", "kimi-k2-thinking",
        # ========== Moonshot v1 (Kimi) ==========
        "moonshot-v1-128k", "moonshot-v1-32k", "moonshot-v1-8k",
    ],
    APIProvider.ZHIPU: [
        # ========== GLM-4.6 (Late 2024) ==========
        "glm-4.6",
        # ========== GLM-4 Series ==========
        "glm-4-plus", "glm-4", "glm-4-flash", "glm-4-air", "glm-4-airx", "glm-4-long",
        # ========== Multimodal ==========
        "glm-4-voice", "glm-4-vision",
    ],
    APIProvider.QWEN: [
        # ========== Qwen 3 Series (April 2025) ==========
        "qwen3-max", "qwen3-max-preview", "qwen3-max-thinking",
        "qwen3-plus", "qwen3-turbo",
        # ========== Qwen 2.5 Series (2024-2025) ==========
        "qwen-max", "qwen-max-2025-01-25", "qwen2.5-max",
        "qwen-plus", "qwen-plus-latest",
        "qwen-turbo", "qwen-turbo-latest",
        # ========== Long Context & Specialized ==========
        "qwen-long", "qwen2.5-1m",
        "qwen-coder-turbo", "qwen-math-turbo",
        # ========== Multimodal ==========
        "qwen2.5-vl",
    ],
}

# API base URLs
API_ENDPOINTS = {
    APIProvider.OPENAI: "https://api.openai.com/v1",
    APIProvider.GOOGLE: None,  # Uses SDK
    APIProvider.ANTHROPIC: "https://api.anthropic.com/v1",
    APIProvider.DEEPSEEK: "https://api.deepseek.com/v1",
    APIProvider.XAI: "https://api.x.ai/v1",
    APIProvider.MOONSHOT: "https://api.moonshot.cn/v1",
    APIProvider.ZHIPU: "https://open.bigmodel.cn/api/paas/v4",
    APIProvider.QWEN: "https://dashscope.aliyuncs.com/compatible-mode/v1",
}


# ============================================================================
# MODEL DETECTOR
# ============================================================================

class ModelDetector:
    """Auto-detect available models for all providers"""
    
    @staticmethod
    async def detect_models(provider: APIProvider, api_key: str) -> List[str]:
        """Detect available models for a provider"""
        if not api_key:
            return DEFAULT_MODELS.get(provider, [])
        
        try:
            if provider == APIProvider.OPENAI:
                return await ModelDetector._detect_openai(api_key)
            elif provider == APIProvider.GOOGLE:
                return await ModelDetector._detect_google(api_key)
            elif provider == APIProvider.ANTHROPIC:
                return await ModelDetector._detect_anthropic(api_key)
            elif provider in [APIProvider.DEEPSEEK, APIProvider.XAI, APIProvider.MOONSHOT, APIProvider.QWEN]:
                return await ModelDetector._detect_openai_compatible(provider, api_key)
            elif provider == APIProvider.ZHIPU:
                return await ModelDetector._detect_zhipu(api_key)
            else:
                return DEFAULT_MODELS.get(provider, [])
        except Exception as e:
            print(f"Model detection failed for {provider}: {e}")
            return DEFAULT_MODELS.get(provider, [])
    
    @staticmethod
    async def _detect_openai(api_key: str) -> List[str]:
        """Detect OpenAI models"""
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
                # Filter for chat models
                chat_models = [m for m in models if any(x in m for x in ["gpt-4", "gpt-3.5", "o1", "o3"])]
                return sorted(chat_models, reverse=True)[:20] if chat_models else DEFAULT_MODELS[APIProvider.OPENAI]
        return DEFAULT_MODELS[APIProvider.OPENAI]
    
    @staticmethod
    async def _detect_google(api_key: str) -> List[str]:
        """Detect Google Gemini models"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            models = []
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    name = m.name.replace("models/", "")
                    models.append(name)
            return models if models else DEFAULT_MODELS[APIProvider.GOOGLE]
        except Exception:
            return DEFAULT_MODELS[APIProvider.GOOGLE]
    
    @staticmethod
    async def _detect_anthropic(api_key: str) -> List[str]:
        """Anthropic doesn't have a list endpoint, return defaults"""
        return DEFAULT_MODELS[APIProvider.ANTHROPIC]
    
    @staticmethod
    async def _detect_openai_compatible(provider: APIProvider, api_key: str) -> List[str]:
        """Detect models for OpenAI-compatible APIs"""
        import httpx
        base_url = API_ENDPOINTS.get(provider)
        if not base_url:
            return DEFAULT_MODELS.get(provider, [])
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{base_url}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m["id"] for m in data.get("data", [])]
                    return models if models else DEFAULT_MODELS.get(provider, [])
            except Exception:
                pass
        return DEFAULT_MODELS.get(provider, [])
    
    @staticmethod
    async def _detect_zhipu(api_key: str) -> List[str]:
        """Zhipu uses different auth, return defaults"""
        return DEFAULT_MODELS[APIProvider.ZHIPU]


# ============================================================================
# WINDOWS BLUR EFFECT - ENHANCED ACRYLIC
# ============================================================================

def apply_windows_blur(hwnd: int, color_hex: str = "#2d2d2d", alpha: int = 180):
    """
    Apply Windows acrylic/blur effect for frosted glass appearance.
    Works on Windows 10 1803+ and Windows 11.
    """
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        # Step 1: Enable dark mode for window
        value = c_int(1)
        windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 20, byref(value), sizeof(value)  # DWMWA_USE_IMMERSIVE_DARK_MODE
        )
    except Exception:
        pass
    
    try:
        # Step 2: Try Windows 11 Acrylic (best effect)
        # DWMWA_SYSTEMBACKDROP_TYPE = 38
        # Values: 0=Auto, 1=None, 2=Mica, 3=Acrylic, 4=Tabbed
        backdrop_type = c_int(3)  # Acrylic
        result = windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 38, byref(backdrop_type), sizeof(backdrop_type)
        )
        if result == 0:  # S_OK
            return True
    except Exception:
        pass
    
    try:
        # Step 3: Fallback to Windows 10 style ACCENT_POLICY
        class ACCENT_POLICY(Structure):
            _fields_ = [
                ("AccentState", DWORD),
                ("AccentFlags", DWORD),
                ("GradientColor", DWORD),
                ("AnimationId", DWORD),
            ]
        
        class WINDOWCOMPOSITIONATTRIBDATA(Structure):
            _fields_ = [
                ("Attribute", DWORD),
                ("Data", POINTER(ACCENT_POLICY)),
                ("SizeOfData", ULONG),
            ]
        
        # Parse hex color to AABBGGRR format
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        # Windows uses AABBGGRR format
        gradient_color = (alpha << 24) | (b << 16) | (g << 8) | r
        
        accent = ACCENT_POLICY()
        # AccentState values:
        # 0 = ACCENT_DISABLED
        # 1 = ACCENT_ENABLE_GRADIENT
        # 2 = ACCENT_ENABLE_TRANSPARENTGRADIENT
        # 3 = ACCENT_ENABLE_BLURBEHIND
        # 4 = ACCENT_ENABLE_ACRYLICBLURBEHIND (Windows 10 1803+)
        # 5 = ACCENT_ENABLE_HOSTBACKDROP (Windows 11)
        accent.AccentState = 4  # ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 2  # ACCENT_FLAG_DRAW_ALL
        accent.GradientColor = gradient_color
        accent.AnimationId = 0
        
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.Data = POINTER(ACCENT_POLICY)(accent)
        data.SizeOfData = sizeof(accent)
        
        # SetWindowCompositionAttribute is undocumented but works
        set_window_composition = windll.user32.SetWindowCompositionAttribute
        set_window_composition(hwnd, byref(data))
        
        return True
    except Exception as e:
        print(f"Blur effect failed: {e}")
        return False


def get_hwnd(widget) -> int:
    """Get the Windows HWND for a tkinter widget."""
    try:
        return windll.user32.GetParent(widget.winfo_id())
    except Exception:
        return 0


# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class GlassFrame(ctk.CTkFrame):
    """Semi-transparent glass-effect frame"""
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", Theme.GLASS_BG)
        kwargs.setdefault("border_color", Theme.GLASS_BORDER)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)


class GlassButton(ctk.CTkButton):
    """Premium styled button"""
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", Theme.ACCENT)
        kwargs.setdefault("hover_color", Theme.ACCENT_HOVER)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", (Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY, "bold"))
        super().__init__(master, **kwargs)


class GlassEntry(ctk.CTkEntry):
    """Premium styled entry"""
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", Theme.BG_DARK)
        kwargs.setdefault("border_color", Theme.GLASS_BORDER)
        kwargs.setdefault("text_color", Theme.TEXT_PRIMARY)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", (Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY))
        super().__init__(master, **kwargs)


class GlassTextbox(ctk.CTkTextbox):
    """Premium styled textbox"""
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", Theme.BG_DARK)
        kwargs.setdefault("border_color", Theme.GLASS_BORDER)
        kwargs.setdefault("text_color", Theme.TEXT_PRIMARY)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", (Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY))
        super().__init__(master, **kwargs)


class GlassOptionMenu(ctk.CTkOptionMenu):
    """Premium styled dropdown"""
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", Theme.BG_DARK)
        kwargs.setdefault("button_color", Theme.ACCENT)
        kwargs.setdefault("button_hover_color", Theme.ACCENT_HOVER)
        kwargs.setdefault("dropdown_fg_color", Theme.GLASS_BG)
        kwargs.setdefault("dropdown_hover_color", Theme.BG_LIGHT)
        kwargs.setdefault("corner_radius", 8)
        kwargs.setdefault("font", (Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY))
        super().__init__(master, **kwargs)


class StatusIndicator(ctk.CTkFrame):
    """Animated status indicator"""
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.dot = ctk.CTkLabel(self, text="●", font=(Theme.FONT_FAMILY, 12))
        self.dot.pack(side="left", padx=(0, 5))
        self.label = ctk.CTkLabel(self, text="Ready", font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL))
        self.label.pack(side="left")
        self.set_status("ready")
    
    def set_status(self, status: str, text: str = None):
        colors = {
            "ready": Theme.SUCCESS,
            "working": Theme.WARNING,
            "warning": Theme.WARNING,  # For API key warnings
            "error": Theme.ERROR,
            "success": Theme.SUCCESS,
        }
        self.dot.configure(text_color=colors.get(status, Theme.TEXT_MUTED))
        if text:
            self.label.configure(text=text)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class AcademicPaperGeneratorApp(ctk.CTk):
    """Premium Academic Paper Generator with Frosted Glass UI"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Academic Paper Generator")
        self.geometry("1200x800")
        self.minsize(900, 600)
        
        # Set dark appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Configure colors
        self.configure(fg_color=Theme.BG_DARK)
        
        # Apply blur after window is mapped
        self.after(100, self._apply_blur)
        
        # State variables
        self.agent_a_models: List[str] = []
        self.agent_b_models: List[str] = []
        self.is_generating = False
        
        # Build UI
        self._create_header()
        self._create_tabs()
        self._create_status_bar()
        
        # Load saved config
        self._load_config()
    
    def _apply_blur(self):
        """Apply Windows blur effect"""
        try:
            hwnd = windll.user32.GetParent(self.winfo_id())
            apply_windows_blur(hwnd, Theme.BG_DARK, 220)
        except Exception:
            pass
    
    def _create_header(self):
        """Create app header"""
        header = GlassFrame(self, height=70)
        header.pack(fill="x", padx=15, pady=(15, 10))
        header.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(
            header,
            text="🎓 Academic Paper Generator",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_TITLE, "bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(side="left", padx=20, pady=15)
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            header,
            text="Game-Theoretic Multi-Agent Verification System",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
            text_color=Theme.TEXT_MUTED
        )
        subtitle.pack(side="left", pady=15)
    
    def _create_tabs(self):
        """Create main tab view"""
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=Theme.GLASS_BG,
            segmented_button_fg_color=Theme.BG_DARK,
            segmented_button_selected_color=Theme.ACCENT,
            segmented_button_unselected_color=Theme.BG_MEDIUM,
            corner_radius=12
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Add tabs
        self.tab_settings = self.tabview.add("⚙️ Settings")
        self.tab_input = self.tabview.add("📝 Input")
        self.tab_output = self.tabview.add("📄 Output")
        
        # Build each tab
        self._build_settings_tab()
        self._build_input_tab()
        self._build_output_tab()
        
        # Default to Input tab
        self.tabview.set("📝 Input")
    
    def _build_settings_tab(self):
        """Build settings tab content"""
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self.tab_settings, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === Agent A Configuration ===
        self._create_agent_config(scroll, "A", "Proponent")
        
        # Spacer
        ctk.CTkLabel(scroll, text="", height=20).pack()
        
        # === Agent B Configuration ===
        self._create_agent_config(scroll, "B", "Reviewer")
        
        # Spacer
        ctk.CTkLabel(scroll, text="", height=20).pack()
        
        # === Advanced Settings ===
        adv_frame = GlassFrame(scroll)
        adv_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            adv_frame,
            text="⚡ Advanced Settings",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_HEADER, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        settings_grid = ctk.CTkFrame(adv_frame, fg_color="transparent")
        settings_grid.pack(fill="x", padx=15, pady=(0, 15))
        
        # Max Rounds
        ctk.CTkLabel(settings_grid, text="Max Debate Rounds:", text_color=Theme.TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=5)
        self.max_rounds_var = ctk.StringVar(value="5")
        ctk.CTkEntry(settings_grid, textvariable=self.max_rounds_var, width=100, fg_color=Theme.BG_DARK).grid(row=0, column=1, padx=10, pady=5)
        
        # Strictness
        ctk.CTkLabel(settings_grid, text="Strictness:", text_color=Theme.TEXT_SECONDARY).grid(row=1, column=0, sticky="w", pady=5)
        self.strictness_var = ctk.StringVar(value="high")
        GlassOptionMenu(settings_grid, values=["low", "medium", "high"], variable=self.strictness_var, width=150).grid(row=1, column=1, padx=10, pady=5)
    
    def _create_agent_config(self, parent, agent_id: str, role: str):
        """Create agent configuration section"""
        frame = GlassFrame(parent)
        frame.pack(fill="x", pady=5)
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text=f"🤖 Agent {agent_id} ({role})",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_HEADER, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Grid for inputs
        grid = ctk.CTkFrame(frame, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=(0, 15))
        grid.columnconfigure(1, weight=1)
        
        # Provider
        ctk.CTkLabel(grid, text="Provider:", text_color=Theme.TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=8)
        provider_var = ctk.StringVar(value="openai")
        provider_menu = GlassOptionMenu(
            grid,
            values=[p.value for p in APIProvider],
            variable=provider_var,
            width=180,
            command=lambda v, a=agent_id: self._on_provider_change(a, v)
        )
        provider_menu.grid(row=0, column=1, sticky="w", padx=10, pady=8)
        
        # API Key
        ctk.CTkLabel(grid, text="API Key:", text_color=Theme.TEXT_SECONDARY).grid(row=1, column=0, sticky="w", pady=8)
        api_key_entry = GlassEntry(grid, show="•", width=350)
        api_key_entry.grid(row=1, column=1, sticky="w", padx=10, pady=8)
        # Bind key release to update status
        api_key_entry.bind("<KeyRelease>", lambda e: self._update_api_status())
        
        # Model selection row
        ctk.CTkLabel(grid, text="Model:", text_color=Theme.TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=8)
        
        model_frame = ctk.CTkFrame(grid, fg_color="transparent")
        model_frame.grid(row=2, column=1, sticky="w", padx=10, pady=8)
        
        model_var = ctk.StringVar(value="gpt-4o")
        model_menu = GlassOptionMenu(model_frame, values=["gpt-4o"], variable=model_var, width=250)
        model_menu.pack(side="left")
        
        detect_btn = GlassButton(
            model_frame,
            text="🔍 Detect",
            width=100,
            command=lambda a=agent_id: self._detect_models(a)
        )
        detect_btn.pack(side="left", padx=10)
        
        # Store references
        if agent_id == "A":
            self.agent_a_provider = provider_var
            self.agent_a_api_key = api_key_entry
            self.agent_a_model = model_var
            self.agent_a_model_menu = model_menu
        else:
            self.agent_b_provider = provider_var
            self.agent_b_api_key = api_key_entry
            self.agent_b_model = model_var
            self.agent_b_model_menu = model_menu
    
    def _build_input_tab(self):
        """Build input tab content"""
        # Mode selector
        mode_frame = GlassFrame(self.tab_input)
        mode_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            mode_frame,
            text="📋 Generation Mode",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_HEADER, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        mode_inner = ctk.CTkFrame(mode_frame, fg_color="transparent")
        mode_inner.pack(fill="x", padx=15, pady=(0, 15))
        
        self.mode_var = ctk.StringVar(value="smart")
        modes = [
            ("verify", "🔍 Verify", "Verify a claim through adversarial debate"),
            ("write", "📝 Write", "Write a paper from structured requirements"),
            ("smart", "🧠 Smart", "Intelligently understand any format of requirements"),
        ]
        
        for i, (value, label, desc) in enumerate(modes):
            btn = ctk.CTkRadioButton(
                mode_inner,
                text=f"{label}\n{desc}",
                variable=self.mode_var,
                value=value,
                fg_color=Theme.ACCENT,
                font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_BODY)
            )
            btn.pack(side="left", padx=20, pady=5)
        
        # Requirements input
        req_frame = GlassFrame(self.tab_input)
        req_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            req_frame,
            text="📄 Requirements / Question",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_HEADER, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.input_text = GlassTextbox(req_frame, height=200)
        self.input_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.input_text.insert("0.0", "Enter your research question or paper requirements here...\n\nExamples:\n• Write a 3000-word essay on climate change using APA format\n• Is the methodology in recent AI papers reliable?\n• 我需要一篇关于区块链的论文，大概5000字")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(req_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.generate_btn = GlassButton(
            btn_frame,
            text="🚀 Generate",
            width=150,
            height=40,
            command=self._start_generation
        )
        self.generate_btn.pack(side="left")
        
        self.stop_btn = GlassButton(
            btn_frame,
            text="⏹ Stop",
            width=100,
            height=40,
            fg_color=Theme.ERROR,
            hover_color="#ff6b6b",
            state="disabled",
            command=self._stop_generation
        )
        self.stop_btn.pack(side="left", padx=10)
        
        # Options
        opt_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
        opt_frame.pack(side="right")
        
        self.gen_paper_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            opt_frame,
            text="Generate Paper",
            variable=self.gen_paper_var,
            fg_color=Theme.ACCENT
        ).pack(side="left", padx=10)
    
    def _build_output_tab(self):
        """Build output tab content"""
        # Results area
        result_frame = GlassFrame(self.tab_output)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with export buttons
        header = ctk.CTkFrame(result_frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            header,
            text="📊 Results",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_HEADER, "bold"),
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")
        
        # Export buttons
        export_frame = ctk.CTkFrame(header, fg_color="transparent")
        export_frame.pack(side="right")
        
        GlassButton(
            export_frame,
            text="📝 Export MD",
            width=100,
            command=lambda: self._export("md")
        ).pack(side="left", padx=5)
        
        GlassButton(
            export_frame,
            text="📄 Export Word",
            width=110,
            command=lambda: self._export("docx")
        ).pack(side="left", padx=5)
        
        # Output text
        self.output_text = GlassTextbox(result_frame, height=400)
        self.output_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.output_text.insert("0.0", "Results will appear here after generation...")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(result_frame, fg_color=Theme.BG_DARK, progress_color=Theme.ACCENT)
        self.progress.pack(fill="x", padx=15, pady=(0, 15))
        self.progress.set(0)
    
    def _create_status_bar(self):
        """Create bottom status bar"""
        status_bar = ctk.CTkFrame(self, fg_color=Theme.BG_MEDIUM, height=30)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        
        self.status_indicator = StatusIndicator(status_bar)
        self.status_indicator.pack(side="left", padx=15, pady=5)
        
        # Creator & Version info
        ctk.CTkLabel(
            status_bar,
            text="v2.0 | By Enge1337 | Powered by Multi-Agent AI",
            font=(Theme.FONT_FAMILY, Theme.FONT_SIZE_SMALL),
            text_color=Theme.TEXT_MUTED
        ).pack(side="right", padx=15, pady=5)
    
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    
    def _on_provider_change(self, agent_id: str, provider: str):
        """Handle provider change"""
        try:
            provider_enum = APIProvider(provider)
            defaults = DEFAULT_MODELS.get(provider_enum, [])
            
            if agent_id == "A":
                self.agent_a_model_menu.configure(values=defaults)
                if defaults:
                    self.agent_a_model.set(defaults[0])
            else:
                self.agent_b_model_menu.configure(values=defaults)
                if defaults:
                    self.agent_b_model.set(defaults[0])
        except Exception as e:
            print(f"Provider change error: {e}")
    
    def _detect_models(self, agent_id: str):
        """Detect available models for an agent"""
        self.status_indicator.set_status("working", "Detecting models...")
        
        def run_detection():
            try:
                if agent_id == "A":
                    provider = APIProvider(self.agent_a_provider.get())
                    api_key = self.agent_a_api_key.get()
                else:
                    provider = APIProvider(self.agent_b_provider.get())
                    api_key = self.agent_b_api_key.get()
                
                # Run async detection
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                models = loop.run_until_complete(ModelDetector.detect_models(provider, api_key))
                loop.close()
                
                # Update UI in main thread
                self.after(0, lambda: self._update_models(agent_id, models))
            except Exception as e:
                self.after(0, lambda: self.status_indicator.set_status("error", f"Detection failed: {e}"))
        
        threading.Thread(target=run_detection, daemon=True).start()
    
    def _update_models(self, agent_id: str, models: List[str]):
        """Update model dropdown with detected models"""
        if models:
            if agent_id == "A":
                self.agent_a_model_menu.configure(values=models)
                self.agent_a_model.set(models[0])
            else:
                self.agent_b_model_menu.configure(values=models)
                self.agent_b_model.set(models[0])
            self.status_indicator.set_status("success", f"Found {len(models)} models")
        else:
            self.status_indicator.set_status("error", "No models found")
    
    def _start_generation(self):
        """Start paper generation"""
        if self.is_generating:
            return
        
        self.is_generating = True
        self.generate_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_indicator.set_status("working", "Generating...")
        self.progress.set(0)
        
        # Clear output
        self.output_text.delete("0.0", "end")
        
        # Get input
        input_text = self.input_text.get("0.0", "end").strip()
        mode = self.mode_var.get()
        
        def run_generation():
            try:
                self._save_config()
                
                # Import core modules
                from src.agents.proponent import ProponentAgent
                from src.agents.reviewer import ReviewerAgent
                from src.engine.adaptive_debate import AdaptiveDebateEngine
                from src.output.consensus import ConsensusGenerator
                from src.output.paper_generator import PaperGenerator
                from src.input.intelligent_analyzer import IntelligentAnalyzer
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                self.after(0, lambda: self.progress.set(0.1))
                self.after(0, lambda: self._append_output("🚀 Starting generation...\n\n"))
                
                # Initialize agents
                proponent = ProponentAgent()
                reviewer = ReviewerAgent(strictness=self.strictness_var.get())
                
                self.after(0, lambda: self.progress.set(0.2))
                self.after(0, lambda: self._append_output("✓ Agents initialized\n"))
                
                if mode == "smart" or mode == "write":
                    # Smart/Write mode: Generate actual paper content
                    self.after(0, lambda: self._append_output("🧠 Analyzing requirements...\n"))
                    analyzer = IntelligentAnalyzer()
                    requirements = loop.run_until_complete(analyzer.analyze(input_text))
                    question = requirements.topic if requirements.topic else input_text
                    self.after(0, lambda: self._append_output(f"📋 Topic: {question}\n"))
                    
                    self.after(0, lambda: self.progress.set(0.4))
                    
                    # Generate actual paper content using LLM
                    self.after(0, lambda: self._append_output("\n📝 Generating paper content...\n"))
                    self.after(0, lambda: self._append_output("(This may take 1-2 minutes for longer papers)\n\n"))
                    
                    paper_gen = PaperGenerator()
                    paper_content = loop.run_until_complete(
                        paper_gen.generate_full_paper(requirements)
                    )
                    
                    self.after(0, lambda: self.progress.set(0.8))
                    
                    # Display generated paper
                    self.after(0, lambda: self._append_output("\n" + "="*60 + "\n"))
                    self.after(0, lambda: self._append_output("📄 GENERATED PAPER\n"))
                    self.after(0, lambda: self._append_output("="*60 + "\n\n"))
                    self.after(0, lambda: self._append_output(paper_content))
                    
                    # Save paper to output folder
                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)
                    paper_gen.export_to_formats(paper_content, str(output_dir))
                    self.after(0, lambda: self._append_output(f"\n\n✓ Paper saved to {output_dir}\n"))
                    
                elif mode == "verify":
                    # Verify mode: Run debate and generate verification report
                    question = input_text
                    
                    self.after(0, lambda: self.progress.set(0.3))
                    
                    # Run adversarial debate for verification
                    self.after(0, lambda: self._append_output("\n⚔️ Running adversarial debate...\n"))
                    engine = AdaptiveDebateEngine(proponent, reviewer, max_rounds=int(self.max_rounds_var.get()))
                    result = loop.run_until_complete(engine.run_debate(question))
                    
                    self.after(0, lambda: self.progress.set(0.6))
                    self.after(0, lambda: self._append_output(f"✓ Debate completed in {result.total_rounds} rounds\n"))
                    self.after(0, lambda: self._append_output(f"📊 Final Score: {result.final_score:.1f}/100\n"))
                    
                    # Generate consensus
                    self.after(0, lambda: self._append_output("\n🤝 Generating consensus...\n"))
                    consensus_gen = ConsensusGenerator()
                    consensus = consensus_gen.generate(result)
                    
                    self.after(0, lambda: self.progress.set(0.8))
                    
                    # Generate verification report if paper generation requested
                    if self.gen_paper_var.get():
                        self.after(0, lambda: self._append_output("\n📄 Generating verification report...\n"))
                        paper_gen = PaperGenerator()
                        paper_content = paper_gen.generate_paper(
                            question, 
                            result, 
                            consensus, 
                            result.voting_result
                        )
                        
                        self.after(0, lambda: self._append_output("\n" + "="*60 + "\n"))
                        self.after(0, lambda: self._append_output("VERIFICATION REPORT\n"))
                        self.after(0, lambda: self._append_output("="*60 + "\n\n"))
                        self.after(0, lambda: self._append_output(paper_content))
                        
                        # Save report
                        output_dir = Path("output")
                        output_dir.mkdir(exist_ok=True)
                        paper_gen.export_to_formats(paper_content, str(output_dir))
                        self.after(0, lambda: self._append_output(f"\n\n✓ Report saved to {output_dir}\n"))
                    else:
                        # Just show consensus
                        self.after(0, lambda: self._append_output(f"\n📋 Verdict: {consensus.verdict}\n"))
                        self.after(0, lambda: self._append_output(f"🎯 Confidence: {consensus.confidence:.1f}%\n"))

                
                loop.close()
                
                self.after(0, lambda: self.progress.set(1.0))
                self.after(0, lambda: self.status_indicator.set_status("success", "Generation complete!"))
                
            except Exception as e:
                import traceback
                error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
                self.after(0, lambda: self._append_output(f"\n❌ {error_msg}"))
                self.after(0, lambda: self.status_indicator.set_status("error", str(e)[:50]))
            finally:
                self.after(0, self._generation_complete)
        
        self.generation_thread = threading.Thread(target=run_generation, daemon=True)
        self.generation_thread.start()
    
    def _append_output(self, text: str):
        """Append text to output"""
        self.output_text.insert("end", text)
        self.output_text.see("end")
    
    def _generation_complete(self):
        """Clean up after generation"""
        self.is_generating = False
        self.generate_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
    
    def _stop_generation(self):
        """Stop current generation"""
        self.is_generating = False
        self.status_indicator.set_status("ready", "Stopped")
        self._generation_complete()
    
    def _export(self, format: str):
        """Export results"""
        from tkinter import filedialog
        
        content = self.output_text.get("0.0", "end")
        
        if format == "md":
            filepath = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown", "*.md"), ("All files", "*.*")]
            )
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_indicator.set_status("success", f"Saved to {Path(filepath).name}")
        
        elif format == "docx":
            try:
                from docx import Document
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".docx",
                    filetypes=[("Word Document", "*.docx"), ("All files", "*.*")]
                )
                if filepath:
                    doc = Document()
                    for para in content.split("\n\n"):
                        doc.add_paragraph(para)
                    doc.save(filepath)
                    self.status_indicator.set_status("success", f"Saved to {Path(filepath).name}")
            except ImportError:
                self.status_indicator.set_status("error", "python-docx not installed")
    
    def _save_config(self):
        """Save current configuration to environment"""
        os.environ["AGENT_A_PROVIDER"] = self.agent_a_provider.get()
        os.environ["AGENT_A_API_KEY"] = self.agent_a_api_key.get()
        os.environ["AGENT_A_MODEL"] = self.agent_a_model.get()
        
        os.environ["AGENT_B_PROVIDER"] = self.agent_b_provider.get()
        os.environ["AGENT_B_API_KEY"] = self.agent_b_api_key.get()
        os.environ["AGENT_B_MODEL"] = self.agent_b_model.get()
        
        os.environ["MAX_DEBATE_ROUNDS"] = self.max_rounds_var.get()
    
    def _load_config(self):
        """Load configuration from environment"""
        # Agent A
        if os.getenv("AGENT_A_PROVIDER"):
            self.agent_a_provider.set(os.getenv("AGENT_A_PROVIDER"))
        if os.getenv("AGENT_A_API_KEY"):
            self.agent_a_api_key.insert(0, os.getenv("AGENT_A_API_KEY"))
        if os.getenv("AGENT_A_MODEL"):
            self.agent_a_model.set(os.getenv("AGENT_A_MODEL"))
        
        # Agent B
        if os.getenv("AGENT_B_PROVIDER"):
            self.agent_b_provider.set(os.getenv("AGENT_B_PROVIDER"))
        if os.getenv("AGENT_B_API_KEY"):
            self.agent_b_api_key.insert(0, os.getenv("AGENT_B_API_KEY"))
        if os.getenv("AGENT_B_MODEL"):
            self.agent_b_model.set(os.getenv("AGENT_B_MODEL"))
        
        # Trigger provider change to load default models
        self._on_provider_change("A", self.agent_a_provider.get())
        self._on_provider_change("B", self.agent_b_provider.get())
        
        # Check API keys and update status
        self._update_api_status()
    
    def _update_api_status(self):
        """Update status indicator based on API key availability"""
        api_a = self.agent_a_api_key.get().strip()
        api_b = self.agent_b_api_key.get().strip()
        
        if not api_a and not api_b:
            self.status_indicator.set_status("warning", "⚠️ Please fill API keys in Settings")
        elif not api_a:
            self.status_indicator.set_status("warning", "⚠️ Agent A API key missing")
        elif not api_b:
            self.status_indicator.set_status("warning", "⚠️ Agent B API key missing")
        else:
            self.status_indicator.set_status("ready", "✓ Ready")


# ============================================================================
# MAIN ENTRY
# ============================================================================

if __name__ == "__main__":
    app = AcademicPaperGeneratorApp()
    app.mainloop()
