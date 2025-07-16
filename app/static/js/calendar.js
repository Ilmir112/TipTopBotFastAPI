// Используйте только одну функцию formatDateToYYYYMMDD
async function formatDateToYYYYMMDD(date) {
    const dateObj = new Date(date);
    if (isNaN(dateObj.getTime())) {
        return null;
    }
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

let previousSelectedDates = [];

// Инициализация flatpickr
const datePicker = flatpickr("#datePicker", {
    mode: "multiple",
    dateFormat: "Y-m-d",
    locale: "ru",
    minDate: "today",
    onChange: function (selectedDates, dateStr, instance) {
        console.log("Обновленный список выбранных дат:");
        selectedDates.forEach(date => {
            console.log(formatDateToYYYYMMDD(date));
        });
        updateSelectedDatesList(selectedDates);
    }
});

// Функция для обновления списка выбранных дат
function updateSelectedDatesList(selectedDates) {
    // Преобразуем выбранные даты в строки для сравнения
    const selectedDateStrings = selectedDates;
    const previousDateStrings = previousSelectedDates;

    // Находим добавленные даты
    const addedDates = selectedDateStrings.filter(date => !previousDateStrings.includes(date));

    // Находим удалённые даты
    const removedDates = previousDateStrings.filter(date => !selectedDateStrings.includes(date));

    // Обрабатываем добавленные даты
    addedDates.forEach(async (dateStr) => {
        await sendAddRequest(dateStr);
    });

    // Обрабатываем удалённые даты
    removedDates.forEach(async (dateStr) => {
        await sendRemoveRequest(dateStr);
    });

    // Обновляем предыдущий список
    previousSelectedDates = selectedDateStrings;
}

// Функции для отправки запросов
async function sendAddRequest(dateStr) {
    try {
        const dateOnlyStr = new Date(dateStr).toISOString().split('T')[0]; // "2025-07-30"
        const response = await fetch('/day/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ working_day: dateOnlyStr })
        });
        if (!response.ok) {
            console.error(`Ошибка при добавлении ${dateOnlyStr}:`, response.statusText);
        } else {
            console.log(`Рабочий день ${dateOnlyStr} успешно добавлен`);
        }
    } catch (error) {
        console.error(`Ошибка сети при добавлении ${dateOnlyStr}:`, error);
    }
}

async function sendRemoveRequest(dateStr) {
    try {
        const response = await fetch('/day/remove?working_day=' + encodeURIComponent(dateStr), {
            method: 'DELETE'
        });
        if (!response.ok) {
            console.error(`Ошибка при удалении ${dateStr}:`, response.statusText);
        } else {
            console.log(`Рабочий день ${dateStr} успешно удален`);
        }
    } catch (error) {
        console.error(`Ошибка сети при удалении ${dateStr}:`, error);
    }
}

// Загружаем существующие дни из базы и отображаем их в календаре
async function loadExistingDays() {
    try {
        const response = await fetch("/day/find_all");
        const data = await response.json();
        if (Array.isArray(data)) {
            // Предполагается, что data — массив строк формата 'YYYY-MM-DD'
            datePicker.setDate(data, false); // без вызова onChange
            previousSelectedDates = data;
            // Обновляем список выбранных дат для синхронизации
            updateSelectedDatesList(data);
        }

    } catch (error) {
        console.error("Ошибка загрузки данных:", error);
    }
}

// Функция для добавления новых дат через кнопку или другой триггер
async function addWorkingDays(dates) {
    const payload = dates.map(d => ({ date: d }));
    try {
        const response = await fetch("/day/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        alert(result.message || "Даты успешно добавлены");

        // После добавления перезагружаем данные из базы чтобы синхронизировать состояние
        await loadExistingDays();

        // Очистка выбора после успешной операции (если нужно)
        datePicker.clear();

        // Обновляем список выбранных дат для синхронизации
        updateSelectedDatesList([]);

        alert("Даты успешно добавлены");

    } catch (error) {
        console.error("Ошибка при добавлении дат:", error);
    }
}

// Загружаем существующие дни при старте приложения
loadExistingDays();

// Обработчик кнопки для добавления новых дат (пример)
document.getElementById("submitDates").addEventListener("click", async () => {
    const selectedDatesArray = Array.from(datePicker.selectedDates).map(d => d.toISOString().split('T')[0]);

    if (selectedDatesArray.length > 0) {
        await addWorkingDays(selectedDatesArray);

        // После этого данные из базы уже загружены внутри addWorkingDays()

// Можно оставить очистку выбора или оставить как есть:
       // datePicker.clear();
       // updateSelectedDatesList([]);

// Или оставить так, чтобы пользователь мог выбрать новые даты после загрузки.

//     alert("Даты успешно добавлены");

} else {
      alert("Пожалуйста, выберите хотя бы одну дату.");
}
});