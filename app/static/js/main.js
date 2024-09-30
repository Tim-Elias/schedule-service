console.log("JavaScript is working");

$(document).ready(function() {
    // Обработчик для формы входа
    $('#loginForm').on('submit', function(event) {
        event.preventDefault();

        let username = $('#username').val();
        let password = $('#password').val();

        $.ajax({
            url: '/auth',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            success: function(response) {
                localStorage.setItem('jwt_token', response.access_token);  // Сохраняем токен в localStorage
                $('#loginAlert').html('<div class="alert alert-success">Login successful!</div>');
                window.location.href = '/active_schedules';  // Перенаправляем на активные расписания
            },
            error: function() {
                $('#loginAlert').html('<div class="alert alert-danger">Invalid username or password.</div>');
            }
        });
    });
    
    // Обработчик для кнопки "Войти через Google"
    $('#googleLogin').on('click', function() {
        // Редиректим пользователя на страницу авторизации Google
        window.location.href = '/auth/google';
    });

/*
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        // Отправляем ID токен на сервер для получения JWT
        $.ajax({
            url: '/auth/google',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ id_token: token }),
            success: function(response) {
                localStorage.setItem('jwt_token', response.access_token);  // Сохраняем JWT токен
                window.location.href = '/active_schedules';  // Перенаправляем на активные расписания
            },
            error: function() {
                $('#loginAlert').html('<div class="alert alert-danger">Google authentication failed.</div>');
            }
        });
    }
    */


    /*
    // Обработчик для проверки, возвращаем ли мы из Google
    if (window.location.pathname === '/auth/callback') {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('code')) {
            const code = urlParams.get('code');
    
            // Отправляем запрос на сервер
            fetch('/auth/callback?code=' + encodeURIComponent(code), {
                method: 'GET',
            })
            .then(response => {
                if (response.ok) {
                    return response.json();  // Получаем токен из ответа
                }
                throw new Error('Failed to get token');
            })
            .then(data => {
                if (data.access_token) {
                    localStorage.setItem('jwt_token', data.access_token);  // Сохраняем токен в локальном хранилище
                    window.location.href = '/active_schedules';  // Перенаправляем на активные расписания
                } else {
                    console.error('Access token not received:', data);
                    document.getElementById('loginAlert').innerHTML = '<div class="alert alert-danger">Failed to receive access token.</div>';
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                document.getElementById('loginAlert').innerHTML = '<div class="alert alert-danger">Google login failed.</div>';
            });
        }
    }
    */
    /*
    // Обработка перенаправления после аутентификации через Google
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        // Отправляем ID токен на сервер для получения JWT
        $.ajax({
            url: '/auth/google',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ id_token: token }),
            success: function(response) {
                localStorage.setItem('jwt_token', response.access_token);  // Сохраняем JWT токен
                window.location.href = '/active_schedules';  // Перенаправляем на активные расписания
            },
            error: function() {
                $('#loginAlert').html('<div class="alert alert-danger">Google authentication failed.</div>');
            }
        });
    }
        */
});


/*
document.addEventListener('DOMContentLoaded', (event) => {
    // Обработчик для кнопки Google авторизации
    document.getElementById('googleLogin').addEventListener('click', function() {
        window.location.href = '/auth/google';
    });

    // Проверяем, если мы возвращаемся из Google
    if (window.location.pathname === '/auth/callback') {
        console.log('Callback URL detected');
        
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('code')) {
            const code = urlParams.get('code');
            console.log("Code received:", code);

            fetch('/auth/callback?code=' + encodeURIComponent(code), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
            })
            .then(response => {
                console.log("Response status:", response.status);
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Failed to get token');
            })
            .then(data => {
                console.log("Data received:", data);
                if (data.access_token) {
                    localStorage.setItem('jwt_token', data.access_token);
                    setTimeout(() => {
                        window.location.href = '/active_schedules';
                    }, 1000);
                } else {
                    console.error('Access token not received:', data);
                    document.getElementById('loginAlert').innerHTML = '<div class="alert alert-danger">Failed to receive access token.</div>';
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                document.getElementById('loginAlert').innerHTML = '<div class="alert alert-danger">Google login failed.</div>';
            });
        } else {
            console.error('No code found in URL');
            document.getElementById('loginAlert').innerHTML = '<div class="alert alert-danger">Authentication failed.</div>';
        }
    }
});
*/