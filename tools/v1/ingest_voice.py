#!/usr/bin/env python3
"""Ingest Faraz's own narration recordings for the Ayah Lens demo v1.0.

Finds s1..s7 (and the s1-fallback and s4-fallback takes) in a folder (default ~/Downloads), in any common audio
format, and for each file:
  decode to 48 kHz mono, remove DC offset, trim leading and trailing silence to 0.3 s (silence = 10 ms frames more
  than 40 dB below the file's peak), two-pass loudnorm to -20 LUFS with peak -3 dBFS (linear when possible),
  write build/video-v1.0/narration/own/<id>.wav (48 kHz mono, 24 bit).
It writes own/manifest.json with duration, integrated loudness and peak per file.

Which ids are required follows edit.json: without a toggle clip s5 is not needed and s4 means s4-fallback.
A file whose trimmed duration is more than 40 percent off the Callum paragraph with the same id is REFUSED by name
and nothing is written for it. The Callum files are never written to.

Run with the venv that has numpy and Pillow:
  /Users/farazsyed/data/khirad/apps/ayah-lens-prep/venv-data/bin/python tools/v1/ingest_voice.py [--src DIR]
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_v1 as R  # noqa: E402

SR = R.SR
PAD_S = 0.3
SILENCE_DB = -40.0
TARGET_LUFS = -20.0
TARGET_TP = -3.0
EXTS = {'.m4a', '.mp3', '.wav', '.aif', '.aiff', '.aifc', '.caf', '.flac', '.ogg', '.opus', '.aac', '.wma', '.mp4', '.mov', '.webm'}
ALL_IDS = [f's{i}' for i in range(1, 8)] + ['s1-fallback', 's4-fallback']
NAME_RE = re.compile(r'^(s[1-7])(-fallback)?(?:-\(?\d+\)?)?$')


class Refused(Exception):
    """A file that must not be ingested; the message names the file and the reason."""


# ----------------------------------------------------------------------------------------------
# finding files
# ----------------------------------------------------------------------------------------------
def normalise_stem(stem):
    return re.sub(r'[\s_]+', '-', stem.strip().lower())


def required_ids(edit=None):
    """Narration ids the current edit.json actually uses: with no toggle clip that is s2, s3, s4-fallback, s6, s7
    (s1 plays Faraz's on-camera audio and has no narration; s5 and the bridged s4 are only needed once toggle.file is set)."""
    edit = edit or R.load_edit(voice='callum')
    return [Path(sec['narration']['file']).stem for sec in edit['sections'] if sec['narration'].get('file')]


def find_sources(folder):
    """Return ({id: Path}, [warnings]). Newest file wins when several match the same id."""
    found, warnings, ignored = {}, [], []
    for p in sorted(Path(folder).expanduser().iterdir()):
        if not p.is_file() or p.suffix.lower() not in EXTS:
            continue
        m = NAME_RE.match(normalise_stem(p.stem))
        if not m:
            continue
        ident = m.group(1) + (m.group(2) or '')
        if ident not in ALL_IDS:
            ignored.append(p.name)
            continue
        found.setdefault(ident, []).append(p)
    chosen = {}
    for ident, files in found.items():
        files.sort(key=lambda f: f.stat().st_mtime)
        chosen[ident] = files[-1]
        for f in files[:-1]:
            warnings.append(f'{ident}: several files match; using the newest ({files[-1].name}), ignoring {f.name}')
    for name in ignored:
        warnings.append(f'ignored {name}: only s1 and s4 have a fallback take')
    return chosen, warnings


# ----------------------------------------------------------------------------------------------
# audio steps
# ----------------------------------------------------------------------------------------------
def decode_mono(path):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path), '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'])
    x = np.frombuffer(raw, dtype='<f4').astype(np.float64)
    if len(x) == 0:
        raise Refused(f'{Path(path).name}: decoded to zero samples')
    return x


def remove_dc(x):
    return x - x.mean()


def detect_speech(x, thr_db=SILENCE_DB, frame_ms=10, min_frames=5):
    """(onset_sample, end_sample) of the speech: the first and last run of min_frames frames whose RMS is within
    thr_db of the file's peak. A single click or lip smack is shorter than min_frames and does not count."""
    peak = float(np.abs(x).max())
    if peak < 1e-4:
        raise Refused('no speech found (file is silent)')
    fr = int(SR * frame_ms / 1000)
    n = len(x) // fr
    rms = np.sqrt(np.mean(x[:n * fr].reshape(n, fr) ** 2, axis=1))
    loud = 20 * np.log10(rms / peak + 1e-12) > thr_db
    runs = np.convolve(loud.astype(int), np.ones(min_frames, dtype=int), 'valid') == min_frames
    idx = np.where(runs)[0]
    if len(idx) == 0:
        raise Refused('no speech found (nothing stays within 40 dB of the peak for 50 ms)')
    return int(idx[0] * fr), int((idx[-1] + min_frames) * fr)


