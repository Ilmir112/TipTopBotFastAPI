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

// Инициализация flatpickr
const datePicker = flatpickr("#datePicker", {
    mode: "multiple",
    dateFormat: "Y-m-d",
    locale: "ru",
    onChange: function (selectedDates) {
        updateSelectedDatesList(selectedDates);
    }
});

async function updateSelectedDatesList(selectedDates) {
    const list = document.getElementById("selectedDatesList");
    list.innerHTML = "";

    const dateStrings = await Promise.all(selectedDates.map(async d => {
        if (typeof d === 'string') return d;
        if (d instanceof Date) {
            return await formatDateToYYYYMMDD(d);
        }
        return '';
    }));
    // фильтр для исключения пустых строк
    const filteredDates = dateStrings.filter(s => s);

    // сортировка
    filteredDates.sort();

    filteredDates.forEach(dateStr => {
        const li = document.createElement("li");
        li.className = "date-item";
        li.textContent = dateStr;

        // Обработчик клика для удаления
        li.onclick = async () => {
            await deleteWorkingDay(dateStr);
            const remainingDates = datePicker.selectedDates.filter(d => formatDateToYYYYMMDD(d) !== dateStr);
            datePicker.setDate(remainingDates, true);
            updateSelectedDatesList(remainingDates);
        };

        // Кнопка удаления
        const removeBtn = document.createElement("span");
        removeBtn.textContent = " ×";
        removeBtn.className = "remove-date";
        removeBtn.onclick = async (e) => {
            e.stopPropagation();
            await deleteWorkingDay(dateStr);
            const remainingDates = datePicker.selectedDates.filter(d => formatDateToYYYYMMDD(d) !== dateStr);
            datePicker.setDate(remainingDates, true);
            updateSelectedDatesList(remainingDates);
        };

        li.appendChild(removeBtn);
        list.appendChild(li);
    });
}

async function deleteWorkingDay(date) {
    // Проверка формата
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
        // Попытка преобразовать
        const newDate = await formatDateToYYYYMMDD(new Date(date));
        if (!newDate) {
            console.error("Некорректная дата:", date);
            return;
        }
        date = newDate;
    }

    try {
        await fetch(`/day/remove?working_day=${date}`, {
            method: "DELETE"
        });
    } catch (error) {
        console.error("Ошибка при удалении дня:", error);
    }
}

async function loadExistingDays() {
    try {
        const response = await fetch("/day/find_all");
        const data = await response.json();
        if (Array.isArray(data)) {
            const dates = data; // предполагается формат 'YYYY-MM-DD'
            datePicker.setDate(dates, false); // без вызова onChange
            updateSelectedDatesList(dates);
        }
    } catch (error) {
        console.error("Ошибка загрузки данных:", error);
    }
}

async function addWorkingDays(dates) {
    const payload = dates.map(d => ({date: d}));
    try {
        const response = await fetch("/day/add", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        alert(result.message || "Даты успешно добавлены");
    } catch (error) {
        console.error("Ошибка при добавлении дат:", error);
    }
}

document.getElementById("submitDates").addEventListener("click", async () => {
    const selectedDates = Array.from(datePicker.selectedDates).map(d => d.toISOString().split('T')[0]);

    if (selectedDates.length > 0) {
        await addWorkingDays(selectedDates);

        await loadExistingDays(); // обновляем список

        // Очистка выбора
        datePicker.clear();

        // Обновляем список отображения пустым
        updateSelectedDatesList([]);

        alert("Даты успешно добавлены");
    } else {
        alert("Пожалуйста, выберите хотя бы одну дату.");
    }
});

// Загружаем существующие дни при старте
loadExistingDays();

