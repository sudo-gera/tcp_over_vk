'use strict';
const { client } = require('telegram');
const common = require('./common.js');





common.create_wss_server(3000, async server_wss_socket => {
    let wss_closing = 0;
    const wss_closer = () => {
        console.log('closed tcp -> closing wss');
        server_wss_socket.disconnect();
    };
    await common.create_tcp_client(3128, () => {
        wss_closing -= 1;
        if (wss_closing < 0){
            wss_closer();
        }
    }, client_tcp_socket => {
        let emit = null;
        client_tcp_socket.on('data', async msg => {
            console.log('>>>', msg.toString('base64'));
            try{
                wss_closing += 2;
                client_tcp_socket.pause();
                await emit(msg.toString('base64'));
            }finally{
                wss_closing -= 2;
                client_tcp_socket.resume();
                if (wss_closing < 0){
                    wss_closer();
                }
            }
        });
        server_wss_socket.on('disconnect', () => {
            console.log('closed wss -> closing tcp');
            client_tcp_socket.end();
            client_tcp_socket.destroy();
        });
        emit = common.unsafe_emit(server_wss_socket, msg => {
            console.log('<<<', msg);
            client_tcp_socket.write(Buffer.from(msg, 'base64'));
        });
    });
});
