"""Download the public data used by the four notebooks (about 26 GB in total).

    python download_cycle_data.py                  # everything, into data/
    python download_cycle_data.py eeg nhanes       # only some parts
    CYCLE_DATA=/path/to/folder python download_cycle_data.py

Parts:
    marquette  Marquette menstrual cycle data (Fehring 2012), 0.3 MB. The host refuses scripted downloads,
               so this part prints where to save the file by hand.
    nhanes     NHANES 2013-2014 (CDC, public domain): 6 files, about 30 MB.
    eeg        OpenNeuro ds007615 v1.0.0 (CC0): questionnaires and resting EEG of 69 women, about 19 GB.
    capture24  CAPTURE-24 (University of Oxford, CC BY 4.0): one zip file, about 6.9 GB.

Safe to re-run: complete files are skipped and interrupted downloads resume. EEG recordings are checked
against their published sizes, and every file is checked so that an error page is never saved as data.
"""
import os
import sys
import urllib.error
import urllib.request

OUT = os.environ.get("CYCLE_DATA", "data")
MARQUETTE_PAGE = "https://epublications.marquette.edu/data_nfp/7"
NHANES_BASE = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2013/DataFiles/"
NHANES_FILES = ["DEMO_H", "BMX_H", "TST_H", "RHQ_H", "RXQ_RX_H", "PAXDAY_H"]
OPENNEURO = "https://s3.amazonaws.com/openneuro.org/ds007615/"
CAPTURE24 = ("https://ora.ox.ac.uk/objects/uuid:99d7c092-d865-4a19-b096-cc16440cd001/download_file"
             "?file_format=&safe_filename=capture24.zip&type_of_work=Dataset")
CAPTURE24_SIZE = 6902652480
# ds007615: size in bytes of the eyes-closed and eyes-open recording of each participant
EEG_SIZES = (
    "01,136761600,136755072;02,136764048,136755344;03,136765952,136755888;04,136764048,136756704;05,136762144,136756704;"
    "06,136761872,136755616;07,136761600,136756160;08,136760240,136755072;09,136765680,136755888;10,136765408,136755344;"
    "11,136760784,136755888;12,136760240,136756704;13,136764048,136755888;14,136760784,136755888;15,136763776,136755072;"
    "16,136763504,136755072;17,136765136,136754528;18,136762960,136756704;19,136767040,136756432;20,136757248,136754800;"
    "21,136764864,136756704;22,136766496,136756160;23,136762144,136756704;24,136764592,136755888;25,136761600,136756976;"
    "26,136770032,136756432;27,136758064,136754800;28,136767312,136756704;29,136759424,136756704;30,136759696,136755344;"
    "31,136766224,136755888;32,136759424,136755344;33,136762144,136756976;34,136759696,136755888;35,136758880,136755616;"
    "36,136766224,136756976;37,136764048,136757248;38,136765952,136755616;39,136762688,136755888;40,136764048,136756432;"
    "41,136764864,136755072;42,136765408,136757248;43,136764320,136756432;44,136763776,136755072;45,136761056,136756976;"
    "46,136767584,136756976;47,136762144,136755888;48,136765136,136755616;49,136763232,136756976;50,136764592,136756976;"
    "51,136763776,136756704;52,136771120,136757248;53,136766496,136756976;54,136761600,136755344;55,136764864,136755344;"
    "56,136757792,136755072;57,136758880,136755344;58,136761328,136755344;59,136760512,136756704;60,136763776,136756704;"
    "61,136761328,136754800;62,136767312,136756160;63,136763504,136755072;64,136765952,136756704;65,136764864,136755344;"
    "66,136767312,136755072;67,136760240,136756976;68,136766224,136756432;69,136762144,136756976")


def looks_valid(path, magic=b""):
    with open(path, "rb") as f:
        head = f.read(512)
    if b"<!doctype html" in head.lower() or b"<html" in head.lower():
        return False
    return not magic or magic in head


