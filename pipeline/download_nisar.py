#!/usr/bin/env python3
"""
NISAR L2 GCOV Data Downloader
Downloads 3 NISAR provisional L2 GCOV products from Alaska Satellite Facility (ASF).
Saves them into data/raw/.
"""

import os
import sys
import time
import base64
import getpass
import netrc
import argparse
from pathlib import Path
import requests
from tqdm import tqdm

FILES = [
    "https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_PROVISIONAL_V1/NISAR_L2_PR_GCOV_026_091_D_076_4005_DHDH_A_20260726T123422_20260726T123457_P05023_N_F_J_001/NISAR_L2_PR_GCOV_026_091_D_076_4005_DHDH_A_20260726T123422_20260726T123457_P05023_N_F_J_001.h5",
    "https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_PROVISIONAL_V1/NISAR_L2_PR_GCOV_025_091_D_076_2005_QPDH_A_20260714T123423_20260714T123457_P05023_F_F_J_001/NISAR_L2_PR_GCOV_025_091_D_076_2005_QPDH_A_20260714T123423_20260714T123457_P05023_F_F_J_001.h5",
    "https://nisar.asf.earthdatacloud.nasa.gov/NISAR/NISAR_L2_GCOV_PROVISIONAL_V1/NISAR_L2_PR_GCOV_024_091_D_076_4005_DHDH_A_20260702T123423_20260702T123458_P05023_N_F_J_001/NISAR_L2_PR_GCOV_024_091_D_076_4005_DHDH_A_20260702T123423_20260702T123458_P05023_N_F_J_001.h5"
]

ASF_AUTH_URL = "https://urs.earthdata.nasa.gov/oauth/authorize?client_id=BO_n7nTIlMljdvU6kRRB3g&redirect_uri=https://auth.asf.alaska.edu/login&response_type=code&state="


def get_credentials():
    """Retrieve username and password from .netrc or prompt user."""
    # 1. Try netrc
    try:
        n = netrc.netrc()
        auth = n.authenticators("urs.earthdata.nasa.gov")
        if auth:
            return auth[0], auth[2]
    except Exception:
        pass

    # Also check ~/.netrc explicitly if default search missed it
    home = Path.home()
    for netrc_name in [".netrc", "_netrc"]:
        netrc_file = home / netrc_name
        if netrc_file.is_file():
            try:
                n = netrc.netrc(str(netrc_file))
                auth = n.authenticators("urs.earthdata.nasa.gov")
                if auth:
                    return auth[0], auth[2]
            except Exception:
                pass

    # 2. Prompt user
    print("Enter your Earthdata Login credentials:")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()
    return username, password


def authenticate(session: requests.Session, username: str, password: str):
    """Authenticate with Earthdata Login and acquire ASF session cookie / bearer token."""
    print(f"Authenticating as {username} with NASA Earthdata Login...")
    user_pass = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {user_pass}"}

    resp = session.get(ASF_AUTH_URL, headers=headers, allow_redirects=True, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Authentication failed with status {resp.status_code}. "
            "Please verify your Earthdata credentials and ensure ASF EULA agreement is accepted at https://urs.earthdata.nasa.gov."
        )

    token = session.cookies.get("urs-access-token")
    if not token and "asf-urs" not in session.cookies:
        raise RuntimeError("Failed to obtain ASF authentication token. Check credentials.")

    print("Authentication successful!")
    return token


def determine_output_dir(custom_dir=None):
    """Determine the target directory for storing files (default data/raw)."""
    if custom_dir:
        target = Path(custom_dir).resolve()
    else:
        # Check relative to script location: ../data/raw or ./data/raw
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent
        target = project_root / "data" / "raw"
        if not target.parent.exists() and Path("data/raw").parent.exists():
            target = Path("data/raw").resolve()

    target.mkdir(parents=True, exist_ok=True)
    return target


