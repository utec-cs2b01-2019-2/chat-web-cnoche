function sendMessage(){
    alert("Heyyyy");
}

function get_current(){
    console.log("Voy a traer el usuario logueado");
    $.getJSON("/current", function(data){
        console.log("Current user is "+data['username'])
        get_all_users(data['id']);
    });
}

function getMessages(user_from_id, user_to_id){
    alert("Voy a traer los mensajes entre "+ user_from_id +" y "+ user_to_id);
}

function get_all_users(user_from_id){
    console.log("Voy a traer todos los usuarios");

    $.getJSON("/users", function(data){
    var i =0;
    $.each(data, function(){
        user_to = data[i]['id'];
        e = '<div class="alert" role="alert" onclick="getMessages('+user_from_id+','+data[i]['id'] +')" >';
        e = e+'<div>'+data[i]['username']+'</div>';
        e = e+'</div>';
        i = i+1;
        $("<div/>",{html:e}).appendTo("#users");
        });
    });
}