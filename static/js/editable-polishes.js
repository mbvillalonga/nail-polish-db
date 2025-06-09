// static/js/editable-polishes.js

function setupEditableCell(cell) { // in-line editing of plain-text fields
    const field = cell.dataset.field;
    const id = cell.dataset.id;

    let options = [];
    try {
        options = JSON.parse(cell.dataset.options || "[]");
    } catch (e) {
        options = [];
    }

    const createEditor = () => { // creates a textarea or input field
        const span = cell.querySelector('.field-value');
        const currentValue = span ? span.textContent.trim() : '';
        const input = document.createElement(field === 'full_desc' ? 'textarea' : 'input');
        input.value = currentValue;
        input.className = 'edit-input';

        if (options.length > 0) { // attach data list for autocomplete
            const listId = `options-${field}-${id}`;
            input.setAttribute('list', listId);

            if (!document.getElementById(listId)) {
                const datalist = document.createElement('datalist');
                datalist.id = listId;
                options.forEach(opt => {
                    const optionElem = document.createElement('option');
                    optionElem.value = opt;
                    datalist.appendChild(optionElem);
                });
                document.body.appendChild(datalist);
            }
        }

        return { input, currentValue };
    };

    const commitChange = (input, originalValue) => {
        // if value changed, send a POST request to /update_polish_field
        const newValue = input.value.trim();
        if (newValue === originalValue) {
            renderValue(originalValue);
            return;
        }

        fetch(`/update_polish_field`, {
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
        setupEditableCell(cell);
    };

    const handleDblClick = () => { // clears cell and inserts editor
        const { input, currentValue } = createEditor();
        cell.innerHTML = '';
        cell.appendChild(input);
        input.focus();

        input.addEventListener('blur', () => commitChange(input, currentValue)); // listen for blur
        input.addEventListener('keydown', e => {
            if (e.key === 'Enter' && field !== 'full_desc') {
                e.preventDefault();
                input.blur();
            }
        });
    };

    cell.addEventListener('dblclick', handleDblClick);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.editable').forEach(setupEditableCell);

    document.querySelectorAll('.editable-tags').forEach(cell => {
        // enable Select2-based tag editing
        const polishId = cell.dataset.id;

        cell.addEventListener('dblclick', () => {
            // confirm script is running
            console.log("Double-clicked editable-tags cell", cell);

            // read visible tags in the cell, turn them into strings:
            const tags = Array.from(cell.querySelectorAll('.tag-label')).map(span => span.textContent.trim());
            // console.log("Parsed tags:", tags); // Debug to check if correct tag names appear

            // replace <td> contents with a <select multiple>:
            const select = document.createElement('select');
            select.setAttribute('multiple', 'multiple');
            select.classList.add('tag-editor');
            select.style.width = '100%';
            cell.innerHTML = '';
            cell.appendChild(select);
            
            // insert <option>s for current tags:
            tags.forEach(tag => {
                const option = document.createElement("option");
                option.value = tag;
                option.textContent = tag; // explicitly set visible text
                option.selected = true;
                select.appendChild(option);
            });

            // initialize Select2
            $(select).select2({
                tags: true,
                placeholder: 'Select or create tags',
                ajax: {
                    url: '/search/tags',
                    dataType: 'json',
                    delay: 200,
                    data: params => ({ q: params.term }),
                    processResults: data => ({
                        results: data.map(tag => ({ id: tag.value, text: tag.label }))
                    }),
                    cache: true
                },
                width: 'resolve'
            });

            // Ensure the real input gets focus
            setTimeout(() => {
                const input = document.querySelector('.select2-container--open .select2-search__field');
                if (input) input.focus();
            }, 0);

            // change/lose focus
            const save = () => {
                const selectedTags = $(select).val(); // array of tag strings
                fetch('/update_polish_tags', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: polishId, tags: selectedTags })
                })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            cell.innerHTML = '';
                            if (selectedTags.length > 0) {
                                $(select).find('option:selected').each(function () {
                                    const label = this.textContext || this.innerText;
                                    const span = document.createElement('span');
                                    span.className = 'tag-label'
                                    span.textContent = label;
                                    cell.appendChild(span);

                                });
                            } else {
                                cell.innerHTML = '<em>No tags</em>';
                            }
                        } else {
                            alert("Failed to update tags.");
                        }
                    });
            };

            // listen for Enter key in Select2's actual input
            $(document).on('keydown.select2-edit', '.select2-container--open input.select2-search__field', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    save();
                }
            });

            // save when clicking outside the cell
            document.addEventListener('click', function handleOutsideClick(event) {
                if (!cell.contains(event.target)) {
                    save();
                    document.removeEventListener('click', handleOutsideClick);
                    $(document).off('keydown.select2-edit');
                }
            });
        });
    });
});
