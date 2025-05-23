document.addEventListener('DOMContentLoaded', function () {
  const showConfirm = document.getElementById('show-confirm');
  const adForm = document.querySelector('form[id^="ad-"]');
  const adModal = document.getElementById('ad-modal');
  const modalAdData = document.getElementById('modal-ad-data');
  const modalConfirm = document.getElementById('modal-confirm');
  const modalCancel = document.getElementById('modal-cancel');

  if (!showConfirm || !adForm || !adModal) return;

  showConfirm.onclick = function() {
    const formData = new FormData(adForm);
    let html = '';
    html += '<div><b>Заголовок:</b> ' + (formData.get('title') || '') + '</div>';

    let description = formData.get('description') || '';
    if (description.length > 200) {
      description = description.slice(0, 197) + '...';
    }
    html += '<div><b>Описание:</b> <div style="max-height:200px; overflow:auto;">' + description + '</div></div>';

    html += '<div><b>Категория:</b> ' + (adForm.category?.options[adForm.category.selectedIndex]?.text || '') + '</div>';
    html += '<div><b>Состояние:</b> ' + (adForm.condition?.options[adForm.condition.selectedIndex]?.text || '') + '</div>';
    modalAdData.innerHTML = html;
    adModal.style.display = 'flex';
  };

  modalConfirm.onclick = function() {
    adModal.style.display = 'none';
    adForm.submit();
  };

  modalCancel.onclick = function() {
    adModal.style.display = 'none';
  };
});
