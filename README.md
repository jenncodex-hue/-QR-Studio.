# QR Studio Android project

This project packages the supplied QR Studio 3.0 Kivy app for Android.

## Storage behavior
Generated QR images and the JSON history file are stored in Kivy's private
application data directory under `QR_Codes`. This avoids broad shared-storage
permissions. These files are private to the installed app and are removed if
the app is uninstalled unless separately exported.

The header logo is bundled as `qr_studio_logo.jpg`.

## Build
The included GitHub Actions workflow is manually triggered from the repository's
Actions tab. It builds a **debug APK** and uploads it as a workflow artifact.
A debug APK is suitable for installation/testing, not a final signed release.

## Important testing note
The in-app file chooser initially opens the app-private QR_Codes directory.
The optional logo overlay chooser therefore only browses files visible to the
app. A system photo-picker integration can be added separately if selecting
arbitrary images from shared phone storage is required.
