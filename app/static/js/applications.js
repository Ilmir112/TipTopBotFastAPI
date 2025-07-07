// Анимация появления элементов
function animateElements() {
    const elements = document.querySelectorAll('h1, table');
    elements.forEach((el, index) => {
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 200 * index);
    });
}

// Запуск анимации при загрузке страницы
window.addEventListener('load', animateElements);

// Обработчик для прокрутки на мобильных устройствах
document.addEventListener('DOMContentLoaded', (event) => {
    const main = document.querySelector('main');
    let isScrolling;

    main.addEventListener('scroll', function () {
        window.clearTimeout(isScrolling);
        isScrolling = setTimeout(function () {
            console.log('Scrolling has stopped.');
        }, 66);
    }, false);
});


document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', () => {
            const applicationId = button.getAttribute('data-id');
            console.log(applicationId)
            if (confirm('Вы уверены, что хотите удалить эту заявку?')) {
                fetch(`/api/delete?application_id=${applicationId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        // Удаляем строку из таблицы
                        button.closest('tr').remove();
                    } else {
                        alert('Ошибка при удалении заявки.');
                    }
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                    alert('Произошла ошибка.');
                });
            }
        });
    });
});
document.getElementById('date-filter').addEventListener('change', function () {
            const urlParams = new URLSearchParams(window.location.search);
            const adminId = urlParams.get('admin_id'); //
            // Можно вставить его в скрытое поле формы
            document.querySelector('input[name="admin_id"]').value = adminId;
            // При выборе даты отправляем форму
            this.form.submit();
        });