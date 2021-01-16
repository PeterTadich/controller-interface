# controller-interface
robotic controller interface module (controller-interface)

## Dependencies

There are no dependencies.

## Installation

### Node.js

```bash
npm install https://github.com/PeterTadich/controller-interface
```

### Google Chrome Web browser

No installation required for the Google Chrome Web browser.

## How to use

### Node.js

```js
import * as rcim from 'controller-interface';
```

### Google Chrome Web browser

```js
import * as rcim from './rcim.mjs';
```

## Examples

### Node.js (server side)

Copy the following code to mini-server.js

```js
//ref: https://www.w3schools.com/nodejs/nodejs_url.asp
var http = require('http');
var url = require('url');
var fs = require('fs');

http.createServer(function (req, res) {
  var q = url.parse(req.url, true);
  var filename = "." + q.pathname;
  fs.readFile(filename, function(err, data) {
    if (err) {
      res.writeHead(404, {'Content-Type': 'text/html'});
      return res.end("404 Not Found");
    } 
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.write(data);
    return res.end();
  });
}).listen(8080); 
```

Copy the following code to 30402.html

```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>30402 interface</title>
        <script type="module" src="30402.mjs"></script>
    </head>
    <body>
        <button id="open">open</button><br/>
        <button id="M1CCW">M1 CCW</button>
        <button id="M1CW">M1 CW</button><br/>
        
        <button id="M2CCW">M2 CCW</button>
        <button id="M2CW">M2 CW</button><br/>
        
        <button id="M3CCW">M3 CCW</button>
        <button id="M3CW">M3 CW</button><br/>
        
        <button id="M4CCW">M4 CCW</button>
        <button id="M4CW">M4 CW</button><br/>
        
        <button id="close">close</button> 
    </body>
</html>
```

Copy the following code to 30402.mjs

```js
import * as rcim from './node_modules/controller-interface/rcim.mjs';

//open
document.getElementById('open').addEventListener('click', () => {
    rcim.II30402();
});

document.getElementById('M1CCW').addEventListener('click', () => {
    rcim.II30402.packetSend([0xC1,0x01]); //M1 CCW
});
document.getElementById('M1CW').addEventListener('click', () => {
    rcim.II30402.packetSend([0xC1,0x02]); //M1 CW
});

document.getElementById('M2CCW').addEventListener('click', () => {
    rcim.II30402.packetSend([0xC1,0x04]); //M2 CCW
});
document.getElementById('M2CW').addEventListener('click', () => {
    rcim.II30402.packetSend([0xC1,0x08]); //M2 CW
});

document.getElementById('M3CCW').addEventListener('click', () => {
    rcim.II30402.packetSend([0xC1,0x10]); //M3 CCW
});
document.getElementById('M3CW').addEventListener('click', () => {
    rcim.II30402.packetSend([0xC1,0x20]); //M3 CW
});

document.getElementById('M4CCW').addEventListener('click', () => {
    rcim.II30402.packetSend([0xC1,0x40]); //M4 CCW
});
document.getElementById('M4CW').addEventListener('click', () => {
    rcim.II30402.packetSend([0xC1,0x80]); //M4 CW
});

//close
document.getElementById('close').addEventListener('click', () => {
    rcim.II30402.closeSocket();
});
```

Then run:

```bash
npm init -y
npm install npm install https://github.com/PeterTadich/controller-interface
```

Added the following code to the package.json file

```js
  "main": "mini-server.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1",
    "start": "node --experimental-modules mini-server.js"
  },
  "type": "module",
```

Full package.json file example

```js
{
  "name": "30402",
  "version": "1.0.0",
  "description": "30402 interface example",
  "main": "mini-server.js",
    "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1",
    "start": "node --experimental-modules mini-server.js"
  },
  "type": "module",
  "author": "Peter Tadich",
  "license": "MIT",
  "dependencies": {
    "controller-interface": "git+https://github.com/PeterTadich/controller-interface.git"
  }
}
```

Run 'websocket30402.py' (serial interface) then try:

```bash
npm start
```

Start your local server and goto port 8080.

## License

[MIT](LICENSE)