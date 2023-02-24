'use strict';
function ans(){
    document.querySelector("#column-center > div > div > div.chat-input > div.chat-input-container > div.rows-wrapper-wrapper > div > div.new-message-wrapper > button.btn-icon.tgico-none.toggle-emoticons").click()
    setTimeout(()=>{
        var q=document.querySelector("#content-emoji > div");
        (a=>a[Math.floor(Math.random()*a.length)])(q.children[7].children[1].children).click()
        document.querySelector("#column-center > div > div > div.chat-input > div.chat-input-container > div.btn-send-container > button").click()
    },128);
}


var last=new Set();

function get(){
    var q=new Set([...document.querySelector("#column-center > div > div > div.bubbles.has-groups.has-sticky-dates > div > div").getElementsByTagName('*')].filter(e=>e.classList.contains('bubble-content-wrapper')))
    var w=[];
    q.forEach(e=>last.has(e)?0:[w.push(e),last.add(e)]);
    return w;
}

var el=getEventListeners(document.querySelector("#column-center > div > div > div.chat-input > div > div.rows-wrapper-wrapper > div > div.new-message-wrapper > div.input-message-container > div:nth-child(1)"));

function type_text(t){
    document.querySelector("#column-center > div > div > div.chat-input > div > div.rows-wrapper-wrapper > div > div.new-message-wrapper > div.input-message-container > div:nth-child(1)").innerText=t;
    el.input.forEach(e=>e.listener());
}

function click_send(){
    document.querySelector("#column-center > div > div > div.chat-input > div > div.btn-send-container > button > div").click();
}

var last_reply_html='';
function _(){
    setInterval(()=>{
        var l=document.querySelector("#column-center > div > div > div.chat-input > div > div.rows-wrapper-wrapper > div > div.reply-wrapper > div.reply").innerHTML;
        if (l!=last_reply_html){
            type_text(l.slice(0,64));
            click_send();
        }
        last_reply_html=l;
    },256);
}

