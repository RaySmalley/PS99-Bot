# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ps99-bot.py'],
    pathex=['.'],
    binaries=[],
	datas = [
		('media/claim-button.png', '.'), 
		('media/claim-rewards.png', '.'), 
		('media/click-for-more.png', '.'), 
		('media/coin-jar-quest.png', '.'), 
		('media/coin-jars-quest.png', '.'), 
		('media/comet-quest.png', '.'), 
		('media/comets-quest.png', '.'), 
		('media/daily-gift-button.png', '.'), 
		('media/lucky-block-quest.png', '.'), 
		('media/ok-button.png', '.'), 
		('media/pinata-quest.png', '.'), 
		('media/pinatas-quest.png', '.'), 
		('media/potion-quest.png', '.'), 
		('media/redeem-button.png', '.'), 
		('media/x-button.png', '.')
	],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ps99-bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
	icon='logo.ico'
)