def fetch(url, dest, size=0, magic=b"", quiet=True):
    """Download url to dest, resuming a partial file. Returns True when dest is complete."""
    if os.path.exists(dest) and (os.path.getsize(dest) == size if size else os.path.getsize(dest) > 0):
        return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    for attempt in range(4):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        if size and have > size:
            os.remove(part)
            have = 0
        if not (size and have == size):
            headers = {"User-Agent": "download_cycle_data.py"}
            if have:
                headers["Range"] = f"bytes={have}-"
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=60) as r, open(part, "ab" if r.status == 206 else "wb") as f:
                    got, step = 0, 1 << 20
                    while True:
                        b = r.read(step)
                        if not b:
                            break
                        f.write(b)
                        got += len(b)
                        if not quiet and (have + got) // (1 << 30) > (have + got - len(b)) // (1 << 30):
                            print(f"    {(have + got) / 1e9:.1f} GB", flush=True)
            except urllib.error.HTTPError as e:
                if e.code in (403, 404):
                    return False
                if e.code != 416:                    # 416: the partial file is already complete
                    continue
            except Exception as e:
                print(f"    interrupted ({e}), resuming", flush=True)
                continue
        n = os.path.getsize(part) if os.path.exists(part) else 0
        if size and n < size:
            continue
        if (not size or n == size) and n > 0 and looks_valid(part, magic):
            os.replace(part, dest)
            return True
        os.remove(part)
    return False


def marquette():
    dest = os.path.join(OUT, "marquette", "FedCycleData071012.csv")
    print("[marquette] Marquette menstrual cycle data")
    if os.path.exists(dest):
        print("  already there")
        return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"  Download 'FedCycleData071012 (2).csv' by hand from {MARQUETTE_PAGE}\n  and save it as {dest}")
    return False


def nhanes():
    print(f"[nhanes] NHANES 2013-2014 ({len(NHANES_FILES)} files)")
    bad = [n for n in NHANES_FILES
           if not fetch(NHANES_BASE + n + ".xpt", os.path.join(OUT, "nhanes_2013_2014", n + ".xpt"), magic=b"HEADER RECORD")]
    print("  done" if not bad else f"  failed: {', '.join(bad)}")
    return not bad


def eeg():
    subjects = [s.split(",") for s in EEG_SIZES.split(";")]
    root = os.path.join(OUT, "ds007615")
    small = ["dataset_description.json", "README", "participants.tsv", "participants.json",
             "phenotype/hc_usage.tsv", "phenotype/hc_usage.json"]
    for sid, _, _ in subjects:
        for acq in ("ec", "eo"):
            small += [f"sub-{sid}/eeg/sub-{sid}_task-rest_acq-{acq}_{s}" for s in ("eeg.vhdr", "eeg.vmrk", "events.tsv")]
    print(f"[eeg] OpenNeuro ds007615: {len(small)} small files, then {2 * len(subjects)} recordings (about 19 GB)")
    bad = [rel for rel in small if not fetch(OPENNEURO + rel, os.path.join(root, rel))]
    for i, (sid, ec, eo) in enumerate(subjects, 1):
        for acq, size in (("ec", int(ec)), ("eo", int(eo))):
            rel = f"sub-{sid}/eeg/sub-{sid}_task-rest_acq-{acq}_eeg.eeg"
            if not fetch(OPENNEURO + rel, os.path.join(root, rel), size=size):
                bad.append(rel)
        print(f"  sub-{sid} ({i} of {len(subjects)})", flush=True)
    print("  done" if not bad else f"  {len(bad)} files failed, run again: {', '.join(bad[:5])}")
    return not bad


def capture24():
    print("[capture24] CAPTURE-24 (one zip file, about 6.9 GB)")
    ok = fetch(CAPTURE24, os.path.join(OUT, "capture24", "capture24.zip"), size=CAPTURE24_SIZE, magic=b"PK", quiet=False)
    print("  done" if ok else "  failed, run again to resume")
    return ok


PARTS = {"marquette": marquette, "nhanes": nhanes, "eeg": eeg, "capture24": capture24}


def main():
    want = sys.argv[1:] or list(PARTS)
    unknown = [w for w in want if w not in PARTS]
    if unknown:
        sys.exit(f"unknown part(s): {', '.join(unknown)}; choose from {', '.join(PARTS)}")
    results = {w: PARTS[w]() for w in want}
    missing = [w for w, ok in results.items() if not ok]
    if missing:
        print(f"Not complete: {', '.join(missing)}")
        sys.exit(1)
    print(f"All parts complete in {OUT}")


if __name__ == "__main__":
    main()
