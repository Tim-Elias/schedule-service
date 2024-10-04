$(document).ready(function () {
  // Проверка наличия токена в localStorage
  const token = localStorage.getItem("jwt_token");

  if (!token) {
    window.location.href = "/";
  } else {
    $.ajax({
      url: "/active_schedules",
      type: "GET",
      headers: {
        Authorization: "Bearer " + token,
      },
      success: function (response) {
        loadSchedulesActive();
        loadLogsActive();
      },
      error: function (xhr, status, error) {
        window.location.href = "/";
      },
    });
  }

  // Показать поле POST данных, если выбран POST метод
  $("#method").on("change", function () {
    if ($(this).val() === "POST") {
      $("#postDataDiv").show();
    } else {
      $("#postDataDiv").hide();
    }
  });

  // Переключение между типами расписаний (interval/daily)
  $("#schedule_type").on("change", function () {
    if ($(this).val() === "interval") {
      $("#intervalDiv").show();
      $("#timeOfDayDiv").hide();
      $("#interval").prop("required", true);
      $("#time_of_day").prop("required", false);
    } else if ($(this).val() === "daily") {
      $("#intervalDiv").hide();
      $("#timeOfDayDiv").show();
      $("#interval").prop("required", false);
      $("#time_of_day").prop("required", true);
    }
  });

  // Обработка отправки формы
  $("#scheduleForm").on("submit", function (event) {
    event.preventDefault();
    let method = $("#method").val();
    let url = $("#url").val();
    let scheduleType = $("#schedule_type").val();
    let interval = scheduleType === "interval" ? $("#interval").val() : null;
    let timeOfDay = scheduleType === "daily" ? $("#time_of_day").val() : null;
    let data = $("#data").val();
    $.ajax({
      url: "/schedule",
      type: "POST",
      contentType: "application/json",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("jwt_token"),
      },
      data: JSON.stringify({
        method: method,
        url: url,
        schedule_type: scheduleType,
        interval: interval,
        time_of_day: timeOfDay,
        data: method === "POST" ? data : null,
      }),
      success: function () {
        loadSchedulesActive();
        loadLogsActive();
        $("#scheduleForm")[0].reset();
        $("#postDataDiv").hide();
        $("#intervalDiv").show();
        $("#timeOfDayDiv").hide();
      },
      error: function (xhr, status, error) {
        console.error("Error adding schedule:", status, error);
      },
    });
  });

  // Автоматическое обновление данных каждые 30 секунд
  setInterval(function () {
    // loadSchedulesActive();
    loadLogsActive();
  }, 30000); // 30000 миллисекунд = 30 секунд

  // Обработчик для кнопки выхода
  $("#logoutButton").on("click", function () {
    // Удаляем токен из localStorage
    localStorage.removeItem("jwt_token");

    // Можно очистить токен из сессии на сервере, если требуется (дополнительно)

    // Перенаправляем пользователя на страницу входа
    window.location.href = "/login";
  });
});

// Загрузка активных расписаний
function loadSchedulesActive() {
  $.ajax({
    url: "/schedules",
    type: "GET",
    headers: {
      Authorization: "Bearer " + localStorage.getItem("jwt_token"),
    },
    data: { _: new Date().getTime() },
    success: function (response) {
      let scheduleList = $("#scheduleList");
      scheduleList.empty();

      let scheduleListCards = $("#scheduleListCards");
      scheduleListCards.empty();

      response.schedules.forEach((schedule) => {
        let scheduleType =
          schedule.schedule_type === "interval"
            ? `Interval (${schedule.interval} min)`
            : `Daily at ${schedule.time_of_day}`;

        let lastRun = schedule.last_run
          ? new Date(schedule.last_run).toLocaleString()
          : "Never";

        // Добавление строки в таблицу
        scheduleList.append(`
            <tr>
                <td>${schedule.id}</td>
                <td>${schedule.method}</td>
                <td>${schedule.url}</td>
                <td>${scheduleType}</td>
                <td>${lastRun}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deactivateScheduleActive(${schedule.id})">Deactivate</button>
                </td>
            </tr>
        `);

        // Добавление карточки
        scheduleListCards.append(`
            <div class="card schedule-card">
                <div class="card-body">
                    <h5 class="card-title">Schedule ID: ${schedule.id}</h5>
                    <p class="card-text"><strong>Method:</strong> ${schedule.method}</p>
                    <p class="card-text"><strong>URL:</strong> ${schedule.url}</p>
                    <p class="card-text"><strong>Schedule Type:</strong> ${scheduleType}</p>
                    <p class="card-text"><strong>Last Run:</strong> ${lastRun}</p>
                    <button class="btn btn-danger btn-sm" onclick="deactivateScheduleActive(${schedule.id})">Deactivate</button>
                </div>
            </div>
        `);
      });
    },
    error: function (xhr, status, error) {
      console.error("Error loading schedules:", status, error);
    },
  });
}

// Загрузка активных логов с поддержкой пагинации
function loadLogsActive(page = 1, perPage = 10) {
  $.ajax({
    url: "/logs/active",
    type: "GET",
    headers: {
      Authorization: "Bearer " + localStorage.getItem("jwt_token"),
    },
    data: {
      page: page,
      per_page: perPage,
      _: new Date().getTime(), // Для предотвращения кэширования
    },
    success: function (response) {
      let logList = $("#logList");
      logList.empty();
      response.logs.forEach((log) => {
        logList.prepend(`
                    <tr>
                        <td>${log.schedule_id}</td>
                        <td>${log.response}</td>
                        <td>${log.timestamp}</td>
                    </tr>
                `);
      });

      // Обновляем навигацию по страницам
      updatePagination(response.page, response.per_page, response.total_logs);
    },
    error: function (xhr, status, error) {
      console.error("Error loading logs:", status, error);
    },
  });
}

// Деактивация расписания
function deactivateScheduleActive(id) {
  $.ajax({
    url: `/schedule/${id}/deactivate`,
    type: "PATCH",
    headers: {
      Authorization: "Bearer " + localStorage.getItem("jwt_token"),
    },
    success: function () {
      loadSchedulesActive();
      loadLogsActive();
    },
    error: function (xhr, status, error) {
      console.error("Error deactivating schedule:", status, error);
    },
  });
}

// Функция обновления навигации по страницам
function updatePagination(currentPage, perPage, totalLogs) {
  let totalPages = Math.ceil(totalLogs / perPage);
  let paginationContainer = $("#pagination");
  paginationContainer.empty();

  for (let page = 1; page <= totalPages; page++) {
    paginationContainer.append(`
            <button onclick="loadLogsActive(${page}, ${perPage})">${page}</button>
        `);
  }
}
