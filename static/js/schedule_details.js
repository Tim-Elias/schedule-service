$(document).ready(function() {
    // Получение ID расписания из URL
    const urlParams = new URLSearchParams(window.location.search);
    const scheduleId = urlParams.get('id');

    if (scheduleId) {
        // Загрузка деталей расписания и логов
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
        url: `/schedule_details/${id}`,
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        success: function(response) {
            console.log('Schedule details loaded:', response);
            $('#scheduleId').text(response.schedule.id);
            $('#scheduleMethod').text(response.schedule.method);
            $('#scheduleUrl').text(response.schedule.url);
            $('#scheduleInterval').text(response.schedule.interval);
            $('#scheduleLastRun').text(response.schedule.last_run || 'Never');
            $('#scheduleStatus').text(response.schedule.is_active ? 'Active' : 'Inactive');
        },
        error: function(xhr, status, error) {
            console.error('Error loading schedule details:', status, error);
        }
    });
}

// Загрузка логов
function loadLogs(scheduleId) {
    console.log(`Loading logs for schedule ${scheduleId}...`);
    $.ajax({
        url: `/logs/${scheduleId}`,
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
        },
        success: function(response) {
            console.log('Logs loaded:', response);
            let logList = $('#logList');
            logList.empty();
            if (Array.isArray(response.logs)) {
                response.logs.forEach(log => {
                    logList.prepend(`
                        <tr>
                            <td>${log.response}</td>
                            <td>${log.timestamp}</td>
                        </tr>
                    `);
                });
            } else {
                console.error('Expected an array of logs, but got:', response.logs);
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading logs:', status, error);
        }
    });
}
