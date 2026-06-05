module.exports = {
  daemon: true,
  run: [
    {
      method: "shell.run",
      params: {
        venv: "env",                // Edit this to customize the venv folder path
        env: { },                   // Edit this to customize environment variables (see documentation)
        path: "app",                // Edit this to customize the path to start the shell from
        message: [
          "python app.py",    // Edit with your custom commands
        ],
        on: [{
          event: "/(http:\\/\\/[0-9.:]+)/",
          done: true
        }]
      }
    },
    {
      // This step sets the local variable 'url'.
      // This local variable will be used in pinokio.js to display the "Open WebUI" tab when the value is set.
      method: "local.set",
      params: {
        url: "{{input.event[1]}}"
      }
    }
  ]
}
