# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ps99-bot.py'],
    pathex=['.'],
    binaries=[],
	datas = [
		('media/best-eggs-quest.png', 'media'),
		('media/buy-button.png', 'media'),
		('media/claim-button.png', 'media'), 
		('media/claim-rewards.png', 'media'), 
		('media/click-for-more.png', 'media'),
		('media/click-to-close.png', 'media'),
		('media/coin-jar-quest.png', 'media'), 
		('media/coin-jars-quest.png', 'media'), 
		('media/comet-quest.png', 'media'), 
		('media/comets-quest.png', 'media'), 
		('media/daily-gift-button.png', 'media'), 
		('media/e-button.png', 'media'),
		('media/logo.ico', 'media'),
		('media/lucky-block-quest.png', 'media'), 
		('media/ok-button.png', 'media'), 
		('media/pinata-quest.png', 'media'), 
		('media/pinatas-quest.png', 'media'), 
		('media/potion-quest.png', 'media'), 
		('media/rare-eggs-quest.png', 'media'),
		('media/redeem-button-1.png', 'media'), 
		('media/redeem-button-2.png', 'media'), 
		('media/redeem-button-3.png', 'media'), 
		('media/redeem-button-4.png', 'media'), 
		('media/tap-to-continue.png', 'media'), 
		('media/x-button.png', 'media')
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
	icon='media/logo.ico'
)
