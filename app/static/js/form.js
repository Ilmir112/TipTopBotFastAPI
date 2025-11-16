//
// // Функция для обновления доступности дат в input type="date"
// function updateDateInputAvailability() {
//     const dateInput = document.getElementById('date');
//
//     // Удаляем все ранее добавленные кастомные ограничения
//     dateInput.removeAttribute('min');
//     dateInput.removeAttribute('max');
//
//     // Вариант 1: блокировать только рабочие дни (если нужно)
//     // Для этого можно использовать событие 'oninput' или 'onchange' и проверять выбранную дату
//
//     // Вариант 2: использовать атрибут 'disabled' для отдельных дат — не поддерживается стандартным input,
//     // поэтому лучше реализовать через обработчик события
//
//     // Добавим обработчик изменения даты
//     dateInput.addEventListener('change', () => {
//         const selectedDate = dateInput.value;
//         if (workingDays.includes(selectedDate)) {
//             // Если дата входит в рабочие дни — показываем сообщение или делаем что-то еще
//             alert('Выбран рабочий день. Пожалуйста, выберите другой день.');
//             dateInput.value = ''; // сбрасываем выбор
//         }
//     });
// }

// Ваша существующая функция для получения занятых времён
async function fetchBookedTimes(appointmentDate) {
    const response = await fetch(`/api/get_booked_times?appointment_date=${appointmentDate}`);
    if (!response.ok) {
        throw new Error('Ошибка при получении данных');
    }
    const bookedTimes = await response.json();
    return bookedTimes; // массив строк, например ['09:00', '10:30', ...]
}


// Функция для обновления доступных времён
async function updateAvailableTimes() {
    const dateInput = document.getElementById('date');
    const selectedDate = dateInput.value;
    if (!selectedDate) return;

    try {
        const bookedTimes = await fetchBookedTimes(selectedDate);
        // Обновляем кнопки с временами
        const allTimeButtons = document.querySelectorAll('.time-btn');

        allTimeButtons.forEach(btn => {
            const time = btn.dataset.time;
            if (bookedTimes.includes(time)) {
                btn.disabled = false; // разблокируем свободные
            } else {
                btn.disabled = true; // блокируем занятые
                btn.classList.remove('active');
            }
        });
    } catch (error) {
        console.error(error);
    }
}

// Обработчики изменения даты и мастера
document.getElementById('date').addEventListener('change', updateAvailableTimes);


// Вызовем при загрузке страницы, чтобы сразу показать актуальные данные
window.addEventListener('load', () => {
    updateAvailableTimes();
});


document.getElementById('appointmentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const service = document.getElementById('service').options[document.getElementById('service').selectedIndex].text;
    const date = document.getElementById('date').value;
    const appointment_time = document.getElementById('selectedTime').value;

    console.log(appointment_time);

    let popupMessage = '';

    if (name.length < 2 || name.length > 50) {
        popupMessage = "Имя должно быть от 2 до 50 символов.";
        showPopup(popupMessage);
        return;
    }
    if (service.length < 2 || service.length > 50) {
        popupMessage = "Услуга должна быть от 2 до 50 символов.";
        showPopup(popupMessage);
        return;
    }
    if (!appointment_time) {
        popupMessage = "Пожалуйста, выберите время услуги.";
        showPopup(popupMessage);
        return;
    }
    if (!date) {
        popupMessage = "Пожалуйста, выберите дату услуги";
        showPopup(popupMessage);
        return;
    }

    // Если все проверки пройдены
    popupMessage = `${name}, вы планируете запись на услугу \n${service.toLowerCase()} \n${date} в ${appointment_time}.`;
    showPopup(popupMessage);
});

// Функция для показа попапа
function showPopup(message) {
    document.getElementById('popupMessage').textContent = message;
    document.getElementById('popup').style.display = 'flex';
}

// Закрытие попапа при клике на крестик
document.querySelector('.close-popup').addEventListener('click', function() {
    document.getElementById('popup').style.display = 'none';
});

