// Ваша существующая функция для получения занятых времён
async function fetchBookedTimes(appointmentDate, masterId) {
    const response = await fetch(`/api/get_booked_times?appointment_date=${appointmentDate}&master_id=${masterId}`);
    if (!response.ok) {
        throw new Error('Ошибка при получении данных');
    }
    const bookedTimes = await response.json();
    return bookedTimes; // массив строк, например ['09:00', '10:30', ...]
}

// Функция для обновления доступных времён
async function updateAvailableTimes() {
    const dateInput = document.getElementById('date');
    const masterInput = document.getElementById('master'); // предполагается, что есть такое поле
    const masterId = masterInput && masterInput.value ? parseInt(masterInput.value.split('_')[0], 10) : null;
    const selectedDate = dateInput.value;
    if (!selectedDate || !masterId) return;

    try {
        const bookedTimes = await fetchBookedTimes(selectedDate, masterId);
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
if (document.getElementById('master')) {
    document.getElementById('master').addEventListener('change', updateAvailableTimes);
}

// Вызовем при загрузке страницы, чтобы сразу показать актуальные данные
window.addEventListener('load', () => {
    updateAvailableTimes();
});

// Остальной ваш существующий код

document.getElementById('appointmentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const service = document.getElementById('service').options[document.getElementById('service').selectedIndex].text;
    const date = document.getElementById('date').value;
    const time = document.getElementById('selectedTime').value;

    const popupMessage = `${name}, вы планируете запись на ${service.toLowerCase()} ${date} в ${time}.`;
    document.getElementById('popupMessage').textContent = popupMessage;

    document.getElementById('popup').style.display = 'flex';
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

// Обработчик для закрытия попапа и отправки данных
document.getElementById('closePopup').addEventListener('click', async function () {
        const name = document.getElementById('name').value.trim();
        const serviceSelect = document.getElementById('service');
        const serviceText = serviceSelect ? serviceSelect.value : '';
        // const serviceId = serviceValue ? parseInt(serviceValue.split('_')[0], 10) : null;
        // const serviceText = document.getElementById('service').trim();
        const date = document.getElementById('date').value;
        const userId = document.getElementById('user_id') ? document.getElementById('user_id').value : '';
        // const master = document.getElementById('master') ? document.getElementById('master').value.trim() : '';

        // Получаем выбранное время из скрытого поля
        const appointment_time = document.getElementById('selectedTime').value;

        // Проверяем валидность полей
        if (name.length < 2 || name.length > 50) {
            alert("Имя должно быть от 2 до 50 символов.");
            return;
        }

        if (serviceText.length < 2 || serviceText.length > 50) {
            alert("Услуга должна быть от 2 до 50 символов.");
            return;
        }

        // if (master && (master.length < 2 || master.length > 50)) {
        //     alert("Имя мастера должно быть от 2 до 50 символов.");
        //     return;
        // }

        if (!appointment_time) {
            alert("Пожалуйста, выберите время услуги.");
            return;
        }

        // Создаем объект с данными
        const appointmentData = {
            name: name,
            service: serviceText,
            appointment_date: date,
            appointment_time: appointment_time,
            // master: master,
            user_id: userId
        };

        // Преобразуем объект в JSON строку
        const jsonData = JSON.stringify(appointmentData);

        // Отправляем POST запрос на /api/appointment
        try {
            const response = await fetch('/api/appointment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: jsonData
            });
            const result = await response.json();
            console.log('Response from /form:', result);

            if (result.status === 'busy') {
                // Время занято — показываем окно с сообщением
                document.getElementById('popupMessage').innerText = 'Это время уже занято. Пожалуйста, выберите другое.';
                document.getElementById('popup').style.display = 'block'; // показываем попап
            } else if (result.status === 'success') {
                // Всё прошло успешно — закрываем попап и закрываем WebApp
                document.getElementById('popup').style.display = 'none';
                setTimeout(() => {
                    window.Telegram.WebApp.close();
                }, 100);
            }
        } catch (error) {
            console.error('Error sending POST request:', error);
        }
    }
)
