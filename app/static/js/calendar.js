

function updateSelectedDatesList(dates) {
    const list = document.getElementById("selectedDatesList");
    list.innerHTML = ""; // Очистить список

    dates.forEach(date => {
        const li = document.createElement("li");
        li.classList.add("date-item");
        li.textContent = date.toISOString().split('T')[0];

        // Кнопка для удаления даты
        const removeBtn = document.createElement("span");
        removeBtn.textContent = " ×";
        removeBtn.classList.add("remove-date");
        removeBtn.onclick = function () {
            datePicker.setDate(dates.filter(d => d !== date), true); // Удалить дату
            updateSelectedDatesList(datePicker.selectedDates); // Обновить список отображаемых дат
        };

        li.appendChild(removeBtn);
        list.appendChild(li);
    });
}

document.getElementById("submitDates").addEventListener("click", function () {
    const selectedDates = datePicker.selectedDates.map(date => {
        return {date: date.toISOString().split('T')[0]};
    });

    if (selectedDates.length > 0) {
        fetch("/day/add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(selectedDates),
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                alert(data.message);
                datePicker.clear(); // Очистить выбор после отправки
                updateSelectedDatesList([]); // Удалить все даты из списка
            })
            .catch(error => console.error("Ошибка:", error));
    } else {
        alert("Пожалуйста, выберите хотя бы одну дату.");
    }
});