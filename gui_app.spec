# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Academic Paper Generator GUI
Premium frosted glass UI with auto model detection
"""

import sys
from pathlib import Path

block_cipher = None

# Get customtkinter path for data files
import customtkinter
ctk_path = Path(customtkinter.__file__).parent

a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include customtkinter themes and assets
        (str(ctk_path), 'customtkinter'),
        # Include .env.example for default config
        ('.env.example', '.'),
        # Include src package
        ('src', 'src'),
    ],
    hiddenimports=[
        # Core
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        
        # API clients
        'openai',
        'google.generativeai',
        'anthropic',
        'httpx',
        'aiohttp',
        
        # Application modules
        'src',
        'src.agents',
        'src.agents.base_agent',
        'src.agents.proponent',
        'src.agents.reviewer',
        'src.engine',
        'src.engine.adaptive_debate',
        'src.engine.scoring',
        'src.engine.voting',
        'src.output',
        'src.output.consensus',
        'src.output.paper_generator',
        'src.output.report',
        'src.input',
        'src.input.requirements_parser',
        'src.input.intelligent_analyzer',
        'src.citation_moat',
        'src.citation_moat.moat_engine',
        'src.citation_moat.extractor',
        'src.citation_moat.web_validator',
        'src.anti_hallucination',
        
        # Other dependencies
        'pydantic',
        'dotenv',
        'click',
        'rich',
        'docx',
        'requests',
        'bs4',
        'lxml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter.test',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AcademicPaperGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - pure GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if available
)
