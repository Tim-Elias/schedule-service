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
                localStorage.setItem('jwt_token', response.access_token);
                $('#loginAlert').html('<div class="alert alert-success">Login successful!</div>');
                window.location.href = '/active_schedules';
                
            },
            error: function() {
                $('#loginAlert').html('<div class="alert alert-danger">Invalid username or password.</div>');
            }
        });
    });
    /*
     // Обработчик для формы регистрации
     $('#registerForm').on('submit', function(event) {
        event.preventDefault();

        let username = $('#username').val();
        let password = $('#password').val();

        $.ajax({
            url: '/register',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, password: password }),
            success: function(response) {
                $('#registerAlert').html('<div class="alert alert-success">Registration successful!</div>');
            },
            error: function() {
                $('#registerAlert').html('<div class="alert alert-danger">Error during registration.</div>');
            }
        });
    });
    */
    
});





