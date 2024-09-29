'use strict';

function create_wss_server(port, on_connect){
    const http = require('http');
    const express = require('express');
    const { Server } = require('socket.io');

    const app = express();
    const server = http.createServer(app);
    const io = new Server(server);

    app.get('/', async (_, res) => {
        console.log("FUNNY")
        res.send("HELLO FROM SERVER - HTTP");
    });

    io.on('connection', async (server_socket) => {
        console.log('a user connected');

        await on_connect(server_socket);

        // server_socket.on('disconnect', () => {
        //     console.log('user disconnected');
        // });

        on_connect(server_socket);
    });

    server.listen(port, () => {
        console.log('listening on localhost:' + port);
    });
}

function create_wss_client(url, on_connect){

    const io = require('socket.io-client')

    const client_socket = io(url)

    let p = new Promise(r=>{
        client_socket.on('connect', async () => {
            console.log('Connected to server')
            await on_connect(client_socket);

            // client_socket.on('disconnect', () => {
            //     console.log('Disconnected from server')
            // })
            r(client_socket);
        })
    });
    return p;
}

function create_tcp_server(port, on_connect){
    var net = require('net');

    var HOST = '0.0.0.0';
    var PORT = port;

    net.createServer(async (server_socket) => {
        console.log('CONNECTED: ' + server_socket.remoteAddress +':'+ server_socket.remotePort);
        await on_connect(server_socket);

        // server_socket.on('close', (data) => {
        //     console.log('CLOSED: ' + server_socket.remoteAddress +' '+ server_socket.remotePort);
        // });

    }).listen(PORT, HOST);

    console.log('Server listening on ' + HOST +':'+ PORT);

}


function create_tcp_client(port, on_error, on_connect){
    const net = require('net');
    var client_socket = new net.Socket();

    let p = new Promise(r=>{
        client_socket.on('close', on_error);
        client_socket.on('error', on_error);
    
        client_socket.connect(port, '127.0.0.1', async () => {
            
            console.log('Connected');
            await on_connect(client_socket);

            r(client_socket);
        });
    });

    return p;
}

let known_events = {0:0};

function safe_emit(socket, on_message){
    socket.on('message', (message, f) => {
        if (!(message.id in known_events)){
            known_events[message.id] = 0;
            on_message(message.message);
        }
        f(0);
    })
    return message => {
        return new Promise(r=>{
            let data = {
                id: Math.random(),
                message: message,
            }
            let emit = () => {
                socket.timeout(4000).emit('message', data, err => {
                    if (err) {
                        emit();
                    }else{
                        r(0);
                    }
                })
            };
            emit();
        });
    };
}

function unsafe_emit(socket, on_message){
    socket.on('message', (message, f) => {
        on_message(message);
        // if (!(message.id in known_events)){
        //     known_events[message.id] = 0;
        //     on_message(message.message);
        // }
        // f(0);
    })
    return message => {
        return socket.emit('message', message);
        // return new Promise(r=>{
        //     let data = {
        //         id: Math.random(),
        //         message: message,
        //     }
        //     let emit = () => {
        //         socket.timeout(4000).emit('message', data, err => {
        //             if (err) {
        //                 emit();
        //             }else{
        //                 r(0);
        //             }
        //         })
        //     };
        //     emit();
        // });
    };
}




if (typeof module !== 'undefined'){
    module.exports = {
        create_wss_client: create_wss_client,
        create_wss_server: create_wss_server,
        create_tcp_server: create_tcp_server,
        create_tcp_client: create_tcp_client,
        safe_emit: safe_emit,
        unsafe_emit: unsafe_emit,
    }

}