def download_file(session: requests.Session, token: str, url: str, output_dir: Path, max_retries: int = 5):
    filename = url.split("?")[0].split("/")[-1]
    dest_path = output_dir / filename
    temp_path = output_dir / f"{filename}.part"

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Get total remote size
    head_resp = session.get(url, headers=headers, stream=True, timeout=30)
    if head_resp.status_code != 200:
        raise RuntimeError(f"Failed to access {url}: status {head_resp.status_code}")

    remote_size = int(head_resp.headers.get("Content-Length", 0))

    # Check if already fully downloaded
    if dest_path.exists():
        local_size = dest_path.stat().st_size
        if remote_size > 0 and local_size == remote_size:
            print(f"File {filename} is already fully downloaded ({local_size:,} bytes). Skipping.")
            return dest_path, local_size

    # Check existing partial download
    start_byte = 0
    if temp_path.exists():
        start_byte = temp_path.stat().st_size
        if remote_size > 0 and start_byte >= remote_size:
            temp_path.replace(dest_path)
            print(f"File {filename} is already complete. Renamed to {filename}.")
            return dest_path, remote_size
        print(f"Resuming {filename} from byte {start_byte:,} ({start_byte / (1024**3):.2f} GB)...")

    for attempt in range(1, max_retries + 1):
        try:
            req_headers = dict(headers)
            if start_byte > 0:
                req_headers["Range"] = f"bytes={start_byte}-"

            with session.get(url, headers=req_headers, stream=True, timeout=60) as r:
                if r.status_code not in (200, 206):
                    raise RuntimeError(f"HTTP status {r.status_code} received when downloading {filename}")

                mode = "ab" if start_byte > 0 else "wb"
                chunk_size = 2 * 1024 * 1024  # 2 MB chunks

                with open(temp_path, mode) as f, tqdm(
                    total=remote_size,
                    initial=start_byte,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=filename[:32] + "...",
                    ncols=100
                ) as bar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))
                            start_byte += len(chunk)

            # Finished successfully
            temp_path.replace(dest_path)
            final_size = dest_path.stat().st_size
            print(f"Successfully downloaded {filename} ({final_size:,} bytes).")
            return dest_path, final_size

        except (requests.RequestException, RuntimeError, IOError) as e:
            print(f"\n[Attempt {attempt}/{max_retries}] Download interrupted: {e}")
            if attempt < max_retries:
                sleep_time = min(2 ** attempt, 30)
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
                # update start_byte for resumption
                if temp_path.exists():
                    start_byte = temp_path.stat().st_size
            else:
                raise RuntimeError(f"Download failed for {filename} after {max_retries} attempts.")


def main():
    parser = argparse.ArgumentParser(description="Download NISAR L2 GCOV products from ASF.")
    parser.add_argument("--output-dir", help="Directory to save files (defaults to data/raw)")
    args = parser.parse_args()

    output_dir = determine_output_dir(args.output_dir)
    print(f"Output directory: {output_dir}")

    username, password = get_credentials()
    if not username or not password:
        print("Error: Earthdata credentials are required.", file=sys.stderr)
        sys.exit(1)

    session = requests.Session()
    token = authenticate(session, username, password)

    results = []
    print(f"\nStarting download of {len(FILES)} NISAR files...")
    start_all = time.time()

    for idx, url in enumerate(FILES, 1):
        print(f"\n[{idx}/{len(FILES)}] Downloading {url.split('?')[0].split('/')[-1]}")
        dest_file, size = download_file(session, token, url, output_dir)
        results.append((dest_file.name, size))

    total_time = time.time() - start_all
    total_bytes = sum(s for _, s in results)

    print("\n" + "=" * 80)
    print("DOWNLOAD COMPLETE SUMMARY")
    print("=" * 80)
    for name, sz in results:
        sz_gb = sz / (1024 ** 3)
        print(f"File: {name}")
        print(f"  Size: {sz:,} bytes ({sz_gb:.2f} GB)")
    print("-" * 80)
    print(f"Total downloaded: {total_bytes / (1024 ** 3):.2f} GB across {len(results)} files in {total_time / 60:.1f} minutes.")
    print("=" * 80)


if __name__ == "__main__":
    main()

