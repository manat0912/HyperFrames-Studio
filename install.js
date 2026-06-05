module.exports = {
  run: [
    // Edit this step to customize the git repository to use
    {
      method: "shell.run",
      params: {
        message: [
          "git clone https://github.com/heygen-com/hyperframes.git app",
        ]
      }
    },
    // Copy custom Gradio/Python files into the cloned app folder
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
    // Edit this step with your custom install commands
    {
      method: "shell.run",
      params: {
        venv: "env",                // Edit this to customize the venv folder path
        path: "app",                // Edit this to customize the path to start the shell from
        message: [
          "uv pip install -r requirements.txt"
        ]
      }
    },
    // Delete this step if your project does not use torch
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",                // Edit this to customize the venv folder path
          path: "app",                // Edit this to customize the path to start the shell from
          // flashattention: true   // uncomment this line if your project requires flashattention
          // xformers: true   // uncomment this line if your project requires xformers
          // triton: true   // uncomment this line if your project requires triton
          // sageattention: true   // uncomment this line if your project requires sageattention
        }
      }
    },
  ]
}
