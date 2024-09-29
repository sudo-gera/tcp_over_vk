'use strict';
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
const common = require('./common.js');

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

async function load(){
	fetch(process.argv[2]).then(e=>{
		console.log(e);
		e.text().then(e=>{
			console.log(e);
		});
	});
}

//load();


//const turl = '________'     // u'//rl, который дал вам туннель

let turl = '';

common.create_tcp_server(3128, async server_tcp_socket => {
    try{
        turl = 'wss' + (await (await fetch(process.argv[2])).text());
    }catch(e){
        console.log(e);
    }
    await common.create_wss_client(turl, client_wss_socket => {
        let wss_closing = 0;
        const wss_closer = () => {
            console.log('closed tcp -> closing wss');
            client_wss_socket.disconnect();
        };
        let emit = null;
        emit = common.unsafe_emit(client_wss_socket, msg => {
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


