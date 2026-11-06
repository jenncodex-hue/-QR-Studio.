[app]

title = QR Studio
package.name = qrstudio
package.domain = com.qrstudio
source.dir = .
source.include_exts = py,jpg,png,kv,atlas
version = 3.0.0
requirements = python3,kivy,qrcode,pillow
orientation = portrait
fullscreen = 0

# No shared-storage permission is needed: QR images and history are
# stored in the app's private data directory.
android.minapi = 23
android.api = 35
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
