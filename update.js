module.exports = {
  run: [
    {
      method: "shell.run",
      params: {
        message: "git pull"
      }
    },
    {
      method: "shell.run",
      params: {
        path: "app",
        message: "git pull"
      }
    },
    // Copy updated custom Gradio/Python files into the app folder
    {
      method: "fs.copy",
      params: {
        src: "app.py",
        dest: "app/app.py"
      }
    },
    {
      method: "fs.copy",
      params: {
        src: "requirements.txt",
        dest: "app/requirements.txt"
      }
    },
    // Re-install requirements
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "uv pip install -r requirements.txt"
        ]
      }
    }
  ]
}
