// static/js/editable-mani-logs.js

function setupEditableManiCell(cell) { // in-line editing 
    const field = cell.dataset.field;
    const id = cell.dataset.id;
    const originalSpan = cell.querySelector('.field-value');
    const originalValue = originalSpan ? originalSpan.textContent.trim() : '';

    const input = document.createElement(field === 'full_desc' ? 'textarea' : 'input');
    input.value = currentValue;
    input.className = 'edit-input';

    if (field === 'mani_date') {
      input.type = 'date';
    }

    cell.innerHTML = '';
    cell.appendChild(input);
    input.focus();

    const save = () => { //send a POST request to /update_mani_record
        const newValue = input.value.trim();

        if (newValue === originalValue || !newValue) {
            renderValue(originalValue);
            return;
        }

        fetch(`/update_mani_record`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, field, value: newValue })
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    renderValue(newValue);
                } else {
                    alert('Update failed.');
                    renderValue(originalValue);
                }
            })
            .catch(() => {
                alert('Server error.');
                renderValue(originalValue);
            });
    };

    const renderValue = (value) => {
        cell.innerHTML = '';
        const span = document.createElement('span');
        span.className = 'field-value';
        span.textContent = value;
        cell.appendChild(span);
        setupManiListeners(); // rebind listeners after restoring view
    };

    input.addEventListener('blur', save);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        input.blur();
      }
    });
}

function setupManiListeners() {
  document.querySelectorAll('.mani-editable').forEach(cell => {
    cell.addEventListener('dblclick', () => setupEditableManiCell(cell))
  });
}

document.addEventListener('DOMContentLoaded', setupManiListeners);