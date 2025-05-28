document.addEventListener('DOMContentLoaded', function () {
  console.log('modal js loaded!');

  // Модальное окно
  const modal = document.getElementById('ad-modal');
  const modalConfirmBtn = document.getElementById('modal-confirm');
  const modalCancelBtn = document.getElementById('modal-cancel');
  const modalTitle = document.querySelector('#ad-modal h3');
  const modalAdData = document.getElementById('modal-ad-data');

  // Кнопки на форме
  const showConfirmBtn = document.getElementById('show-confirm');
  const showDeleteConfirmBtn = document.getElementById('show-delete-confirm');
  const adUpdateForm = document.getElementById('ad-update-form');
  const adCreateForm = document.getElementById('ad-create-form'); // Новое!
  const deleteAdForm = document.getElementById('delete-ad-form');

  let confirmAction = null;

  // Универсальная функция вывода предпросмотра
  function buildAdPreview(form) {
    const formData = new FormData(form);
    let html = '';
    html += '<div><b>Заголовок:</b> ' + (formData.get('title') || '') + '</div>';

    let description = formData.get('description') || '';
    if (description.length > 200) {
      description = description.slice(0, 197) + '...';
    }
    html += '<div><b>Описание:</b> <div style="max-height:200px; overflow:auto;">' + description + '</div></div>';

    // Для select-ов (category, condition) ищем их по имени
    const categorySelect = form.querySelector('[name="category"]');
    const conditionSelect = form.querySelector('[name="condition"]');
    html += '<div><b>Категория:</b> ' + (categorySelect ? categorySelect.options[categorySelect.selectedIndex].text : '') + '</div>';
    html += '<div><b>Состояние:</b> ' + (conditionSelect ? conditionSelect.options[conditionSelect.selectedIndex].text : '') + '</div>';

    return html;
  }

  // Обработка "Создать" или "Обновить"
  if (showConfirmBtn) {
    showConfirmBtn.addEventListener('click', function (e) {
      e.preventDefault();

      // Определяем, какая форма есть на странице
      let form = adUpdateForm || adCreateForm;
      if (!form) return;

      // Меняем заголовок модалки в зависимости от формы
      if (form === adUpdateForm) {
        modalTitle.textContent = "Подтвердите обновление";
      } else {
        modalTitle.textContent = "Подтвердите создание объявления";
      }
      modalAdData.innerHTML = buildAdPreview(form);
      modal.style.display = "flex";
      confirmAction = function () {
        form.submit();
      };
    });
  }

  // Обработка "Удалить"
  if (showDeleteConfirmBtn && adUpdateForm && deleteAdForm) {
    showDeleteConfirmBtn.addEventListener('click', function (e) {
      e.preventDefault();
      modalTitle.textContent = "Подтвердите удаление";
      modalAdData.innerHTML = buildAdPreview(adUpdateForm);
      modal.style.display = "flex";
      confirmAction = function () {
        deleteAdForm.submit();
      };
    });
  }

  // Подтвердить действие
  if (modalConfirmBtn) {
    modalConfirmBtn.addEventListener('click', function () {
      modal.style.display = "none";
      if (typeof confirmAction === "function") {
        confirmAction();
      }
    });
  }

  // Отмена
  if (modalCancelBtn) {
    modalCancelBtn.addEventListener('click', function () {
      modal.style.display = "none";
      confirmAction = null;
    });
  }

  // Клик вне окна — закрыть
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === modal) {
        modal.style.display = "none";
        confirmAction = null;
      }
    });
  }
});
