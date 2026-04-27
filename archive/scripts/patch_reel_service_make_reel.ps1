$ErrorActionPreference = 'Stop'

$sshTarget = 'ubuntu@43.201.227.194'
$keyPath = 'C:\Users\minho\Downloads\n8n-key.pem'

$py = @'
from pathlib import Path
import re

p = Path('/app/main.py')
s = p.read_text()

s = re.sub(
    r'class ReelResponse\(BaseModel\):\n\s*ok: bool\n\s*video_base64: str\n',
    'class ReelResponse(BaseModel):\n    ok: bool\n    video_url: str\n    video_base64: Optional[str] = None\n\n',
    s,
    count=1,
)

s = re.sub(
    r'\n\s*with open\(output_path, "rb"\) as f:\n\s*video_bytes = f\.read\(\)\n\n\s*video_base64 = base64\.b64encode\(video_bytes\)\.decode\(\)\n\s*return ReelResponse\(ok=True, video_base64=video_base64\)',
    '\n        with open(output_path, "rb") as f:\n            video_bytes = f.read()\n\n        save_dir = "/var/www/images"\n        os.makedirs(save_dir, exist_ok=True)\n        filename = f"reel_{uuid.uuid4().hex}.mp4"\n        save_path = os.path.join(save_dir, filename)\n        with open(save_path, "wb") as out_f:\n            out_f.write(video_bytes)\n        video_url = f"https://n8n.mykindredai.com/images/{filename}"\n\n    return ReelResponse(ok=True, video_url=video_url)',
    s,
    count=1,
    flags=re.S,
)

p.write_text(s)
print('PATCHED')
'@

$remoteCmd = @"
python - <<'PY'
$py
PY
"@

ssh -i $keyPath $sshTarget "docker exec reel-service sh -lc $([char]34)$remoteCmd$([char]34)"
ssh -i $keyPath $sshTarget "docker restart reel-service"
ssh -i $keyPath $sshTarget "docker exec reel-service sh -lc 'sed -n \"1,220p\" /app/main.py'"
