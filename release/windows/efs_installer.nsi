; EasyFormStudio NSIS installer
; Kompajlirati s NSIS 3.x: makensis efs_installer.nsi
; Ocekuje build u %USERPROFILE%\build_windows\bin\Release (promijeni SRC_DIR).

!define PRODUCT "EasyFormStudio"
!define VERSION "2026"
; Moze se pregaziti s komandne linije: makensis /DSRC_DIR=C:\...\bin\Release efs_installer.nsi
!ifndef SRC_DIR
  !define SRC_DIR "$%USERPROFILE%\build_windows\bin\Release"
!endif

Unicode true
Name "${PRODUCT} ${VERSION}"
OutFile "${PRODUCT}-${VERSION}-setup.exe"
InstallDir "$PROGRAMFILES64\${PRODUCT}"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

; Ekstenzije moraju biti bundlane prije kompajliranja installera
; (python build_files\utils\make_bundle_extensions.py).
!if ! /FileExists "${SRC_DIR}\5.2\extensions\system\efs\blender_manifest.toml"
  !error "EFS ekstenzija nije bundlana u ${SRC_DIR} - pokreni make_bundle_extensions.py prije makensis"
!endif
!if ! /FileExists "${SRC_DIR}\5.2\extensions\system\bool_tool\blender_manifest.toml"
  !error "Bool Tool ekstenzija nije bundlana u ${SRC_DIR} - pokreni make_bundle_extensions.py prije makensis"
!endif

!include "MUI2.nsh"
!define MUI_ICON "..\..\release\windows\icons\winblender.ico"
!define MUI_UNICON "..\..\release\windows\icons\winblender.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\EasyFormStudio.exe"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Croatian"
!insertmacro MUI_LANGUAGE "English"

Section "EasyFormStudio"
  SetOutPath "$INSTDIR"
  File /r "${SRC_DIR}\*.*"

  ; Precaci ciljaju GUI launcher (bez konzolnog prozora). blender.exe MORA
  ; ostati pod tim imenom - launcher ga pokrece hardkodirano.
  IfFileExists "$INSTDIR\EasyFormStudio.exe" +2 0
    Rename "$INSTDIR\blender-launcher.exe" "$INSTDIR\EasyFormStudio.exe"

  CreateDirectory "$SMPROGRAMS\${PRODUCT}"
  CreateShortcut "$SMPROGRAMS\${PRODUCT}\${PRODUCT}.lnk" "$INSTDIR\EasyFormStudio.exe"
  CreateShortcut "$DESKTOP\${PRODUCT}.lnk" "$INSTDIR\EasyFormStudio.exe"

  ; .blend asocijacija
  WriteRegStr HKCR ".blend" "" "EasyFormStudio.File"
  WriteRegStr HKCR "EasyFormStudio.File" "" "EasyFormStudio File"
  WriteRegStr HKCR "EasyFormStudio.File\DefaultIcon" "" "$INSTDIR\EasyFormStudio.exe,1"
  WriteRegStr HKCR "EasyFormStudio.File\shell\open\command" "" '"$INSTDIR\EasyFormStudio.exe" "%1"'

  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT}" \
      "DisplayName" "${PRODUCT} ${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT}" \
      "DisplayIcon" "$INSTDIR\EasyFormStudio.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT}" \
      "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT}" \
      "Publisher" "EasyFormStudio"
SectionEnd

Section "Uninstall"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\${PRODUCT}\${PRODUCT}.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT}"
  Delete "$DESKTOP\${PRODUCT}.lnk"
  DeleteRegKey HKCR "EasyFormStudio.File"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT}"
SectionEnd
