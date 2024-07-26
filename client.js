'use strict';
const common = require('./common.js');



const turl = 'wss://user225847803-yb3bi2ef.wormhole.vk-apps.com/'  // url, который дал вам туннель

common.create_tcp_server(3002, async server_tcp_socket => {
    await common.create_wss_client(turl, client_wss_socket => {
        let wss_closing = 0;
        const wss_closer = () => {
            console.log('closed tcp -> closing wss');
            client_wss_socket.disconnect();
        };
        let emit = null;
        emit = common.safe_emit(client_wss_socket, msg => {
            console.log('>>>', msg);
            server_tcp_socket.write(Buffer.from(msg, 'base64'));
        });
        client_wss_socket.on('disconnect', () => {
            console.log('closed wss -> closing tcp');
            server_tcp_socket.end();
            server_tcp_socket.destroy();
        });
        server_tcp_socket.on('close', () => {
            wss_closing -= 1;
            if (wss_closing < 0){
                wss_closer();
            }
        });
        server_tcp_socket.on('error', (data) => {
            console.log('closed tcp -> closing wss');
            client_wss_socket.disconnect();
        });
        server_tcp_socket.on('data', async msg => {
            console.log('<<<', msg.toString('base64'));
            try{
                wss_closing += 2;
                server_tcp_socket.pause();
                await emit(msg.toString('base64'));
            }finally{
                wss_closing -= 2;
                server_tcp_socket.resume();
                if (wss_closing < 0){
                    wss_closer();
                }
            }
        });
    });
});

