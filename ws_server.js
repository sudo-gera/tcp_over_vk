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
  // console.log('a user connected');

  // socket.on('message', (msg) => {
  //   console.log('message: ' + msg);
  //   socket.emit('message', "HELLO FROM SERVER - WS");
  // });

  // socket.on('disconnect', () => {
  //   console.log('user disconnected');
  // });

  var net = require('net');

  var client = new net.Socket();
  client.connect(1337, '127.0.0.1', function() {
    // console.log('Connected');
    // client.write('Hello, server! Love, Client.');
    client.pipe(socket);
  });

  // client.on('data', function(data) {
  //   console.log('Received: ' + data);
  //   client.destroy(); // kill client after server's response
  // });

  // client.on('close', function() {
  //   console.log('Connection closed');
  // });

});

server.listen(3000, () => {
  console.log('listening on localhost:3000');
});