def trim_to_pads(x, onset, end, pad_s=PAD_S):
    """Keep exactly pad_s before the onset and after the end, zero-filling when the recording has less."""
    pad = round(pad_s * SR)
    lo, hi = onset - pad, end + pad
    out = np.zeros(hi - lo, dtype=np.float64)
    a, b = max(lo, 0), min(hi, len(x))
    out[a - lo:b - lo] = x[a:b]
    f = round(0.01 * SR)
    out[:f] *= np.linspace(0, 1, f)
    out[-f:] *= np.linspace(1, 0, f)
    return out


def write_f32_wav(path, x):
    raw = Path(str(path) + '.f32')
    raw.write_bytes(x.astype('<f4').tobytes())
    R.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', raw, '-c:a', 'pcm_f32le', path])
    raw.unlink()


def parse_loudnorm_json(log):
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', log)
    if m is None:
        raise ValueError('No loudnorm measurement block')
    d = json.loads(m.group(0))
    need = ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')
    out = {}
    for k in need:
        v = d.get(k)
        if v is None:
            raise ValueError(f'loudnorm report lacks {k}')
        out[k] = float(v)
        if out[k] in (float('inf'), float('-inf')) or out[k] != out[k]:
            raise Refused('loudness could not be measured (file is silent or too short)')
    return out


def loudnorm_two_pass(src_wav, dst_wav, n_samples):
    """Pass 1 measures, pass 2 applies linear gain; the result is forced to exactly n_samples (CLAUDE.md: loudnorm
    timestamps can change lengths, so reset them and pad or trim)."""
    base = f'loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA=11'
    p1 = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(src_wav), '-af', base + ':print_format=json', '-f', 'null', '-'],
                        capture_output=True, text=True, check=True).stderr
    m = parse_loudnorm_json(p1)
    af = (f"{base}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,"
          f'aresample={SR},asetpts=N/SR/TB,apad=whole_len={n_samples},atrim=end_sample={n_samples}')
    R.run(['ffmpeg', '-v', 'error', '-y', '-i', src_wav, '-af', af, '-ar', str(SR), '-ac', '1', '-c:a', 'pcm_s24le', dst_wav])
    return m


def wav_samples(path):
    return int(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=duration_ts', '-of', 'csv=p=0', str(path)]).decode().strip())


# ----------------------------------------------------------------------------------------------
# duration guard
# ----------------------------------------------------------------------------------------------
def check_duration(ident, src_name, own_s, callum_s, tol=0.40):
    ratio = own_s / callum_s
    if abs(ratio - 1.0) > tol:
        raise Refused(f'REFUSED {ident}: {src_name} is {own_s:.1f} s after trimming, the Callum {ident} paragraph is {callum_s:.1f} s '
                      f'({(ratio - 1) * 100:+.0f}%, limit +/-{tol * 100:.0f}%). Nothing was written for {ident}. '
                      f'Re-record it, or check that the file really is {ident}.')
    return ratio


def callum_file(callum_dir, ident):
    for ext in ('.mp3', '.wav', '.m4a'):
        p = Path(callum_dir) / f'{ident}{ext}'
        if p.exists():
            return p
    raise FileNotFoundError(f'No Callum paragraph {ident} in {callum_dir}')


# ----------------------------------------------------------------------------------------------
# one file
# ----------------------------------------------------------------------------------------------
def ingest_file(ident, src, out_dir, callum_dir, tol=0.40, tmp=None):
    """Process one recording; return its manifest record. Raises Refused before writing anything."""
    src, out_dir = Path(src), Path(out_dir)
    x = decode_mono(src)
    dc = float(x.mean())
    raw_peak = float(np.abs(x).max())
    x = remove_dc(x)
    onset, end = detect_speech(x)
    y = trim_to_pads(x, onset, end)
    own_s = len(y) / SR
    cal = callum_file(callum_dir, ident)
    cal_s = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(cal)]).decode().strip())
    ratio = check_duration(ident, src.name, own_s, cal_s, tol)
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / f'{ident}.wav'
    if dst.resolve() == cal.resolve() or Path(callum_dir).resolve() == out_dir.resolve():
        raise RuntimeError('refusing to write into the Callum folder')
    with tempfile.TemporaryDirectory(dir=tmp) as d:
        pre = Path(d) / 'pre.wav'
        write_f32_wav(pre, y)
        ln = loudnorm_two_pass(pre, dst, len(y))
    n = wav_samples(dst)
    if n != len(y):
        raise RuntimeError(f'{ident}: wrote {n} samples, expected {len(y)}')
    lufs, peak = R.measure_wav(dst)
    warns = []
    if abs(lufs - TARGET_LUFS) > 1.0:
        warns.append(f'loudness {lufs:.1f} LUFS is more than 1 LU from {TARGET_LUFS:.0f}')
    if peak > TARGET_TP + 0.1:
        warns.append(f'peak {peak:.1f} dBFS is above {TARGET_TP:.0f}')
    if raw_peak >= 0.999:
        warns.append('source reaches full scale (clipped); re-record quieter')
    return {
        'id': ident, 'status': 'warn' if warns else 'ok', 'warnings': warns,
        'source_file': str(src), 'source_sha256': R.sha256(src), 'output': str(dst),
        'duration_s': round(own_s, 3), 'samples': len(y), 'speech_s': round((end - onset) / SR, 3),
        'lead_s': PAD_S, 'trail_s': PAD_S, 'dc_offset_removed': round(dc, 6),
        'integrated_lufs': round(lufs, 2), 'peak_dbfs': round(peak, 2),
        'callum_file': str(cal), 'callum_duration_s': round(cal_s, 3), 'ratio_to_callum': round(ratio, 3),
        'loudnorm_pass1': ln,
    }


