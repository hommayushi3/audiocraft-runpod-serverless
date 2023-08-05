import gradio as gr
from predict import run, decode_b64_to_file

def generate(description, duration, melody):
    outputs = run(descriptions=[description], duration=duration, melody=melody)
    for k, v in outputs.items():
        decode_b64_to_file(v, f"{k}.wav")
    return "0.wav"

iface = gr.Interface(
    generate,
    [
        gr.inputs.Textbox(lines=3, label="Description of Music"),
        gr.inputs.Slider(minimum=1, maximum=60, step=1, label="Duration in seconds"),
        gr.inputs.File(label="Optional melody audio file upload (WAV)")
    ],
    gr.outputs.File(label="Generated music file"),
    live=False
)

# Replace these with your desired credentials
username = "musicgen"
password = "12345"

iface.launch(share=True, auth=(username, password))
