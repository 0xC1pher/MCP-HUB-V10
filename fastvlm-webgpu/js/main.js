class VisionHubApp {
  constructor() {
    this.video = document.getElementById('webcam-video');
    this.canvas = document.getElementById('video-canvas');
    this.ctx = this.canvas.getContext('2d');
    this.captionText = document.getElementById('caption-text');
    this.playPauseBtn = document.getElementById('play-pause-btn');
    this.promptInput = document.getElementById('prompt-input');
    this.sendPromptBtn = document.getElementById('send-prompt-btn');
    this.suggestions = document.querySelectorAll('.suggestion-chip');

    this.isRunning = false;
    this.processor = null;
    this.currentPrompt = 'Describe what you see in detail.';
    this.modelLoaded = false;

    this.initDrag();
    this.bindEvents();
    this.loadModel();
  }

  async loadModel() {
    try {
      console.log('Loading FastVLM model...');
      this.processor = await pipeline('image-to-text', 'Xenova/FastVLM-0.5B-ONNX');
      this.modelLoaded = true;
      console.log('Model loaded successfully!');
    } catch (error) {
      console.error('Failed to load model:', error);
      this.captionText.textContent = 'Model load failed. Check console.';
    }
  }

  bindEvents() {
    this.playPauseBtn.addEventListener('click', () => this.toggle());
    this.sendPromptBtn.addEventListener('click', () => this.updatePrompt());
    this.promptInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.updatePrompt();
    });
    this.suggestions.forEach(chip => {
      chip.addEventListener('click', () => {
        this.promptInput.value = chip.dataset.prompt;
        this.updatePrompt();
      });
    });
  }

  async toggle() {
    if (this.isRunning) {
      this.stop();
    } else {
      await this.start();
    }
  }

  async start() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      this.video.srcObject = stream;
      await this.video.play();
      this.canvas.width = this.video.videoWidth;
      this.canvas.height = this.video.videoHeight;
      this.isRunning = true;
      this.playPauseBtn.textContent = '⏸️ Pause';
      this.inferenceLoop();
    } catch (error) {
      console.error('Error accessing camera:', error);
      this.captionText.textContent = 'Camera access denied.';
    }
  }

  stop() {
    if (this.video.srcObject) {
      this.video.srcObject.getTracks().forEach(track => track.stop());
    }
    this.isRunning = false;
    this.playPauseBtn.textContent = '▶️ Start';
    cancelAnimationFrame(this.rafId);
  }

  updatePrompt() {
    this.currentPrompt = this.promptInput.value || 'Describe what you see.';
  }

  async inferenceLoop() {
    if (!this.isRunning || !this.modelLoaded) return;

    this.ctx.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
    const imageDataUrl = this.canvas.toDataURL('image/jpeg', 0.8);

    try {
      const output = await this.processor(imageDataUrl, {
        prompt: this.currentPrompt,
        max_new_tokens: 100
      });
      this.captionText.textContent = output[0].generated_text;
    } catch (error) {
      console.error('Inference error:', error);
      this.captionText.textContent = 'Inference failed. Retrying...';
    }

    this.rafId = requestAnimationFrame(() => this.inferenceLoop());
  }

  initDrag() {
    const draggables = document.querySelectorAll('.draggable');
    draggables.forEach(el => {
      let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
      el.onmousedown = dragMouseDown;

      function dragMouseDown(e) {
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDrag;
        document.onmousemove = elementDrag;
      }

      function elementDrag(e) {
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        el.style.top = (el.offsetTop - pos2) + 'px';
        el.style.left = (el.offsetLeft - pos1) + 'px';
        el.style.right = 'auto';
        el.style.bottom = 'auto';
      }

      function closeDrag() {
        document.onmouseup = null;
        document.onmousemove = null;
      }
    });
  }
}

// Initialize app when DOM loaded
document.addEventListener('DOMContentLoaded', () => {
  new VisionHubApp();
});
