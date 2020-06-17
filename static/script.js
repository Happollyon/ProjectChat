
window.onload = function() {
  select(localStorage.getItem('channel_id'),localStorage.getItem('user'))
};

function sendimg()
{
    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);


    let url=localStorage.getItem('img')
    let channel_id=localStorage.getItem('channel_id');

    socket.emit('msg_giff', {'url':url,'channel_id':channel_id});
    document.getElementById('input').value=''

    var objDiv = document.getElementById("msgs");
    objDiv.scrollTop = objDiv.scrollHeight;
}
function send(event)
{
    if(event.key==='Enter')
    {
        // Connect to websocket
        var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

                // Each button should emit a "submit vote" event

                    let text=document.getElementById('input').value
                    if(text===null)
                    {
                        return
                    }
                    let url='';
                    let channel_id=localStorage.getItem('channel_id');

                    socket.emit('msg', {'text':text,'url':url,'channel_id':channel_id});
                    document.getElementById('input').value=''

                    var objDiv = document.getElementById("msgs");
        objDiv.scrollTop = objDiv.scrollHeight;

    }
}


function select(channel_id,user) {
    localStorage.setItem('channel_id',channel_id)
    localStorage.setItem('user',user)
    const myNode = document.getElementById("msgs");
    myNode.innerHTML = '';

    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var data = JSON.parse(this.responseText)
            console.log(data.giff.data.images.original.url)
            var mydiv= document.getElementById('gif')
            var newcontent = document.createElement('img')
            newcontent.setAttribute("src", data.giff.data.images.original.url);
            localStorage.setItem('img', data.giff.data.images.original.url)
            mydiv.appendChild(newcontent)

            data.msgs.map(data => {
                var mydiv= document.getElementById('msgs')
                var newcontent = document.createElement('div')
                if(user!==data.username)
                {
                    newcontent.setAttribute("id", "text");
                }else{
                    newcontent.setAttribute("id", "text_right");
                }
                if(data.url!=='')
                {
                    newcontent.innerHTML=newcontent.innerHTML= "<div id='username'>"+data.username+"</div><div id='msg_text'>"+data.text+'</div><img src='+data.url+'/><div>'+data.created_at+'</div>'

                }else {
                    newcontent.innerHTML=newcontent.innerHTML= "<div id='username'>"+data.username+"</div><div id='msg_text'>"+data.text+'</div><div>'+data.created_at+'</div>'

                }
                 mydiv.appendChild(newcontent) })
            var objDiv = document.getElementById("msgs");
            objDiv.scrollTop = objDiv.scrollHeight;
        }
    };

    xhttp.open("GET", "/selectmsgs/" + channel_id, true);
    xhttp.send();


    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {
        socket.on(channel_id, data => {

            var mydiv= document.getElementById('msgs')
            newcontent = document.createElement('div')

            if(user!==data.username)
            {
                newcontent.setAttribute("id", "text");

                if(data.url!=null)
            {
                newcontent.innerHTML=newcontent.innerHTML= "<div id='username'>"+data.username+"</div><div id='msg_text'>"+data.text+'</div><img src='+data.url+'/>'

            }else {
                newcontent.innerHTML=newcontent.innerHTML= "<div id='username'>"+data.username+"</div><div id='msg_text'>"+data.text+'</div>'

            }

                mydiv.appendChild(newcontent)

            }else {
                newcontent.setAttribute("id", "text_right");
                if(data.url!=null)
                {
                    newcontent.innerHTML=newcontent.innerHTML= "<div id='username'>"+data.username+"</div><div id='msg_text'>"+data.text+'</div><img src='+data.url+'/><div>'+data.created_at+'</div>'

                }else {
                    newcontent.innerHTML=newcontent.innerHTML= "<div id='username'>"+data.username+"</div><div id='msg_text'>"+data.text+'</div>'

                }
                mydiv.appendChild(newcontent)

            }

            var objDiv = document.getElementById("msgs");
            objDiv.scrollTop = objDiv.scrollHeight;
        });
    })
}

