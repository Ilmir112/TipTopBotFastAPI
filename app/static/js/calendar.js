let previousSelectedDates = [];

console.log("calendar.js loaded.");

// Инициализация flatpickr
console.log("Initializing flatpickr...");
const datePicker = flatpickr("#datePicker", {
    mode: "multiple",
    dateFormat: "Y-m-d",
    locale: "ru",
    minDate: "today",
    onChange: function (selectedDates, dateStr, instance) {
        console.log("Обновленный список выбранных дат:");
        selectedDates.forEach(async (date) => {
            console.log(await formatDateToYYYYMMDD(date));
        });
        updateSelectedDatesList(selectedDates);
    }
});
console.log("flatpickr initialized.");

function markDayAsActive(dateStr) {
    // Находим элемент по дате
    const dayElement = document.querySelector(`[data-date='${dateStr}']`);
    if (dayElement) {
        // Удаляем класс 'inactive', чтобы сделать день активным
        dayElement.classList.remove('inactive');
        // Или, если вы скрывали элемент, можно его показать
        // dayElement.style.display = '';
    }
}

function formatDateToYYYYMMDD(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function updateSelectedDatesList(selectedDates) {
    // Преобразуем выбранные даты в строки
    const selectedDateStrings = selectedDates.map(d => formatDateToYYYYMMDD(d));

    // Убедимся, что previousSelectedDates — тоже массив строк
    // Если он содержит объекты Date, преобразуем их
    const previousDateStrings = previousSelectedDates.map(d => {
        if (d instanceof Date) {
            return d.toISOString().split('T')[0];
        } else {
            return d; // уже строка
        }
    });

    // Находим добавленные даты
    const addedDates = selectedDateStrings.filter(date => !previousDateStrings.includes(date));

    // Находим удалённые даты
    const removedDates = previousDateStrings.filter(date => !selectedDateStrings.includes(date));


    // Обрабатываем добавленные даты последовательно
    (async () => {
        for (const dateStr of addedDates) {
            await sendAddRequest(dateStr);
        }
        // Обрабатываем удалённые даты последовательно
        for (const dateStr of removedDates) {
            await sendRemoveRequest(dateStr);
        }
        // После завершения всех операций обновляем previousSelectedDates
        previousSelectedDates = selectedDateStrings;
    })();
}

// Функции для отправки запросов
async function sendAddRequest(dateStr) {
    try {
        // Передача в формате 'YYYY-MM-DD'
        const response = await fetch('/day/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({working_day: dateStr})
        });
        if (!response.ok) {
            console.error(`Ошибка при добавлении ${dateStr}:`, response.statusText);
        } else {
            console.log(`Рабочий день ${dateStr} успешно добавлен`);
        }
    } catch (error) {
        console.error(`Ошибка сети при добавлении ${dateStr}:`, error);
    }
}

async function sendRemoveRequest(dateStr) {
    try {
        const response = await fetch('/day/remove?working_day=' + encodeURIComponent(dateStr), {
            method: 'DELETE'
        });
        if (!response.ok) {
            const errorData = await response.json();
            if (response.status === 409 && errorData.detail) {
                alert(errorData.detail); // Показываем сообщение
                console.log(`Удаление ${dateStr} невозможно: ${errorData.detail}`);
                markDayAsActive(dateStr)

            } else {
                alert(`Ошибка: ${response.statusText}`);
            }
            throw new Error(`Ошибка при удалении: ${response.status} ${response.statusText}`);
        } else {
            console.log(`Рабочий день ${dateStr} успешно удален`);

        }
    } catch (error) {
        console.error(`Ошибка сети или другая ошибка:`, error);
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
            updateSelectedDatesList(data.map(d => new Date(d)));
        }
    } catch (error) {
        console.error("Ошибка загрузки данных:", error);
    }
}

// Теперь убрана функция addWorkingDays и обработчик кнопки

// Загружаем существующие дни при старте приложения
console.log("Loading existing days...");
loadExistingDays();
console.log("loadExistingDays() called.");

// Если нужно, можно добавить автоматическую синхронизацию или другие триггеры
