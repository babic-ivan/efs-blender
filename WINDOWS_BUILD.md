# EasyFormStudio — Windows build

## Preduvjeti (jednokratno)

1. **Visual Studio 2022** (Community je dovoljan) s workloadom
   *Desktop development with C++* (uključi Windows 10/11 SDK).
2. **Git za Windows** (git-scm.com) — uključi Git LFS pri instalaciji.
3. **CMake** (cmake.org, dodaj u PATH) — VS-ov CMake također radi.

## Build

U **x64 Native Tools Command Prompt for VS 2022**:

```bat
cd %USERPROFILE%
git clone -b efs-blender-pub https://github.com/babic-ivan/efs-blender.git blender-efs
cd blender-efs

rem libovi i asseti se povlače s projects.blender.org (URL-ovi su apsolutni)
make update

make
```

Rezultat: `%USERPROFILE%\build_windows\bin\Release\` s `blender.exe` i
`blender-launcher.exe`. **To je očekivano** — CMake target se i dalje zove
blender. Installer preimenuje `blender-launcher.exe` (GUI wrapper, bez
konzolnog prozora) u `EasyFormStudio.exe`; `blender.exe` MORA zadržati svoje
ime jer ga launcher pokreće hardkodirano. Za ručno testiranje bez installera
pokreći `blender-launcher.exe`.

Napomena za ikone: `release\windows\icons\*.ico` se kompajlira u binarke pri
buildu — nakon povlačenja novog snapshota s izmijenjenim ikonama treba
ponovni `make` (relink je dovoljan, inkrementalni build to odradi).

## Bundlanje EFS + MeasureIt + Bool Tool

Ekstenzije se kopiraju iz lokalne Blender instalacije (instaliraj ih u
obični Blender na tom stroju, ili prenesi foldere s Maca) pa:

```bat
python build_files\utils\make_bundle_extensions.py ^
    --app %USERPROFILE%\build_windows\bin\Release ^
    --efs-src <putanja>\efs ^
    --measureit-src <putanja>\measureit ^
    --booltool-src <putanja>\bool_tool
```

Skripta sama nađe verzijski folder (`5.2`) i složi
`5.2\extensions\system\{efs,measureit,bool_tool}`; `apk` se nikad ne kopira.

## Installer (NSIS)

Bundlanje ekstenzija (korak iznad) MORA proći prije kompajliranja
installera — `efs_installer.nsi` odbija kompajlirati ako
`5.2\extensions\system\{efs,bool_tool}` ne postoje u build folderu.

1. Instaliraj **NSIS** (nsis.sourceforge.io).
2. Desni klik na `release\windows\efs_installer.nsi` → *Compile NSIS Script*
   (ili `makensis release\windows\efs_installer.nsi`).
3. Rezultat: `EasyFormStudio-2026-setup.exe` — instalira u
   `%ProgramFiles%\EasyFormStudio`, kreira prečace i uninstaller.

Napomena: `efs_installer.nsi` očekuje build u
`%USERPROFILE%\build_windows\bin\Release` — prilagodi `SRC_DIR` na vrhu
skripte ako je drugdje.

## Potpisivanje (kasnije)

Windows SmartScreen upozorenje nestaje s code-signing certifikatom
(OV/EV, npr. Certum/Sectigo) — `signtool sign /fd SHA256 /tr <timestamp>`
na setup.exe i EasyFormStudio.exe. Nije blokirajuće za interne testove.
