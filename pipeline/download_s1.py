"""pipeline/download_s1.py
Downloads the target Sentinel-1 GRD ZIP product to data/s1/ using asf_search and Earthdata credentials.
"""
from pathlib import Path
import netrc
import asf_search as asf

SCENE_NAME = "S1D_IW_GRDH_1SDV_20260725T120434_20260725T120459_003830_006E63_520C"
OUT_DIR = Path("data/s1")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def download_sentinel1():
    print(f"Searching for GRD_HD product {SCENE_NAME} via asf_search...")
    results = asf.search(
        platform=asf.PLATFORM.SENTINEL1,
        processingLevel=asf.PRODUCT_TYPE.GRD_HD,
        granule_list=[SCENE_NAME],
    )
    if not results:
        print(f"Error: Scene {SCENE_NAME} not found on ASF.")
        return False, "Scene not found on ASF", None

    granule = results[0]
    expected_bytes = granule.properties.get("bytes", 0)
    file_name = granule.properties.get("fileName", f"{SCENE_NAME}.zip")
    zip_path = OUT_DIR / file_name

    print(f"Found product: {file_name}")
    print(f"Expected size: {expected_bytes / 1e6:.1f} MB ({expected_bytes} bytes)")

    if zip_path.exists():
        actual_size = zip_path.stat().st_size
        print(f"File already exists: {zip_path} ({actual_size / 1e6:.1f} MB)")
        if actual_size >= 0.99 * expected_bytes:
            print("Download already complete and verified.")
            return True, str(zip_path), actual_size

    # Authenticate via netrc
    auth = None
    for p in [Path.home() / "_netrc", Path.home() / ".netrc"]:
        if p.exists():
            n = netrc.netrc(str(p))
            auth = n.authenticators("urs.earthdata.nasa.gov")
            if auth:
                break

    if not auth:
        return False, "No Earthdata credentials found in netrc", None

    session = asf.ASFSession()
    session.auth_with_creds(auth[0], auth[2])
    print(f"Authenticated as {auth[0]}. Starting download to {OUT_DIR}...")

    try:
        granule.download(path=str(OUT_DIR), session=session)
        if zip_path.exists():
            actual_size = zip_path.stat().st_size
            print(f"Downloaded: {zip_path} ({actual_size / 1e6:.1f} MB)")
            if actual_size >= 0.95 * expected_bytes:
                return True, str(zip_path), actual_size
            else:
                return False, f"File incomplete ({actual_size} of {expected_bytes} bytes)", actual_size
        else:
            return False, f"File missing after download: {zip_path}", None
    except Exception as e:
        print(f"Download failed: {e}")
        return False, str(e), None


if __name__ == "__main__":
    success, msg, sz = download_sentinel1()
    print("Outcome:", success, msg, sz)
