function setupAutocomplete(inputElement, url) {
    let dataList = document.createElement('div');
    dataList.className = 'autocomplete-items';
    inputElement.parentNode.appendChild(dataList);

    let timeout = null;
    inputElement.addEventListener('input', function(e) {
        clearTimeout(timeout);
        timeout = setTimeout(fetchOptions, 300);
    });

    inputElement.addEventListener('focus', fetchOptions);

    function fetchOptions() {
        let currentValue = inputElement.value;
        dataList.innerHTML = '';

        if (!currentValue) {
            dataList.style.display = 'none';
            return;
        }

        fetch(url + '?query=' + currentValue)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.length === 0) {
                    dataList.style.display = 'none';
                } else {
                    data.forEach(function(item) {
                        let option = document.createElement('div');
                        let displayItem = item.split('-')[0]; // Отображаем только часть до "-"
                        option.innerHTML = displayItem.replace(new RegExp(currentValue, 'gi'), match => `<strong>${match}</strong>`);
                        option.className = 'autocomplete-option';
                        option.addEventListener('click', function() {
                            inputElement.value = displayItem;
                            dataList.innerHTML = '';
                            dataList.style.display = 'none';
                        });
                        dataList.appendChild(option);
                    });
                    dataList.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('There has been a problem with your fetch operation:', error);
            });
    }

    let activeOption = -1;
    inputElement.addEventListener('keydown', function(e) {
        let options = dataList.children;
        if (e.key === 'ArrowDown') {
            activeOption = (activeOption + 1) % options.length;
        } else if (e.key === 'ArrowUp') {
            activeOption = (activeOption - 1 + options.length) % options.length;
        } else if (e.key === 'Enter' && activeOption > -1) {
            options[activeOption].click();
            e.preventDefault();
        }

        Array.from(options).forEach((option, i) => {
            if (i === activeOption) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    });

    document.addEventListener('click', function(e) {
        if (e.target !== inputElement && e.target.parentNode !== dataList) {
            dataList.innerHTML = '';
            dataList.style.display = 'none';
        }
    });
}

document.querySelectorAll('.clear-input').forEach(function(button) {
    button.addEventListener('click', function() {
        let inputElement = this.previousElementSibling;
        inputElement.value = '';
        inputElement.focus();
        let event = new Event('input');
        inputElement.dispatchEvent(event);
    });
});

// Подключаем автозаполнение к полям
setupAutocomplete(document.getElementById('station_id'), '/api/station_ids');
setupAutocomplete(document.getElementById('city'), '/api/cities');
setupAutocomplete(document.getElementById('zone'), '/api/zones');
