const http = require('http');
const express = require('express');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.get('/', (_, res) => {
  console.log("FUNNY")
  res.send("HELLO FROM SERVER - HTTP");
});

io.on('connection', (socket) => {
  console.log('a user connected');

  socket.on('message', (msg) => {
    console.log('message: ' + msg);
    socket.emit('message', "HELLO FROM SERVER - WS");
  });

  let i = setInterval(() => {
    socket.emit('message', "____HELLO FROM SERVER - WS");
  }, 1500);

  socket.on('disconnect', () => {
    console.log('user disconnected');
    clearInterval(i);
  });
});

server.listen(3001, () => {
  console.log('listening on localhost:3001');
});