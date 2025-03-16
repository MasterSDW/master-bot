document.addEventListener('DOMContentLoaded', function() {
    // Перевірка наявності Alpine.js і завантаження, якщо потрібно
    if (typeof Alpine === 'undefined') {
        var collapseScript = document.createElement('script');
        collapseScript.src = 'https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.12.3/dist/cdn.min.js';
        collapseScript.defer = true;
        document.head.appendChild(collapseScript);
        
        var alpineScript = document.createElement('script');
        alpineScript.src = 'https://cdn.jsdelivr.net/npm/alpinejs@3.12.3/dist/cdn.min.js';
        alpineScript.defer = true;
        document.head.appendChild(alpineScript);
    }

    // Ініціалізація маски для телефону
    const phoneInput = document.querySelector('input[name="phone"]');
    if (phoneInput) {
        initPhoneMask(phoneInput);
    }

    // Обробка відправки форми
    const form = document.getElementById('repairForm');
    if (form) {
        const submitButton = form.querySelector('button[type="submit"]');
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Перевіряємо валідність телефону перед відправкою
            const phoneInput = form.querySelector('input[name="phone"]');
            const phoneMask = IMask.createMask({
                mask: '+38 (000) 00-00-000',
            });
            
            phoneMask.resolve(phoneInput.value);
            if (phoneMask.unmaskedValue.length < 10) {
                // Показуємо помилку, якщо телефон неправильний
                phoneInput.classList.add('is-invalid');
                
                // Перевіряємо, чи вже є повідомлення про помилку
                const errorDiv = phoneInput.parentNode.querySelector('.invalid-feedback');
                if (!errorDiv) {
                    const newErrorDiv = document.createElement('div');
                    newErrorDiv.className = 'invalid-feedback';
                    newErrorDiv.textContent = 'Будь ласка, введіть повний номер телефону';
                    phoneInput.parentNode.appendChild(newErrorDiv);
                }
                
                return; // Зупиняємо відправку форми
            }
            
            // Відключаємо кнопку на час відправки
            submitButton.disabled = true;
            
            try {
                // Збираємо дані форми в об'єкт
                const formData = {};
                new FormData(form).forEach((value, key) => {
                    formData[key] = value;
                });
                
                // Відправляємо дані на bot.py в форматі JSON
                const response = await fetch('/bot/submit-form', {
                    method: 'POST',
                    body: JSON.stringify(formData),
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Очищаємо форму і показуємо повідомлення про успіх
                    form.reset();
                    showMessage('Дякуємо за вашу заявку! Ми зв\'яжемося з вами найближчим часом.', 'success');
                } else {
                    showMessage(result.error || 'Виникла помилка при відправці форми', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showMessage('Виникла помилка при відправці форми. Спробуйте пізніше.', 'error');
            } finally {
                // Включаємо кнопку назад
                submitButton.disabled = false;
            }
        });
        
        // Очищаємо помилки при введенні
        form.querySelectorAll('input, textarea').forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
                const errorDiv = this.parentNode.querySelector('.invalid-feedback');
                if (errorDiv) {
                    errorDiv.remove();
                }
            });
        });
    }
});

/**
 * Ініціалізує маску для введення телефону у форматі +38 (***) **-**-***
 * @param {HTMLInputElement} input - Поле введення телефону
 */
