from flask import Flask, render_template, request
import time
import base64
from runwayml import RunwayML

app = Flask(__name__)

client = RunwayML()

@app.route('/', methods=['GET', 'POST'])
def index():
    video_url = None
    if request.method == 'POST' and 'image' in request.files:
        image_file = request.files['image']
        prompt_text = request.form['prompt']

        # Encode image to base64
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Create a new image-to-video task
        task = client.image_to_video.create(
            model='gen3a_turbo',
            prompt_image=f"data:image/png;base64,{base64_image}",
            prompt_text=prompt_text,
        )
        task_id = task.id

        # Poll the task until it's complete
        time.sleep(5)
        task = client.tasks.retrieve(task_id)
        while task.status not in ['SUCCEEDED', 'FAILED']:
            time.sleep(10)
            task = client.tasks.retrieve(task_id)

        if task.status == 'SUCCEEDED':
            video_url = task.output[0]

    return render_template('index.html', video_url=video_url)

if __name__ == '__main__':
    app.run(debug=True)
