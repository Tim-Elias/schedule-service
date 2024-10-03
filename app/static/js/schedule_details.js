$(document).ready(function() {
    const token = localStorage.getItem('jwt_token');
    const urlParams = new URLSearchParams(window.location.search);
    const scheduleId = urlParams.get('id');

    if (!token) {
        window.location.href = '/';
    } else if (scheduleId) {
        // Загружаем детали расписания и логи только один раз
        loadScheduleDetails(scheduleId);
        loadLogs(scheduleId);
    } else {
        console.error('No schedule ID found in the URL.');
    }
});


// Загрузка деталей расписания
function loadScheduleDetails(id) {
    console.log(`Loading details for schedule ${id}...`);
    $.ajax({
        url: `/schedule_details?id=${id}`,  // Передаем ID через параметры URL
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        success: function(response) {
            console.log('Schedule details loaded:', response);
            $('#scheduleId').text(response.schedule.id);
            $('#scheduleMethod').text(response.schedule.method);
            $('#scheduleUrl').text(response.schedule.url);

            if (response.schedule.schedule_type === 'interval') {
                $('#scheduleInterval').text(response.schedule.interval + ' minutes');
                $('#scheduleDailyTime').hide();
            } else if (response.schedule.schedule_type === 'daily') {
                $('#scheduleInterval').hide();
                $('#scheduleDailyTime').text(response.schedule.time_of_day);
            }

            $('#scheduleLastRun').text(response.schedule.last_run || 'Never');
            $('#scheduleStatus').text(response.schedule.is_active ? 'Active' : 'Inactive');
        },
        error: function(xhr, status, error) {
            console.error('Error loading schedule details:', status, error);
        }
    });
}

// Загрузка логов по scheduleId с поддержкой пагинации
function loadLogs(scheduleId, page = 1, perPage = 10) {
    $.ajax({
        url: `/logs/${scheduleId}`,
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        data: { 
            page: page, 
            per_page: perPage 
        },
        success: function(response) {
            let logList = $('#logList');
            logList.empty();
            if (Array.isArray(response.logs)) {
                response.logs.forEach(log => {
                    logList.append(`
                        <tr>
                            <td>${log.schedule_id}</td>
                            <td>${log.response}</td>
                            <td>${log.timestamp}</td>
                        </tr>
                    `);
                });

                // Обновляем навигацию по страницам с учетом scheduleId
                updatePagination(response.page, response.per_page, response.total_logs, scheduleId);
            } else {
                console.error('Expected an array of logs, but got:', response.logs);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading logs:', status, error);
        }
    });
}



// Функция обновления навигации по страницам
function updatePagination(currentPage, perPage, totalLogs, scheduleId) {
    let totalPages = Math.ceil(totalLogs / perPage);
    let paginationContainer = $('#pagination');
    paginationContainer.empty();

    for (let page = 1; page <= totalPages; page++) {
        paginationContainer.append(`
            <button onclick="loadLogs(${scheduleId}, ${page}, ${perPage})">${page}</button>
        `);
    }
}


