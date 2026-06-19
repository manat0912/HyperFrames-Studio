module.exports = {
  run: [
    {
      method: "shell.run",
      params: {
        message: [
          "git clone https://github.com/heygen-com/hyperframes.git app",
        ]
      }
    },
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "uv pip install -r ../requirements.txt"
        ]
      }
    },
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          path: "app",
        }
      }
    },
    {
      method: "shell.run",
      params: {
        path: "app",
        message: [
          "bun install",
          "bun run build"
        ]
      }
    },
    {
      method: "shell.run",
      params: {
        path: "app",
        message: 'npx -y skills add heygen-com/hyperframes --skill "*" --yes --global'
      }
    },
    {
      method: "input",
      params: {
        title: "Installation successful!",
        description: "You can use your Agent now to create your first video using the /hyperframes skill.\n(It is expected that 16 skills will not be installed!)\nYou can close the app now. You won't need it anymore unless you want to update or uninstall it. Your Agent can even use hyperframes when Pinokio is not running."
      }
    }
  ]
}