# ----------------------------------------------------------------------------------------------
# folder
# ----------------------------------------------------------------------------------------------
def ingest_folder(src_dir, out_dir, callum_dir, tol=0.40, log=print, required=None):
    out_dir, callum_dir = Path(out_dir), Path(callum_dir)
    if out_dir.resolve() == callum_dir.resolve():
        raise RuntimeError('The output folder must not be the Callum folder')
    chosen, warnings = find_sources(src_dir)
    for w in warnings:
        log('note: ' + w)
    records, refused = [], []
    req = required if required is not None else required_ids()
    for ident in ALL_IDS:
        if ident not in chosen:
            continue
        try:
            rec = ingest_file(ident, chosen[ident], out_dir, callum_dir, tol)
            records.append(rec)
            log(f"{ident}: {rec['duration_s']:.2f} s (Callum {rec['callum_duration_s']:.2f} s, {rec['ratio_to_callum']:.2f}x), "
                f"{rec['integrated_lufs']:.1f} LUFS, peak {rec['peak_dbfs']:.1f} dBFS" + (f"  WARN: {'; '.join(rec['warnings'])}" if rec['warnings'] else ''))
        except Refused as e:
            msg = str(e) if str(e).startswith('REFUSED') else f'REFUSED {ident}: {chosen[ident].name}: {e}'
            refused.append({'id': ident, 'source_file': str(chosen[ident]), 'reason': msg})
            log(msg)
    missing = [i for i in req if i not in chosen]
    for i in missing:
        log(f'MISSING {i}: no file named {i}.* in {src_dir}')
    manifest = {
        'generated': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'source_folder': str(Path(src_dir).expanduser()),
        'targets': {'lufs': TARGET_LUFS, 'peak_dbfs': TARGET_TP, 'pad_s': PAD_S, 'silence_db_below_peak': SILENCE_DB, 'duration_tolerance': tol},
        'files': records, 'refused': refused, 'missing_required': missing,
        'required_ids': req, 'extra_ingested': [r['id'] for r in records if r['id'] not in req],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', default=str(Path.home() / 'Downloads'), help='folder with s1..s7 recordings (default ~/Downloads)')
    ap.add_argument('--out', default=str(R.ROOT / 'build/video-v1.0/narration/own'))
    ap.add_argument('--callum-dir', default=str(R.ROOT / 'build/video-v1.0/narration'))
    ap.add_argument('--tolerance', type=float, default=0.40)
    args = ap.parse_args(argv)
    m = ingest_folder(args.src, args.out, args.callum_dir, args.tolerance)
    ok = len(m['files']) - sum(1 for f in m['files'] if f['status'] == 'warn')
    print(f"ingested {len(m['files'])} file(s) ({ok} clean), refused {len(m['refused'])}, missing {len(m['missing_required'])}; manifest {Path(args.out) / 'manifest.json'}")
    return 0 if (not m['refused'] and not m['missing_required']) else 1


if __name__ == '__main__':
    sys.exit(main())
