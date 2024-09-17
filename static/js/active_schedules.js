$(document).ready(function() {
    // Проверка наличия токена в localStorage
    const token = localStorage.getItem('jwt_token');

    // Если токен отсутствует, перенаправляем на страницу логина
    if (!token) {
        window.location.href = '/';
    } else {
        // Если токен есть, вы можете дополнительно проверить его действительность
        $.ajax({
            url: '/active_schedules',  // Необходимо добавить этот маршрут на сервере
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                loadSchedulesActive();
                loadLogsActive();
                // Токен действителен, страница загружается
                // Дополнительный код для загрузки защищенной информации, если необходимо
            },
            error: function(xhr, status, error) {
                // Если токен недействителен, перенаправляем на страницу логина
                window.location.href = '/';
            }
        });
    }

    // Показать поле POST данных, если выбран POST метод
    $('#method').on('change', function() {
        if ($(this).val() === 'POST') {
            $('#postDataDiv').show();
        } else {
            $('#postDataDiv').hide();
        }
    });

    //loadSchedulesActive();
    //loadLogsActive();

    // Автоматическое обновление данных каждые 30 секунд
    setInterval(function() {
        loadSchedulesActive();
        loadLogsActive();
        
    }, 30000);  // 30000 миллисекунд = 30 секунд

    // Добавление нового расписания
    $('#scheduleForm').on('submit', function(event) {
        event.preventDefault();
    
        let method = $('#method').val();
        let url = $('#url').val();
        let interval = $('#interval').val();
        let data = $('#data').val();
    
        $.ajax({
            url: '/schedule',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
            },
            data: JSON.stringify({
                method: method,
                url: url,
                interval: interval,
                data: method === 'POST' ? data : null
            }),
            success: function() {
                loadSchedulesActive(); // Обновление активных расписаний
                loadLogsActive(); //Обновление активных логов
                $('#scheduleForm')[0].reset();
                $('#postDataDiv').hide();
            },
            error: function(xhr, status, error) {
                console.error('Error adding schedule:', status, error);
            }
        });
    });
    

    // Загрузка логов активных расписаний при нажатии кнопки
    $('#loadActiveLogs').on('click', function() {
        loadLogs();
    });
});


// Загрузка расписаний
function loadSchedulesActive() {
    console.log('Loading schedules...');
    $.ajax({
        url: '/schedules',
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        data: { _: new Date().getTime() },
        success: function(response) {
            console.log('Schedules loaded:', response);
            let scheduleList = $('#scheduleList');
            scheduleList.empty();
            response.schedules.forEach(schedule => {
                scheduleList.prepend(`
                    <tr>
                        <td>${schedule.id}</td>
                        <td>${schedule.method}</td>
                        <td>${schedule.url}</td>
                        <td>${schedule.interval}</td>
                        <td>${schedule.last_run || 'Never'}</td>
                        <td><button class="btn btn-danger" onclick="deactivateScheduleActive(${schedule.id})">Deactivate</button></td>
                    </tr>
                `);
            });
        },
        error: function(xhr, status, error) {
            console.error('Error loading schedules:', status, error);
        }
    });
}

// Загрузка логов
function loadLogsActive(scheduleId = null) {
    console.log('Loading logs...');
    $.ajax({
        url: scheduleId ? `/logs/${scheduleId}` : '/logs/active',
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        data: { _: new Date().getTime() }, // Добавление параметра времени для предотвращения кэширования
        success: function(response) {
            console.log('Logs loaded:', response);
            let logList = $('#logList');
            logList.empty(); // Очищаем список перед добавлением новых данных
            response.logs.forEach(log => {
                logList.prepend(`
                    <tr>
                        <td>${log.schedule_id}</td>
                        <td>${log.response}</td>
                        <td>${log.timestamp}</td>
                    </tr>
                `);
            });
        },
        error: function(xhr, status, error) {
            console.error('Error loading logs:', status, error);
        }
    });
}


// Деактивация расписания
function deactivateScheduleActive(id) {
    $.ajax({
        url: `/schedule/${id}/deactivate`,
        type: 'PATCH',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        success: function() {
            loadSchedulesActive(); // Обновление активных расписаний
        },
        error: function(xhr, status, error) {
            console.error('Error deactivating schedule:', status, error);
        }
    });
}