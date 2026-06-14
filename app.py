import os
import re
import sys
import subprocess
import gradio as gr
import torch
import devicetorch

# Define templates
TEMPLATES = {
    "Minimal Intro": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body { margin: 0; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; font-family: 'Helvetica Neue', Arial, sans-serif; }
    #root { width: 1920px; height: 1080px; position: relative; overflow: hidden; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .title-container { text-align: center; opacity: 0; transform: translateY(50px); animation: fadeInUp 1.5s cubic-bezier(0.25, 1, 0.5, 1) forwards; animation-delay: 0.5s; }
    h1 { font-size: 140px; margin: 0; font-weight: 800; letter-spacing: -2px; text-shadow: 0 10px 30px rgba(0,0,0,0.3); }
    p { font-size: 48px; margin-top: 20px; color: #a0c4ff; font-weight: 300; }
    
    @keyframes fadeInUp {
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div id="root" data-composition-id="minimal-intro" data-width="1920" data-height="1080" data-duration="5">
    <div class="title-container" data-start="0" data-duration="5" data-track-index="1">
      <h1>HyperFrames Studio</h1>
      <p>Render Videos with Web Technologies</p>
    </div>
  </div>
</body>
</html>""",

    "Swiss Grid": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body { margin: 0; background: #f4f4f4; color: #111; font-family: 'Helvetica Neue', Arial, sans-serif; }
    #root { width: 1920px; height: 1080px; position: relative; overflow: hidden; box-sizing: border-box; padding: 100px; display: grid; grid-template-rows: auto 1fr; }
    
    .header { border-bottom: 5px solid #111; padding-bottom: 20px; opacity: 0; animation: fadeIn 1s forwards; }
    .meta-label { font-size: 24px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }
    
    .content { display: grid; grid-template-columns: 1fr 1fr; align-items: end; margin-top: 50px; }
    .title { font-size: 120px; font-weight: 900; line-height: 0.95; letter-spacing: -4px; opacity: 0; transform: translateX(-50px); animation: slideInLeft 1s forwards; animation-delay: 0.5s; }
    .desc { font-size: 36px; line-height: 1.4; color: #555; padding-left: 50px; border-left: 3px solid #111; opacity: 0; animation: fadeIn 1.2s forwards; animation-delay: 1s; }
    
    @keyframes fadeIn { to { opacity: 1; } }
    @keyframes slideInLeft { to { opacity: 1; transform: translateX(0); } }
  </style>
</head>
<body>
  <div id="root" data-composition-id="swiss-grid" data-width="1920" data-height="1080" data-duration="6">
    <div class="header" data-start="0" data-duration="6" data-track-index="1">
      <div class="meta-label">Design System v1.0 // HeyGen</div>
    </div>
    <div class="content" data-start="0.2" data-duration="5.8" data-track-index="2">
      <div class="title">SWISS<br>GRID.</div>
      <div class="desc">A structured layout focusing on cleanliness, readability, and objectivity. Built entirely using HTML5 and CSS Grid.</div>
    </div>
  </div>
</body>
</html>""",

    "Kinetic Type": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body { margin: 0; background: #050505; color: #fff; font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif; overflow: hidden; }
    #root { width: 1920px; height: 1080px; position: relative; }
    
    .slide { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 220px; text-transform: uppercase; letter-spacing: -2px; }
    
    .word1 { opacity: 0; transform: scale(0.5); animation: popIn 1s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
    .word2 { opacity: 0; transform: rotate(-10deg) translateY(100px); animation: slideUpSkew 1s cubic-bezier(0.19, 1, 0.22, 1) forwards; }
    .word3 { opacity: 0; transform: scale(2); filter: blur(20px); animation: focusIn 1s ease-out forwards; }
    
    @keyframes popIn { to { opacity: 1; transform: scale(1); } }
    @keyframes slideUpSkew { to { opacity: 1; transform: rotate(0deg) translateY(0); } }
    @keyframes focusIn { to { opacity: 1; transform: scale(1); filter: blur(0); } }
  </style>
</head>
<body>
  <div id="root" data-composition-id="kinetic-type" data-width="1920" data-height="1080" data-duration="6">
    <!-- Slide 1 (0s to 2s) -->
    <div class="slide" data-start="0" data-duration="2" data-track-index="1">
      <div class="word1">FAST.</div>
    </div>
    <!-- Slide 2 (2s to 4s) -->
    <div class="slide" data-start="2" data-duration="2" data-track-index="1">
      <div class="word2" style="color: #ff0055;">BOLD.</div>
    </div>
    <!-- Slide 3 (4s to 6s) -->
    <div class="slide" data-start="4" data-duration="2" data-track-index="1">
      <div class="word3" style="color: #00ffcc;">DETERMINISTIC.</div>
    </div>
  </div>
</body>
</html>""",

    "Vignelli Portrait (9:16)": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body { margin: 0; background: #ff3300; color: white; font-family: 'Helvetica Neue', Arial, sans-serif; }
    #root { width: 1080px; height: 1920px; position: relative; overflow: hidden; box-sizing: border-box; padding: 80px; display: flex; flex-direction: column; justify-content: space-between; }
    
    .top-text { font-size: 40px; font-weight: 700; border-top: 10px solid white; padding-top: 20px; opacity: 0; animation: fadeIn 1s forwards; }
    .mid-text { font-size: 160px; font-weight: 900; line-height: 0.85; letter-spacing: -6px; opacity: 0; transform: translateY(50px); animation: fadeInUp 1s forwards; animation-delay: 0.4s; }
    .bot-text { font-size: 36px; font-weight: 400; line-height: 1.4; opacity: 0; animation: fadeIn 1s forwards; animation-delay: 0.8s; }
    
    @keyframes fadeIn { to { opacity: 1; } }
    @keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }
  </style>
</head>
<body>
  <div id="root" data-composition-id="vignelli-portrait" data-width="1080" data-height="1920" data-duration="5">
    <div class="top-text" data-start="0" data-duration="5" data-track-index="1">
      NO. 42
    </div>
    <div class="mid-text" data-start="0" data-duration="5" data-track-index="2">
      MODERN<br>POSTER<br>DESIGN.
    </div>
    <div class="bot-text" data-start="0" data-duration="5" data-track-index="1">
      A beautiful portrait composition based on the grid principles of Massimo Vignelli.
    </div>
  </div>
</body>
</html>""",

    "Video Background with Captions": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body { margin: 0; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; font-family: 'Helvetica Neue', Arial, sans-serif; overflow: hidden; }
    #root { width: 1920px; height: 1080px; position: relative; overflow: hidden; }
    
    /* Background video styling */
    .bg-video {
      position: absolute;
      top: 0;
      left: 0;
      width: 1920px;
      height: 1080px;
      object-fit: cover;
      z-index: 1;
    }
    
    /* Overlay for better text readability */
    .overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.5);
      z-index: 2;
    }
    
    /* Captions container */
    .captions-container {
      position: absolute;
      inset: 0;
      display: flex;
      justify-content: center;
      align-items: flex-end;
      padding-bottom: 180px;
      z-index: 3;
      pointer-events: none;
    }
    
    .caption-box {
      background-color: rgba(15, 23, 42, 0.85);
      border: 2px solid rgba(255, 255, 255, 0.1);
      padding: 24px 48px;
      border-radius: 24px;
      display: flex;
      justify-content: center;
      align-items: center;
      min-width: 200px;
      max-width: 85%;
      opacity: 0;
      transform: translateY(20px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .caption-text {
      color: #fff;
      font-size: 56px;
      font-weight: 800;
      text-align: center;
      line-height: 1.25;
      text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
  </style>
</head>
<body>
  <div id="root" data-composition-id="video-captions" data-width="1920" data-height="1080" data-duration="10">
    <!-- Play background video if available (saved as input_video.mp4) -->
    <video class="bg-video" src="input_video.mp4" data-start="0" data-track-index="1" muted></video>
    
    <!-- Play audio track if available (saved as input_audio.wav) -->
    <audio id="el-audio" src="input_audio.wav" data-start="0" data-track-index="2" data-volume="1"></audio>
    
    <div class="overlay"></div>
    
    <div class="captions-container">
      <div id="caption-box" class="caption-box">
        <span id="caption-text" class="caption-text">Upload audio and video to render!</span>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <script>
    (function () {
      // This array is automatically filled by the transcription step when input_audio.wav is supplied
      const script = [
        { "text": "Upload", "start": 0.0, "end": 1.0 },
        { "text": "an", "start": 1.0, "end": 2.0 },
        { "text": "audio", "start": 2.0, "end": 3.0 },
        { "text": "file", "start": 3.0, "end": 4.0 },
        { "text": "and", "start": 4.0, "end": 5.0 },
        { "text": "a", "start": 5.0, "end": 6.0 },
        { "text": "video", "start": 6.0, "end": 7.0 },
        { "text": "to", "start": 7.0, "end": 8.0 },
        { "text": "see", "start": 8.0, "end": 9.0 },
        { "text": "automatic", "start": 9.0, "end": 10.0 },
        { "text": "captions!", "start": 10.0, "end": 11.0 }
      ];

      // Group words into lines (max 4 words per line)
      const lines = [];
      for (let i = 0; i < script.length; i += 4) {
        const lineWords = script.slice(i, i + 4);
        lines.push({
          text: lineWords.map((w) => w.text).join(" "),
          start: lineWords[0].start,
          end: lineWords[lineWords.length - 1].end,
        });
      }

      const tl = gsap.timeline({ paused: true });
      const box = document.getElementById("caption-box");
      const textEl = document.getElementById("caption-text");

      lines.forEach((line) => {
        // Show line
        tl.set(box, { visibility: "visible" }, line.start);
        tl.to(
          box,
          {
            opacity: 1,
            y: 0,
            duration: 0.15,
            ease: "power2.out",
            onStart: () => {
              textEl.textContent = line.text;
            },
          },
          line.start,
        );

        // Hide line
        tl.to(
          box,
          {
            opacity: 0,
            y: -10,
            duration: 0.15,
            ease: "power2.in",
          },
          line.end,
        );

        // Hard kill
        tl.set(box, { opacity: 0, y: 20, visibility: "hidden" }, line.end + 0.01);
      });

      window.__timelines = window.__timelines || {};
      window.__timelines["video-captions"] = tl;
    })();
  </script>
</body>
</html>"""
}

SYSTEM_PROMPT = """You are an expert HyperFrames developer. Your job is to generate or modify valid HTML video compositions based on the user's prompt.
HyperFrames is a framework for turning HTML, CSS, media, and seekable animations into MP4 videos.
Guidelines for generating valid HyperFrames HTML:
1. The output MUST be a single, complete, valid HTML document.
2. The root element MUST be <div id="root" data-composition-id="..." data-width="1920" data-height="1080" data-duration="...">.
3. Use GSAP (GreenSock) for animations. Include the GSAP CDN script tag:
   <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
4. Do NOT use markdown code blocks or explanations in your response. Return ONLY the raw HTML code.
5. All animations must be seekable, deterministic, and mapped to the timeline via GSAP timeline registered on window.__timelines["YOUR_COMPOSITION_ID"] = tl;
6. Video elements must be muted and play in separate tags from audio:
   - <video src="input_video.mp4" data-start="0" data-track-index="1" muted></video>
   - <audio src="input_audio.wav" data-start="0" data-track-index="2" data-volume="1"></audio>
7. If the user refers to input video or audio, use "input_video.mp4" or "input_audio.wav" as the source.
8. Support caption rendering when captions script is needed:
   const script = [...]; (JSON array of word objects with text, start, end).

Return ONLY the raw HTML code. Do not wrap it in markdown code blocks or backticks. Start directly with <!DOCTYPE html> and end with </html>."""

def generate_html_with_ai(prompt, provider, url, model, current_html):
    import requests
    import json
    
    if provider == "None" or not provider:
        return current_html, "⚠️ Please select a provider (Ollama or LM Studio) first."
        
    if not prompt:
        return current_html, "⚠️ Please enter an AI prompt."
        
    headers = {
        "Content-Type": "application/json"
    }
    
    # Construct standard chat completion payload
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the current HTML:\\n```html\\n{current_html}\\n```\\n\\nUser request: {prompt}"}
        ],
        "temperature": 0.2
    }
    
    # Ensure correct URL endpoint
    base_url = url.strip()
    if not base_url.endswith("/chat/completions"):
        if base_url.endswith("/"):
            base_url = base_url + "chat/completions"
        else:
            base_url = base_url + "/chat/completions"
            
    try:
        response = requests.post(base_url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            ai_code = data["choices"][0]["message"]["content"].strip()
            
            # Clean up markdown block wraps if any
            if ai_code.startswith("```html"):
                ai_code = ai_code[7:]
            elif ai_code.startswith("```"):
                ai_code = ai_code[3:]
            if ai_code.endswith("```"):
                ai_code = ai_code[:-3]
                
            ai_code = ai_code.strip()
            
            return ai_code, "🎉 HTML code successfully generated and updated in editor."
        else:
            return current_html, f"❌ API Error (HTTP {response.status_code}): {response.text}"
    except Exception as e:
        return current_html, f"❌ Failed to connect to {provider} at {base_url}: {str(e)}"

def generate_html_with_cloud_ai(prompt, cloud_model, api_key, current_html):
    import requests
    import json
    
    if not prompt:
        return current_html, "⚠️ Please enter an AI prompt."
        
    # Default Gemini Key
    gemini_default_key = ""
    
    # Identify provider and model properties
    if "Gemini" in cloud_model:
        provider = "Gemini"
        actual_key = api_key.strip() if api_key.strip() else gemini_default_key
        if "3.1 Flash" in cloud_model:
            model_id = "gemini-3.1-flash"
        elif "3.1 Pro" in cloud_model:
            model_id = "gemini-3.1-pro"
        elif "2.0 Flash" in cloud_model:
            model_id = "gemini-2.0-flash-exp"
        elif "1.5 Pro" in cloud_model:
            model_id = "gemini-1.5-pro"
        else:
            model_id = "gemini-1.5-flash"
        
        url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {actual_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the current HTML:\n```html\n{current_html}\n```\n\nUser request: {prompt}"}
            ],
            "temperature": 0.2
        }
    elif "GPT" in cloud_model:
        provider = "OpenAI"
        actual_key = api_key.strip()
        if not actual_key:
            return current_html, "⚠️ OpenAI API key is required for GPT models."
        
        if "GPT-4o-mini" in cloud_model:
            model_id = "gpt-4o-mini"
        else:
            model_id = "gpt-4o"
            
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {actual_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the current HTML:\n```html\n{current_html}\n```\n\nUser request: {prompt}"}
            ],
            "temperature": 0.2
        }
    elif "Claude" in cloud_model:
        provider = "Anthropic"
        actual_key = api_key.strip()
        if not actual_key:
            return current_html, "⚠️ Anthropic API key is required for Claude models."
            
        if "3.7 Sonnet" in cloud_model:
            model_id = "claude-3-7-sonnet-20250219"
        elif "3.5 Sonnet" in cloud_model:
            model_id = "claude-3-5-sonnet-20241022"
        elif "Opus" in cloud_model:
            model_id = "claude-3-opus-20240229"
        else:
            model_id = "claude-3-5-haiku-20241022"
            
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": actual_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": model_id,
            "max_tokens": 8192,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": f"Here is the current HTML:\n```html\n{current_html}\n```\n\nUser request: {prompt}"}
            ],
            "temperature": 0.2
        }
    else:
        return current_html, "⚠️ Unknown cloud provider."

    try:
        if provider == "Anthropic":
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                ai_code = data["content"][0]["text"].strip()
            else:
                return current_html, f"❌ Anthropic API Error (HTTP {response.status_code}): {response.text}"
        else:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                ai_code = data["choices"][0]["message"]["content"].strip()
            else:
                return current_html, f"❌ {provider} API Error (HTTP {response.status_code}): {response.text}"
                
        # Clean up markdown block wraps if any
        if ai_code.startswith("```html"):
            ai_code = ai_code[7:]
        elif ai_code.startswith("```"):
            ai_code = ai_code[3:]
        if ai_code.endswith("```"):
            ai_code = ai_code[:-3]
            
        ai_code = ai_code.strip()
        return ai_code, f"🎉 HTML code successfully generated using {cloud_model} and updated in editor."
        
    except Exception as e:
        return current_html, f"❌ Failed to connect to {provider}: {str(e)}"

def get_torch_info():
    try:
        device = devicetorch.get(torch)
        device_name = torch.cuda.get_device_name(0) if device == "cuda" else "N/A"
        return f"🔥 Device: {device.upper()} (GPU Name: {device_name})"
    except Exception as e:
        return f"⚠️ Torch Device Error: {str(e)}"

def inject_attributes(html, duration, width, height):
    match = re.search(r'(<div[^>]+id=["\']root["\'][^>]*>)', html)
    if match:
        root_tag = match.group(1)
        new_root_tag = re.sub(r'\s+data-duration=["\'][^"\']*["\']', '', root_tag)
        new_root_tag = re.sub(r'\s+data-width=["\'][^"\']*["\']', '', new_root_tag)
        new_root_tag = re.sub(r'\s+data-height=["\'][^"\']*["\']', '', new_root_tag)
        
        # Inject new values
        new_root_tag = new_root_tag.replace('>', f' data-duration="{duration}" data-width="{width}" data-height="{height}">')
        html = html.replace(root_tag, new_root_tag)
    return html

def render_video(html_code, duration, width, height, video_file=None, audio_file=None):
    import shutil
    logs = ""
    
    # Handle video file
    if video_file:
        try:
            shutil.copy(video_file, "input_video.mp4")
            logs += "✅ Video asset copied to 'input_video.mp4'\n"
            yield logs, None
        except Exception as e:
            logs += f"⚠️ Error copying video file: {str(e)}\n"
            yield logs, None
    else:
        if os.path.exists("input_video.mp4"):
            try:
                os.remove("input_video.mp4")
                logs += "ℹ️ Removed previous 'input_video.mp4'\n"
                yield logs, None
            except Exception:
                pass

    # Handle audio file
    if audio_file:
        try:
            shutil.copy(audio_file, "input_audio.wav")
            logs += "✅ Audio asset copied to 'input_audio.wav'\n"
            yield logs, None
        except Exception as e:
            logs += f"⚠️ Error copying audio file: {str(e)}\n"
            yield logs, None
    else:
        if os.path.exists("input_audio.wav"):
            try:
                os.remove("input_audio.wav")
                logs += "ℹ️ Removed previous 'input_audio.wav'\n"
                yield logs, None
            except Exception:
                pass

    # Prepare HTML with selected settings
    processed_html = inject_attributes(html_code, duration, width, height)
    
    # Save code to index.html in current folder
    html_path = "index.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(processed_html)
        
    output_filename = "output.mp4"
    if os.path.exists(output_filename):
        try:
            os.remove(output_filename)
        except Exception:
            pass
            
    # If audio is present, run transcription BEFORE rendering
    if audio_file:
        transcribe_cmd = ["npx", "-y", "hyperframes", "transcribe", "input_audio.wav", "--dir", "."]
        logs += f"Starting transcription command: {' '.join(transcribe_cmd)}\n\n"
        yield logs, None
        
        try:
            # We run the transcribe command and capture logs live
            process = subprocess.Popen(
                transcribe_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True # needed for npx on windows
            )
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                logs += line
                yield logs, None
                
            process.wait()
            
            if process.returncode == 0:
                logs += f"\n🎉 Transcription successful! transcript.json saved and index.html patched.\n\n"
                yield logs, None
            else:
                logs += f"\n❌ Transcription failed with exit code: {process.returncode}\n\n"
                yield logs, None
                
        except Exception as e:
            logs += f"\n❌ Transcription Error: {str(e)}\n\n"
            yield logs, None

    # Command to run npx hyperframes render
    # We specify --output output.mp4
    cmd = ["npx", "-y", "hyperframes", "render", "--output", output_filename]
    
    logs += f"Starting rendering command: {' '.join(cmd)}\n\n"
    yield logs, None
    
    try:
        # We run the command and capture logs live
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True # needed for npx on windows
        )
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
            logs += line
            yield logs, None
            
        process.wait()
        
        if process.returncode == 0 and os.path.exists(output_filename):
            logs += f"\n🎉 Rendering successful! Video saved to: {os.path.abspath(output_filename)}"
            yield logs, output_filename
        else:
            logs += f"\n❌ Rendering failed with exit code: {process.returncode}"
            yield logs, None
            
    except Exception as e:
        logs += f"\n❌ Execution Error: {str(e)}"
        yield logs, None

# Gradio Interface
with gr.Blocks(title="HyperFrames Studio", css="""
    body { background-color: #0f172a; }
    #terminal-box textarea {
        background-color: #020617 !important;
        color: #38bdf8 !important;
        font-family: 'Courier New', Courier, monospace !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
""") as demo:
    gr.Markdown(
        """
        # 🎬 HyperFrames Studio (Gradio Wrapper)
        Generate stunning, deterministic MP4 videos using HTML, CSS, and animations directly inside Pinokio.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=3):
            # Template Selector
            template_dropdown = gr.Dropdown(
                choices=list(TEMPLATES.keys()),
                value="Minimal Intro",
                label="Select Starting Template"
            )
            
            # HTML Code Area - Local AI Code Assistant
            with gr.Accordion("🔮 Local AI Code Assistant (Ollama, LM Studio, Jan.ai, LLaMA.cpp, KoboldCPP)", open=False):
                with gr.Row():
                    llm_provider = gr.Radio(
                        choices=["None", "Ollama", "LM Studio", "Llama.cpp", "Jan.ai", "KoboldCPP"],
                        value="None",
                        label="Local Provider"
                    )
                with gr.Row():
                    llm_url = gr.Textbox(
                        label="API Base URL",
                        value="http://localhost:11434/v1",
                        placeholder="e.g. http://localhost:11434/v1"
                    )
                    llm_model = gr.Textbox(
                        label="Model Name",
                        value="qwen2.5-coder",
                        placeholder="e.g. qwen2.5-coder"
                    )
                ai_prompt = gr.Textbox(
                    label="What would you like the Local AI to build or edit?",
                    placeholder="e.g. 'Add a fade-in text overlay in the center' or 'Create a 10-second slideshow from scratch'",
                    lines=3
                )
                ai_generate_btn = gr.Button("🔮 Generate / Update HTML Code (Local)", variant="secondary")
                ai_status = gr.Markdown(value="*Select a local provider, specify model details, write a prompt, and click generate.*")

            # HTML Code Area - Closed Source AI Code Assistant
            with gr.Accordion("🌐 Closed Source AI Code Assistant (Gemini, OpenAI, Claude)", open=False):
                with gr.Row():
                    cloud_provider = gr.Dropdown(
                        choices=[
                            "Gemini 3.1 Flash (Free API Key)",
                            "Gemini 3.1 Pro (Free API Key)",
                            "Gemini 2.0 Flash (Free API Key)",
                            "Gemini 1.5 Pro (Free API Key)",
                            "Gemini 1.5 Flash (Free API Key)",
                            "GPT-4o (Requires OpenAI Key)",
                            "GPT-4o-mini (Requires OpenAI Key)",
                            "Claude 3.7 Sonnet (Requires Anthropic Key)",
                            "Claude 3.5 Sonnet (Requires Anthropic Key)",
                            "Claude 3.5 Haiku (Requires Anthropic Key)",
                            "Claude 3 Opus (Requires Anthropic Key)"
                        ],
                        value="Gemini 3.1 Flash (Free API Key)",
                        label="Cloud Model"
                    )
                with gr.Row():
                    cloud_api_key = gr.Textbox(
                        label="API Key (Leave blank to use pre-configured Gemini Key)",
                        placeholder="Enter your API Key here",
                        type="password"
                    )
                cloud_prompt = gr.Textbox(
                    label="What would you like the Cloud AI to build or edit?",
                    placeholder="e.g. 'Add a fade-in text overlay in the center' or 'Create a 10-second slideshow from scratch'",
                    lines=3
                )
                cloud_generate_btn = gr.Button("🌐 Generate / Update HTML Code (Cloud)", variant="secondary")
                cloud_status = gr.Markdown(value="*Select cloud model, enter API key if required, write a prompt, and click generate.*")

            html_editor = gr.Code(
                value=TEMPLATES["Minimal Intro"],
                language="html",
                label="HTML / CSS / JS Composition Code",
                lines=25
            )
            
            with gr.Row():
                # Slider Controls
                duration_slider = gr.Slider(minimum=1, maximum=60, value=5, step=1, label="Duration (seconds)")
                width_slider = gr.Slider(minimum=256, maximum=3840, value=1920, step=8, label="Width (px)")
                height_slider = gr.Slider(minimum=256, maximum=3840, value=1080, step=8, label="Height (px)")
                
            with gr.Row():
                video_input = gr.Video(label="Upload Video Asset (saved as 'input_video.mp4')", interactive=True)
                audio_input = gr.Audio(label="Upload Audio Asset (saved as 'input_audio.wav')", type="filepath", interactive=True)
                
            render_btn = gr.Button("🚀 Render Video", variant="primary", size="lg")
            
        with gr.Column(scale=2):
            torch_status = gr.Label(value=get_torch_info(), label="System Status")
            
            # Output Video
            video_output = gr.Video(label="Rendered Video Output", interactive=False)
            
            # Live Terminal Logs
            log_output = gr.Textbox(
                value="Ready to render. Select a template or write your own HTML code, then click 'Render Video'.",
                label="Console Output / Build Logs",
                lines=15,
                max_lines=30,
                interactive=False,
                elem_id="terminal-box"
            )
            
    # Event listeners
    def update_llm_defaults(provider):
        if provider == "Ollama":
            return "http://localhost:11434/v1", "qwen2.5-coder"
        elif provider == "LM Studio":
            return "http://localhost:1234/v1", "qwen2.5-coder"
        elif provider == "Jan.ai":
            return "http://localhost:1337/v1", "qwen2.5-coder"
        elif provider == "Llama.cpp":
            return "http://localhost:8080/v1", ""
        elif provider == "KoboldCPP":
            return "http://localhost:5001/v1", ""
        else:
            return "http://localhost:11434/v1", ""
            
    llm_provider.change(
        fn=update_llm_defaults,
        inputs=[llm_provider],
        outputs=[llm_url, llm_model]
    )
    
    ai_generate_btn.click(
        fn=generate_html_with_ai,
        inputs=[ai_prompt, llm_provider, llm_url, llm_model, html_editor],
        outputs=[html_editor, ai_status]
    )

    cloud_generate_btn.click(
        fn=generate_html_with_cloud_ai,
        inputs=[cloud_prompt, cloud_provider, cloud_api_key, html_editor],
        outputs=[html_editor, cloud_status]
    )

    def load_template(name):
        return TEMPLATES[name]
        
    template_dropdown.change(
        fn=load_template,
        inputs=[template_dropdown],
        outputs=[html_editor]
    )
    
    render_btn.click(
        fn=render_video,
        inputs=[html_editor, duration_slider, width_slider, height_slider, video_input, audio_input],
        outputs=[log_output, video_output]
    )

if __name__ == "__main__":
    demo.queue().launch(server_name="127.0.0.1", server_port=7860)
