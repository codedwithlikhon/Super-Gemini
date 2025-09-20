// Executes a node.js script safely.
const { exec } = require('child_process');
const scriptPath = process.argv[2];

if (scriptPath) {
  console.log(`Running node script: ${scriptPath}`);
  exec(`node ${scriptPath}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
  });
}
