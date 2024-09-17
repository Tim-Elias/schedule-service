

$(document).ready(function() {
    // Загрузка всех расписаний
    loadAllSchedules();
    
    // Автоматическое обновление данных каждые 30 секунд
    setInterval(function() {
        loadAllSchedules();
        loadLogs();
        
    }, 30000);  // 30000 миллисекунд = 30 секунд

});

// Загрузка всех расписаний
// Загрузка всех расписаний
function loadAllSchedules() {
    console.log('Loading all schedules...');
    $.ajax({
        url: '/all_schedules_get',
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        data: { _: new Date().getTime() },
        success: function(response) {
            console.log('Response:', response);  // Выводим ответ в консоль
            let allScheduleList = $('#allScheduleList');
            allScheduleList.empty();

            // Проверяем, существует ли ключ `schedules` и является ли он массивом
            if (Array.isArray(response.schedules)) {
                // Сортируем расписания. Например, по ID, чтобы новые всегда шли внизу
                response.schedules.sort((a, b) => a.id - b.id);

                response.schedules.forEach(schedule => {
                    let actionButton = schedule.is_active 
                        ? `<button class="btn btn-warning" onclick="deactivateScheduleAll(${schedule.id})">Deactivate</button>`
                        : `<button class="btn btn-success" onclick="activateScheduleAll(${schedule.id})">Activate</button>`;

                    let viewLogsButton = !schedule.is_active
                        ? `<a href="/schedule_details?id=${schedule.id}" class="btn btn-info">View Logs</a>`
                        : '';

                    allScheduleList.append(`  <!-- Используем append, чтобы новые записи добавлялись в конец -->
                        <tr>
                            <td>${schedule.id}</td>
                            <td>${schedule.method}</td>
                            <td>${schedule.url}</td>
                            <td>${schedule.interval}</td>
                            <td>${schedule.last_run || 'Never'}</td>
                            <td>${schedule.is_active ? 'Active' : 'Inactive'}</td>
                            <td>
                                ${actionButton}
                                ${viewLogsButton}
                            </td>
                        </tr>
                    `);
                });
            } else {
                console.error('Expected an array of schedules, but got:', response.schedules);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading all schedules:', status, error);
        }
    });
}



// Активация расписания
function activateScheduleAll(id) {
    $.ajax({
        url: `/schedule/${id}/activate`,
        type: 'PATCH',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        success: function() {
            loadAllSchedules();
        },
        error: function(xhr, status, error) {
            console.error('Error activating schedule:', status, error);
        }
    });
}

// Деактивация расписания
function deactivateScheduleAll(id) {
    $.ajax({
        url: `/schedule/${id}/deactivate`,
        type: 'PATCH',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        success: function() {
            loadAllSchedules(); // Обновление всех расписаний
        },
        error: function(xhr, status, error) {
            console.error('Error deactivating schedule:', status, error);
        }
    });
}

