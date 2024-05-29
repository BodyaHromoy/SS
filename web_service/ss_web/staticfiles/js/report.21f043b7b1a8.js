function setupAutocomplete(inputElement, url) {
    let dataList = document.createElement('div');
    dataList.className = 'autocomplete-items';
    dataList.style.position = 'absolute';
    dataList.style.top = inputElement.offsetHeight + 'px';
    dataList.style.width = inputElement.offsetWidth + 'px';
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

        let queryUrl = url;
        if (currentValue) {
            queryUrl += '?query=' + currentValue;
        }
        fetch(queryUrl)
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
                        option.innerHTML = displayItem.replace(currentValue, `<strong>${currentValue}</strong>`);
                        option.className = 'autocomplete-option';
                        option.addEventListener('click', function() {
                            let selectedItem = document.createElement('div');
                            selectedItem.className = 'selected-item';
                            selectedItem.innerHTML = displayItem + '<button type="button">x</button>';
                            selectedItem.querySelector('button').addEventListener('click', function() {
                                selectedItem.remove();
                            });
                            inputElement.parentNode.appendChild(selectedItem);

                            inputElement.value = '';
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
        if (e.key === 'ArrowDown') {
            activeOption = Math.min(activeOption + 1, dataList.children.length - 1);
        } else if (e.key === 'ArrowUp') {
            activeOption = Math.max(activeOption - 1, -1);
        } else if (e.key === 'Enter' && activeOption > -1) {
            dataList.children[activeOption].click();
            e.preventDefault();
        }

        Array.from(dataList.children).forEach((option, i) => {
            if (i === activeOption) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    });

    document.addEventListener('click', function(e) {
        if (e.target !== inputElement) {
            dataList.innerHTML = '';
            dataList.style.display = 'none';
        }
    });
}

// Подключаем автозаполнение к полям
setupAutocomplete(document.getElementById('station_id'), '/api/station_ids');
setupAutocomplete(document.getElementById('city'), '/api/cities');
setupAutocomplete(document.getElementById('zone'), '/api/zones');