import h5py
from pathlib import Path

DATA_DIR = Path("data/raw")

for f in sorted(DATA_DIR.glob("NISAR_L2_PR_GCOV_*.h5")):
    print("=" * 80)
    print(f.name)
    with h5py.File(f, "r") as h5:
        def show(name, obj):
            if isinstance(obj, h5py.Dataset):
                print(f"  {name}  shape={obj.shape}  dtype={obj.dtype}")
        h5.visititems(show)

