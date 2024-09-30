$(document).ready(function() {
    // Проверка наличия токена в localStorage
    const token = localStorage.getItem('jwt_token');

    if (!token) {
        window.location.href = '/';
    } else {
        $.ajax({
            url: '/all_schedules',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                loadAllSchedules();
            },
            error: function(xhr, status, error) {
                window.location.href = '/';
            }
        });
    }
    // Загрузка всех расписаний
    //loadAllSchedules();

    // Автоматическое обновление данных каждые 30 секунд
    setInterval(function() {
        loadAllSchedules();
    }, 30000);

    // Скрыть форму редактирования
    function hideEditForm() {
        $('#scheduleEditFormContainer').hide();
        $('#scheduleEditForm')[0].reset();
    }

    // Обработчик отправки формы редактирования
    $('#scheduleEditForm').on('submit', function(event) {
        event.preventDefault();

        let id = $('#editScheduleId').val();
        let method = $('#editMethod').val();
        let url = $('#editUrl').val();
        let scheduleType = $('#editScheduleType').val();
        let interval = scheduleType === 'interval' ? $('#editInterval').val() : null;
        let dailyTime = scheduleType === 'daily' ? $('#editDailyTime').val() : null;
        let data = method === 'POST' ? $('#editData').val() : null;

        $.ajax({
            url: `/schedule/${id}`,
            type: 'PUT',
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
            },
            data: JSON.stringify({
                method: method,
                url: url,
                schedule_type: scheduleType,
                interval: interval,
                time_of_day: dailyTime,
                data: data
            }),
            success: function() {
                loadAllSchedules(); // Обновление списка расписаний
                hideEditForm();     // Скрыть форму редактирования
            },
            error: function(xhr, status, error) {
                console.error('Error updating schedule:', status, error);
            }
        });
    });

    // Показать форму редактирования с данными расписания
    window.editSchedule = function(scheduleId, method, url, scheduleType, interval, dailyTime, data) {
        $('#scheduleEditFormContainer').show();
        $('#editScheduleId').val(scheduleId);
        $('#editMethod').val(method);
        $('#editUrl').val(url);
        $('#editScheduleType').val(scheduleType);
        
        // Показать/скрыть поля в зависимости от типа расписания
        if (scheduleType === 'interval') {
            $('#editIntervalDiv').show();
            $('#editInterval').val(interval || '');
            $('#editDailyTimeDiv').hide();
        } else if (scheduleType === 'daily') {
            $('#editDailyTimeDiv').show();
            $('#editDailyTime').val(dailyTime || '');
            $('#editIntervalDiv').hide();
        }

        // Показать поле для POST данных, если метод POST
        if (method === 'POST') {
            $('#editPostDataDiv').show();
            $('#editData').val(data || '');
        } else {
            $('#editPostDataDiv').hide();
        }
    };
});

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
            console.log('Response:', response);
            let allScheduleList = $('#allScheduleList');
            allScheduleList.empty();

            if (Array.isArray(response.schedules)) {
                response.schedules.sort((a, b) => a.id - b.id);
                response.schedules.forEach(schedule => {
                    let actionButton = schedule.is_active 
                        ? `<button class="btn btn-warning" onclick="deactivateScheduleAll(${schedule.id})">Deactivate</button>`
                        : `<button class="btn btn-success" onclick="activateScheduleAll(${schedule.id})">Activate</button>`;

                    let viewLogsButton = !schedule.is_active
                        ? `<a href="/schedule_details?id=${schedule.id}" class="btn btn-info">View Logs</a>`
                        : '';

                    let editButton = `<button class="btn btn-primary" onclick="editSchedule(${schedule.id}, '${schedule.method}', '${schedule.url}', '${schedule.schedule_type}', ${schedule.interval || null}, '${schedule.daily_time || ''}', '${schedule.data || ''}')">Edit</button>`;

                    allScheduleList.append(`
                        <tr>
                            <td>${schedule.id}</td>
                            <td>${schedule.method}</td>
                            <td>${schedule.url}</td>
                            <td>${schedule.schedule_type === 'interval' ? schedule.interval + ' min' : schedule.time_of_day}</td>
                            <td>${schedule.last_run || 'Never'}</td>
                            <td>${schedule.is_active ? 'Active' : 'Inactive'}</td>
                            <td>
                                ${actionButton}
                                ${viewLogsButton}
                                ${editButton}
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
            loadAllSchedules();
        },
        error: function(xhr, status, error) {
            console.error('Error deactivating schedule:', status, error);
        }
    });
}
