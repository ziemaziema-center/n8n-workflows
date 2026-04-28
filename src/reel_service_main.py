import base64
import os
import subprocess
import tempfile
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, model_validator

DEFAULT_DURATION = 1.5

app = FastAPI(title="FFmpeg Reel Service")


class ReelRequest(BaseModel):
    images_base64: List[str]
    durations: Optional[List[float]] = None

    @field_validator("images_base64")
    @classmethod
    def images_not_empty(cls, v):
        if not v:
            raise ValueError("images_base64 must not be empty")
        return v

    @model_validator(mode="after")
    def fill_and_validate_durations(self):
        if self.durations is None:
            self.durations = [DEFAULT_DURATION] * len(self.images_base64)
        elif len(self.durations) != len(self.images_base64):
            raise ValueError("durations must have the same length as images_base64")
        return self


class ReelResponse(BaseModel):
    ok: bool
    video_url: str
    video_base64: Optional[str] = None


@app.get("/")
def health():
    return {"ok": True, "message": "FFmpeg Reel Service is running"}


@app.post("/make-reel", response_model=ReelResponse)
def make_reel(req: ReelRequest):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Decode and save each image
        image_paths = []
        for i, b64 in enumerate(req.images_base64):
            try:
                img_data = base64.b64decode(b64)
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail=f"images_base64[{i}] is not valid base64",
                )
            img_path = os.path.join(tmpdir, f"img_{i:04d}.jpg")
            with open(img_path, "wb") as f:
                f.write(img_data)
            image_paths.append(img_path)

        # Build FFmpeg concat file
        concat_path = os.path.join(tmpdir, "input.txt")
        with open(concat_path, "w") as f:
            for img_path, duration in zip(image_paths, req.durations):
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration}\n")
            # FFmpeg concat demuxer needs the last file repeated without duration
            f.write(f"file '{image_paths[-1]}'\n")

        output_path = os.path.join(tmpdir, f"{uuid.uuid4()}.mp4")

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_path,
            "-vf", (
                "scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,"
                "format=yuv420p"
            ),
            "-r", "30",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output_path,
        ]

        try:
            result = subprocess.run(
                ffmpeg_cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="FFmpeg timed out")
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"FFmpeg failed: {e.stderr.decode(errors='replace')[-2000:]}",
            )

        with open(output_path, "rb") as f:
            video_bytes = f.read()

        save_dir = "/var/www/images"
        os.makedirs(save_dir, exist_ok=True)
        filename = f"reel_{uuid.uuid4().hex}.mp4"
        save_path = os.path.join(save_dir, filename)
        with open(save_path, "wb") as out_f:
            out_f.write(video_bytes)
        video_url = f"https://n8n.mykindredai.com/images/{filename}"

    video_b64 = base64.b64encode(video_bytes).decode("ascii")
    return ReelResponse(ok=True, video_url=video_url, video_base64=video_b64)

class SaveImageRequest(BaseModel):
    image_url: str
    filename: str

class SaveImageResponse(BaseModel):
    ok: bool
    permanent_url: str

@app.post('/save-image', response_model=SaveImageResponse)
def save_image(req: SaveImageRequest):
    import urllib.request
    save_dir = '/var/www/images'
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, req.filename)
    urllib.request.urlretrieve(req.image_url, save_path)
    permanent_url = f'https://n8n.mykindredai.com/images/{req.filename}'
    return SaveImageResponse(ok=True, permanent_url=permanent_url)
