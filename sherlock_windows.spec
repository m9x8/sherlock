# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# We collect any specific resources we want, especially data.json
datas = [
    ('sherlock_project/resources/data.json', 'sherlock_project/resources'),
    ('sherlock_project/resources/data.schema.json', 'sherlock_project/resources'),
]

# Collecting hiddenimports
hidden_imports = [
    'customtkinter',
    'phonenumbers',
    'docx',
    'reportlab',
    'reportlab.lib',
    'reportlab.lib.pagesizes',
    'reportlab.lib.colors',
    'reportlab.lib.units',
    'reportlab.platypus',
    'reportlab.lib.styles',
    'pandas',
    'openpyxl',
    'tomli',
    'dns',
    'whois',
    'shodan',
    'holehe',
    'socialscan'
]

a = Analysis(
    ['sherlock_project/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SherlockProfessional',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # Set to False so it launches purely as a GUI without command prompt windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
