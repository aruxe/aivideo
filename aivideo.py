from flask import Flask, render_template, request, jsonify, url_for
import time
import base64
from runwayml import RunwayML

app = Flask(__name__)

# Test mode flag
TEST_MODE = True  # Set to False to use the real API

client = RunwayML()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    prompt_text = request.form['prompt']

    if TEST_MODE:
        time.sleep(10)
        # Simulate API response in test mode
        video_url = url_for('static', filename='videos/test.mp4')
    else:
        # Use the real API
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Create a new image-to-video task
        task = client.image_to_video.create(
            model='gen3a_turbo',
            prompt_image=f"data:image/png;base64,{base64_image}",
            prompt_text=prompt_text,
        )
        task_id = task.id

        # Poll the task until it's complete
        time.sleep(10)
        task = client.tasks.retrieve(task_id)
        while task.status not in ['SUCCEEDED', 'FAILED']:
            time.sleep(10)
            task = client.tasks.retrieve(task_id)

        if task.status == 'SUCCEEDED':
            video_url = task.output[0]
        else:
            return jsonify({'error': 'Video generation failed'}), 500

    return jsonify({'video_url': video_url})

if __name__ == '__main__':
    app.run(debug=True)