// Дополнительно: закрытие попапа при клике вне его области
document.getElementById('popup').addEventListener('click', function(e) {
    if (e.target.id === 'popup') {
        document.getElementById('popup').style.display = 'none';
    }
});

// Анимация появления элементов при загрузке страницы
function animateElements() {
    const elements = document.querySelectorAll('h1, .form-group, .btn');
    elements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

// Стили для анимации
var styleSheet = document.styleSheets[0];
styleSheet.insertRule(`
h1, .form-group, .btn {
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.5s ease, transform 0.5s ease;
}
`, styleSheet.cssRules.length);

window.addEventListener('load', function () {
    document.body.style.opacity = '1';
    animateElements();
});

styleSheet.insertRule(`
body {
    opacity: 0;
    transition: opacity 0.5s ease;
}
`, styleSheet.cssRules.length);

// Добавляем текущую дату в поле даты
document.addEventListener('DOMContentLoaded', (event) => {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').setAttribute('min', today);
});

// Обработчик для выбора времени при клике на кнопки
const buttons = document.querySelectorAll('.time-btn');
const hiddenInput = document.getElementById('selectedTime');

buttons.forEach(button => {
    button.addEventListener('click', () => {
        // Удаляем активный класс у всех кнопок
        buttons.forEach(btn => btn.classList.remove('active'));
        // Добавляем активный класс выбранной кнопке
        button.classList.add('active');
        // Устанавливаем значение скрытого поля
        hiddenInput.value = button.dataset.time;
    });
});

async function findWorkingDayIdByDate(dateString) {
    const url = `/find_id?working_day=${encodeURIComponent(dateString)}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Предположим, что API возвращает либо объект с id, либо null
        return data; // data — это working_day_id или null
    } catch (error) {
        console.error('Ошибка при вызове API:', error);
        return null;
    }
}

// Обработчик для закрытия попапа и отправки данных
document.getElementById('closePopup').addEventListener('click', async function () {
    const name = document.getElementById('name').value.trim();
    const serviceSelect = document.getElementById('service');
    const serviceText = serviceSelect ? serviceSelect.value : '';
    const date = document.getElementById('date').value;
    const userId = document.getElementById('user_id') ? document.getElementById('user_id').value : '';
    const appointment_time = document.getElementById('selectedTime').value;
    // const workingDayId = document.getElementById("workingDayId").value

    // Валидация
    if (name.length < 2 || name.length > 50) {
        alert("Имя должно быть от 2 до 50 символов.");
        return;
    }
    if (serviceText.length < 2 || serviceText.length > 50) {
        alert("Услуга должна быть от 2 до 50 символов.");
        return;
    }
    if (!appointment_time) {
        alert("Пожалуйста, выберите время услуги.");
        return;
    }
    if (!date) {
        alert("Пожалуйста, выберите дату услуги")
        return;
    }

    const appointmentData = {
        name: name,
        service: serviceText,
        appointment_date: date,
        appointment_time: appointment_time,
        user_id: userId,
        // working_day_id: workingDayId
    };

    try {
        const response = await fetch('/api/appointment', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(appointmentData)
        });
        const result = await response.json();

        if (result.status === 'busy') {
            // Время занято — показываем сообщение в попап
            document.getElementById('popupMessage').innerText = 'Это время уже занято. Пожалуйста, выберите другое.';
            document.getElementById('popup').style.display = 'block'; // показываем попап
        } else if (result.status === 'success') {
            document.getElementById('popupMessage').innerText = 'Вы успешно записаны!';
            // Можно оставить попап открытым чуть дольше или скрыть его сразу
            document.getElementById('popup').style.display = 'none';

            // Задержка для отображения сообщения
            setTimeout(() => {
                window.Telegram.WebApp.close();
            }, 1000); // 1 секунда
        }
    }
catch
(error)
{
    console.error('Ошибка при отправке:', error);
    alert('Произошла ошибка. Попробуйте еще раз.');
}
})
;