function initPhoneMask(input) {
    // Створюємо маску для телефону за допомогою IMask
    const phoneMask = IMask(input, {
        mask: '+38 (000) 00-00-000',
        lazy: false,  // Показувати маску одразу
        placeholderChar: '_'
    });
    
    // Перевірка правильності номера при втраті фокусу
    input.addEventListener('blur', function() {
        // Перевіряємо, чи заповнена маска повністю
        if (phoneMask.unmaskedValue.length < 10) {
            // Додаємо клас помилки, якщо номер неповний
            this.classList.add('is-invalid');
            
            // Перевіряємо, чи вже є повідомлення про помилку
            const errorDiv = this.parentNode.querySelector('.invalid-feedback');
            if (!errorDiv) {
                const newErrorDiv = document.createElement('div');
                newErrorDiv.className = 'invalid-feedback';
                newErrorDiv.textContent = 'Будь ласка, введіть повний номер телефону';
                this.parentNode.appendChild(newErrorDiv);
            }
        } else {
            // Видаляємо клас помилки, якщо номер повний
            this.classList.remove('is-invalid');
            
            // Видаляємо повідомлення про помилку, якщо воно є
            const errorDiv = this.parentNode.querySelector('.invalid-feedback');
            if (errorDiv) {
                errorDiv.remove();
            }
        }
    });
    
    // Очищаємо помилки при введенні
    input.addEventListener('input', function() {
        this.classList.remove('is-invalid');
        const errorDiv = this.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    });
}

/**
 * Показує модальне вікно з повідомленням
 * @param {string} message - Текст повідомлення
 * @param {string} type - Тип повідомлення ('success' або 'error')
 */
function showMessage(message, type) {
    // Створюємо модальне вікно
    const modalDiv = document.createElement('div');
    modalDiv.className = 'fixed inset-0 flex items-center justify-center z-50 modal-enter';
    modalDiv.innerHTML = `
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" id="modal-backdrop"></div>
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-md w-full mx-4 relative transform transition-all shadow-xl modal-content-enter">
            <div class="absolute top-4 right-4">
                <button id="close-modal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            <div class="text-center">
                <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full ${type === 'success' ? 'bg-green-100 dark:bg-green-900' : 'bg-red-100 dark:bg-red-900'} mb-6">
                    ${type === 'success' 
                        ? `<svg class="w-8 h-8 text-green-600 dark:text-green-400 icon-animate" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                           </svg>` 
                        : `<svg class="w-8 h-8 text-red-600 dark:text-red-400 icon-animate" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                           </svg>`
                    }
                </div>
                <h3 class="text-xl font-medium text-gray-900 dark:text-white mb-2">
                    ${type === 'success' ? 'Успіх!' : 'Помилка!'}
                </h3>
                <p class="text-gray-600 dark:text-gray-300 mb-6">
                    ${message}
                </p>
                <button id="confirm-modal" class="w-full px-6 py-3 rounded-xl ${type === 'success' 
                    ? 'bg-gradient-to-r from-green-500 to-green-600' 
                    : 'bg-gradient-to-r from-blue-600 to-indigo-600'} 
                    text-white hover:shadow-lg transition-all transform hover:scale-105 button-animate">
                    ${type === 'success' ? 'Чудово!' : 'Зрозуміло'}
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modalDiv);
    
    // Додаємо анімацію появи
    setTimeout(() => {
        modalDiv.classList.remove('modal-enter');
        modalDiv.classList.add('modal-enter-active');
        
        const modalContent = modalDiv.querySelector('.bg-white');
        modalContent.classList.remove('modal-content-enter');
        modalContent.classList.add('modal-content-enter-active');
    }, 10);
    
    // Обробники подій для закриття модального вікна
    const closeModal = () => {
        modalDiv.classList.remove('modal-enter-active');
        modalDiv.classList.add('modal-exit-active');
        
        const modalContent = modalDiv.querySelector('.bg-white');
        modalContent.classList.remove('modal-content-enter-active');
        modalContent.classList.add('modal-content-exit-active');
        
        setTimeout(() => {
            modalDiv.remove();
        }, 300);
    };
    
    modalDiv.querySelector('#modal-backdrop').addEventListener('click', closeModal);
    modalDiv.querySelector('#close-modal').addEventListener('click', closeModal);
    modalDiv.querySelector('#confirm-modal').addEventListener('click', closeModal);
    
    // Автоматично закриваємо через 5 секунд для успішних повідомлень
    if (type === 'success') {
        setTimeout(closeModal, 5000);
    }
} 