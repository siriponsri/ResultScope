"""Build a complete source ZIP, excluding private state and regenerable dependencies."""
from pathlib import Path
import argparse, hashlib, json, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','.venv','node_modules','__pycache__','.pytest_cache','.vercel','.hyperframes','.playwright-mcp','build'}

def included(path):
    parts=path.parts
    return not (any(p in EXCLUDED for p in parts) or parts[0]=='data' or path.name=='PROMPT.md'
        or (path.name.startswith('.env') and path.name!='.env.example')
        or path.suffix in {'.pyc','.pyo'} or path.name=='DELIVERY_MANIFEST.json')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if (ROOT/'.git').exists():
        candidates=[Path(name) for name in subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=ROOT).decode().split('\0') if name]
    else:
        candidates=[p.relative_to(ROOT) for p in ROOT.rglob('*') if p.is_file()]
    files=sorted(p for p in candidates if included(p) and (ROOT/p).is_file() and (ROOT/p).resolve()!=args.output.resolve())
    # Verify owner-supplied assets before packaging. Never alter gold labels or originals.
    demos=ROOT/'examples/thai_lab_reference_v3'
    for entry in json.loads((demos/'MANIFEST.json').read_text()):
        raw=(demos/entry['file']).read_bytes()
        assert len(raw)==entry['bytes'] and hashlib.sha256(raw).hexdigest()==entry['sha256'],entry['file']
    manifest={'version':'2.0.0','date':'2026-10-05','baseline':'4ac870a14bbd51dddaaeedc6b6c35498152d8654','private_state_included':False,'files':[{'path':p.as_posix(),'bytes':(ROOT/p).stat().st_size,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in files]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for p in files:archive.write(ROOT/p,'ResultScope/'+p.as_posix())
        archive.writestr('ResultScope/DELIVERY_MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(args.output) as archive:assert archive.testzip() is None
    print(json.dumps({'file':str(args.output.resolve()),'files':len(files)+1,'bytes':args.output.stat().st_size,'sha256':hashlib.sha256(args.output.read_bytes()).hexdigest()}))
if __name__=='__main__':main()
