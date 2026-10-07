"""Download the original UCI Online Retail workbook (not generated data)."""
import shutil
import ssl
from urllib.request import urlopen

import certifi

from src.config import RAW_FILE

UCI_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"


def main() -> None:
    if RAW_FILE.exists():
        print(f"Raw data already exists: {RAW_FILE}")
        return
    import zipfile
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(suffix=".zip") as temp:
        print("Downloading UCI Online Retail dataset…")
        # Explicit certifi bundle keeps the download reproducible on Python
        # installations without a system CA bundle (common on macOS).
        context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(UCI_URL, context=context) as response, open(temp.name, "wb") as target:
            shutil.copyfileobj(response, target)
        with zipfile.ZipFile(temp.name) as archive:
            candidates = [name for name in archive.namelist() if name.lower().endswith(".xlsx")]
            if not candidates:
                raise RuntimeError("UCI archive did not contain an Excel workbook.")
            with archive.open(candidates[0]) as source, RAW_FILE.open("wb") as destination:
                destination.write(source.read())
    print(f"Saved real source data to {RAW_FILE}")


if __name__ == "__main__":
    main()
