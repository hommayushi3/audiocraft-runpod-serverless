import logging
import os
import torchaudio
from typing import Union, Generator
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from huggingface_hub import snapshot_download
import runpod
import base64
import json

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

def load_model():
    global model

    if not model:
        snapshot_download(repo_id=os.environ["MODEL_REPO"], revision=os.getenv("MODEL_REVISION", "main"))
        model = MusicGen.get_pretrained(os.environ["MODEL_REPO"])

    return model

model = None

def encode_file(file_name):
    with open(file_name, "rb") as f:
        encoded = base64.b64encode(f.read())
    return encoded.decode('utf-8')

def inference(event) -> Union[str, Generator[str, None, None]]:
    logging.info("Starting inference")
    job_input = event["input"]
    if not job_input:
        raise ValueError("No input provided")
    model = load_model()
    logging.info("Model loaded")

    generation_params = job_input.pop("generation_params", {"duration": 10})
    logging.info(generation_params)
    model.set_generation_params(**generation_params)
    descriptions = job_input.pop("descriptions", None)

    sample_file_name = job_input.pop("encoded_music_file_name", None)
    encoded_music_file = job_input.pop("encoded_music_file_content", None)
    music_bytes = base64.b64decode(encoded_music_file.encode('utf-8')) if encoded_music_file else None

    if isinstance(descriptions, str):
        descriptions = [descriptions]
    
    if descriptions is None:
        outputs = model.generate_unconditional(1)
    elif music_bytes:
        with open(sample_file_name, "wb+") as f:
            f.write(music_bytes)
        melody, sr = torchaudio.load(sample_file_name)
        outputs = model.generate_with_chroma(descriptions, melody[None].expand(3, -1, -1), sr)
    else:
        outputs = model.generate(descriptions)
    logging.info("Inference complete")

    output_files = {}
    for idx, one_wav in enumerate(outputs):
        # Will save under {idx}.wav, with loudness normalization at -14 db LUFS.
        audio_write(f'{idx}', one_wav.cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)
        output_files[idx] = encode_file(f'{idx}.wav')
    logging.info("Output files written")
    return json.dumps(output_files)

runpod.serverless.start({"handler": inference})
