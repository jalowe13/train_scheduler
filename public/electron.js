const { app, BrowserWindow, screen } = require("electron");
const { spawn, exec } = require("child_process");
const psTree = require("ps-tree");
const path = require("path");
const url = require("url");
const waitOn = require("wait-on");
const chalk = require("chalk");

// Declare variables for the backend and frontend processes
let frontend, backend, dynamo, uvicorn;
// PID of last node.js process instance when application starts
let lastChildPid;

function createWindow() {
  // Create the browser window and listen for screen size changes
  console.log("Creating window...");
  process.env.FORCE_COLOR = 1; // Force chalk colors
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  const win = new BrowserWindow({
    width: width,
    height: height,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      zoomFactor: 1.0, // Disable zooming
    },
    show: false, // Don't show the window initially
  });

  // Arguments for staring go server or not

  const args = process.argv.slice(2);

  // Convert argument into boolean to start go service or not
  const startGo = args.includes("true");

  console.log(`Starting up`);

  // Only start go backend if argument is true
  const processToKill = "server.exe";

  if (startGo) {
    console.log(chalk.green("Starting go server"));
    backend = spawn("npm", ["run", "start-go"], { shell: true });
    backend.stdout.on("data", (data) => {
      console.log(chalk.green(`[Backend]: ${data}`));
    });
  } else {
    console.log(chalk.red("Not starting go server"));
    console.log(
      chalk.red("Please start go uvicorn manually with npm run start-uvicorn")
    );
    console.log(chalk.red("Starting dynamo"));
    dynamo = spawn("npm", ["run", "start-dynamo"], { shell: true });
    dynamo.stdout.on("data", (data) => {
      console.log(chalk.green(`[DynamoGB]: ${data}`));
    });
  }

  frontend = spawn("npm", ["run", "start"], { shell: true, env: process.env });

  console.log(`Started Node.js process with PID: ${frontend.pid}`);

  frontend.stdout.on("data", (data) => {
    console.log(chalk.blue(`[Frontend]: ${data.toString()}`));
  });

  console.log("App started!");
  // Adjust screen size per window size
  screen.on("display-metrics-changed", () => {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;
    win.setSize(width, height);
  });

  // Start URL for production
  const startUrl =
    process.env.ELECTRON_START_URL ||
    url.format({
      pathname: path.join(__dirname, "/../build/index.html"),
      protocol: "file:",
      slashes: true,
    });

  console.log("Starting the server...");

  //load the index.html from a url wait for the server to be ready
  waitOn({ resources: ["http://localhost:3000"] }, (err) => {
    if (err) {
      console.error("Error waiting for the server:", err);
      return;
    }

    // Load the React app
    console.log("Server ready!");

    win.loadURL("http://localhost:3000");
    // Show when the React app is ready

    // Disable Scrollbar
    win.webContents.on("did-finish-load", () => {
      win.webContents.insertCSS(`
      body {
        overflow: hidden;
      }
    `);
    });
    win.once("ready-to-show", () => {
      win.setTitle("PassNow");
      win.maximize();
      win.show();
      // Get the child processes of the frontend
      psTree(frontend.pid, (err, children) => {
        if (err) {
          console.error(`Failed to get child processes: ${err}`);
        } else {
          console.log("Child processes:", children);
          lastChildPid = children[children.length - 1].PID;
          console.log(`Last child PID: ${lastChildPid}`);
        }
      });
    });
  });
}

// App Listener events

app.whenReady().then(createWindow);

app.on("before-quit", () => {
  console.log("App is quitting...");
  // Killing last child node process for port 3000
  exec(`taskkill /PID ${lastChildPid} /T /F`, (err) => {
    if (err) {
      console.error(`Failed to kill process ${lastChildPid}: ${err}`);
    } else {
      console.log(`Successfully killed process ${lastChildPid}`);
    }
  });
});

app.on("window-all-closed", () => {
  // The port number you're interested in
  // Get a list of child processes
  if (process.platform !== "darwin") {
    console.log("Quitting app");
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
