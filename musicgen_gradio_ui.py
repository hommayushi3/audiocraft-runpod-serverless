import gradio as gr
from predict import run, decode_b64_to_file



def generate(description=None, duration=15, temperature=0.5, top_p=0.7, top_k=50,
             extend_stride=2, encoded_music_file_name=None):
    outputs = run(
        descriptions=[description, description, description],
        generation_params={
            "duration": duration,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "extend_stride": extend_stride
        },
        encoded_music_file_name=encoded_music_file_name
    )
    for k, v in outputs.items():
        decode_b64_to_file(v, k)
    return ["0.wav", "1.wav", "2.wav"]

iface = gr.Interface(
    generate,
    [
        gr.components.Textbox(lines=1, value="lo-fi piano music", label="Description of Music"),
        gr.components.Slider(minimum=1, maximum=30, step=1, value=15, label="Duration in seconds"),
        gr.components.Slider(minimum=0, maximum=1, step=0.1, value=0.5, label="Temperature"),
        gr.components.Slider(minimum=0, maximum=1, step=0.1, value=0.7, label="Top P"),
        gr.components.Slider(minimum=0, maximum=100, step=5, value=50, label="Top K"),
        gr.components.Slider(minimum=0, maximum=10, step=0.5, value=2, label="Extend Stride"),
        gr.components.Audio(label="Optional melody recording (WAV)", source="microphone", type="filepath")
    ],
    [
        gr.components.Audio(label="Generated music file", autoplay=True),
        gr.components.Audio(label="Generated music file", autoplay=False),
        gr.components.Audio(label="Generated music file", autoplay=False)
    ],
    live=False,
    enable_queue=True
)

# Replace these with your desired credentials
username = "musicgen"
password = "12345"

iface.queue().launch(share=True) #, auth=(username, password))
