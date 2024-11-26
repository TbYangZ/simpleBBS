document.addEventListener('DOMContentLoaded', function() {
    // 获取按钮和表单
    const createServer = document.getElementById('createServer');
    const formCreateServer = document.getElementById('formCreateServer');
    const cancelCreate = document.getElementById('cancelCreate');


    const joinServer = document.getElementById('joinServer');
    const formJoinServer = document.getElementById('formJoinServer');
    const cancelJoin = document.getElementById('cancelJoin');

    joinServer.addEventListener('click', function() {
        formCreateServer.style.display = 'none';
        formJoinServer.style.display = 'block';
    });

    cancelJoin.addEventListener('click', function() {
        formJoinServer.style.display = 'none';
    });


    // 点击按钮显示表单
    createServer.addEventListener('click', function() {
        formJoinServer.style.display = 'none'; // 隐藏表单
        formCreateServer.style.display = 'block'; // 显示表单
    });

    // 点击关闭按钮隐藏表单
    cancelCreate.addEventListener('click', function() {
        formCreateServer.style.display = 'none'; // 隐藏表单
    });

    const server_list = document.getElementById('server_list');
});
