from cx_Freeze import setup, Executable

build_spec_options = {
    "packages": ["customtkinter", "tkinter", "minify_html", "bs4", "requests", "re", "base64", "threading", "os"],
    "include_files": ["pico.min.css", "custom.css", "Wattpad2epub.py", "README.md"]
}

setup(
    name="BookNow",
    version="0.2.0",
    description="Wattpad Book Downloader",
    options={"build_exe": build_spec_options},
    executables=[Executable("gui.py")],
)
