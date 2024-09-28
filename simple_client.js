const TUNNEL_URL = 'https://user225847803-f3ep5hdc.wormhole.vk-apps.com/'  // url, который дал вам туннель
// const TUNNEL_URL = 'wss://127.0.0.1:3002/'  // url, который дал вам туннель
// const TUNNEL_URL = 'ws://127.0.0.1:3000/'  // url, который дал вам туннель

const io = require('socket.io-client')

const socket = io(TUNNEL_URL, {
    transports: ['websocket'],
    rejectUnauthorized: false,
    // extraHeaders: {
    //     Host: "https://user225847803-f3ep5hdc.wormhole.vk-apps.com/"
    // }
})

socket.on('connect', () => {
  console.log('Connected to server')
  setInterval(() => socket.emit('message', 'Hello from client'), 2000)
})

socket.on('message', (msg) => {
  console.log('Message from server:', msg)
})

socket.on('disconnect', () => {
  console.log('Disconnected from server')
})
