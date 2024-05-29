let socket;
let socket_reports;
let reconnectAttempts = 0;
const maxReconnectAttempts = 10;
const reconnectInterval = 2000; // 2 seconds

let historyStack = [];
let typeStack = [];

function connectSocket() {
    socket = new WebSocket('ws://' + window.location.host + '/ws/ss_main/');
    socket_reports = new WebSocket('ws://' + window.location.host + '/ws/ss_main/reports');

    socket.onopen = function() {
        reconnectAttempts = 0;
        console.log("Socket connected!");
    };

    socket.onmessage = function(event) {
        const response = JSON.parse(event.data);
        updateContent(response);
    };

    socket.onerror = function(error) {
        console.error("WebSocket error:", error);
    };

    socket.onclose = function(event) {
        console.log(`WebSocket closed with code: ${event.code}. Attempting to reconnect...`);
        if (reconnectAttempts < maxReconnectAttempts) {
            setTimeout(connectSocket, reconnectInterval);
            reconnectAttempts++;
        } else {
            console.error("Max reconnect attempts reached. WebSocket not connected.");
        }
    };

    socket_reports.onmessage = function(event) {
        const response = JSON.parse(event.data);
        updateReports(response);
    };

    socket_reports.onerror = function(error) {
        console.error("WebSocket reports error:", error);
    };

    socket_reports.onclose = function(event) {
        console.log(`WebSocket reports closed with code: ${event.code}. Attempting to reconnect...`);
        if (reconnectAttempts < maxReconnectAttempts) {
            setTimeout(connectSocket, reconnectInterval);
            reconnectAttempts++;
        } else {
            console.error("Max reconnect attempts reached. WebSocket reports not connected.");
        }
    };
}

connectSocket();

function refreshData() {
    const currentType = typeStack[typeStack.length - 1];
    const currentAction = currentType === 'cabinets' ? 'load_cabinets' :
                          currentType === 'cells' ? 'load_cells' :
                          currentType === 'cell' ? 'load_cell' : null;

    if (currentAction) {
        let data = {'action': currentAction};
        if (currentType === 'cells') {
            data['cabinet_id'] = document.querySelector('#dataTable tr:first-child td:first-child').innerText;
        } else if (currentType === 'cell') {
            data['vir_sn_eid'] = document.querySelector('#dataTable tr:first-child td:first-child').innerText;
        }
        socket.send(JSON.stringify(data));
    } else {
        console.log("Невозможно обновить данные для текущего типа.");
    }
}

function updateContent(response) {
    const type = response.type;
    const answer_data = response.data;
    let breadcrumbHtml = '';
    let tableHtml = '<table class="table table-striped" id="dataTable">';

    updateBreadcrumb(type);
    typeStack.push(type);

    const currentContent = document.getElementById('dataDisplay').innerHTML;
    if (currentContent) {
        if (historyStack.length >= 7) {
            historyStack.shift();
        }
        historyStack.push(currentContent);
    }

    if (type === 'cabinets') {
        tableHtml += `
            <thead>
                <tr>
                    <th>City</th>
                    <th>Zone</th>
                    <th>Box ID</th>
                    <th>Address</th>
                    <th>Locker ID</th>
                    <th>Additional info</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>`;
        answer_data.forEach(item => {
            tableHtml += `<tr>
                              <td>${item.city}</td>
                              <td>${item.zone}</td>
                              <td>${item.shkaf_id}</td>
                              <td>${item.location}</td>
                              <td>${item.street}</td>
                              <td>${item.extra_inf}</td>
                              <td><button class="btn btn-primary" onclick="loadCells(${item.shkaf_id})">Check slots</button></td>
                          </tr>`;
        });

    } else if (type === 'cells') {
        tableHtml += `
            <thead>
                <tr>
                    <th>Box</th>
                    <th>Slot ID</th>
                    <th>Status</th>
                    <th>Charge in %</th>
                    <th>Vendor</th>
                    <th>Actions</th>
                </tr>
            </thead>

            <tbody>`;
        answer_data.forEach(item => {
            let chargeColor = '';
            if (item.charge >= 91) {
                chargeColor = 'green';
            } else if (item.charge >= 50) {
                chargeColor = 'blue';
            } else if (item.charge >= 30) {
                chargeColor = 'yellow';
            } else {
                chargeColor = 'red';
            }

            let statusIcon = '';
            switch (item.status) {
                case 'charging':
                    statusIcon = '<span class="status-icon charging-icon"></span>';
                    break;
                case 'not_charging':
                    statusIcon = '<span class="status-icon not-charging-icon"></span>';
                    break;
                case 'empty':
                    statusIcon = '<span class="status-icon empty-icon"></span>';
                    break;
                case 'inactive':
                    statusIcon = '<span class="status-icon inactive-icon"></span>';
                    break;
                case 'ready':
                    statusIcon = '<span class="status-icon ready-icon"></span>';
                    break;
                case 'full':
                    statusIcon = '<span class="status-icon ready-icon"></span>';
                    break;
                default:
                    statusIcon = '';
                    break;
            }
            tableHtml += `<tr>
                              <td>${item.station_id}</td>
                              <td>${item.id}</td>
                              <td>${statusIcon}${item.status}</td>
                              <td><span class="charge-circle ${chargeColor}"></span>${item.charge}</td>
                              <td>${item.vid}</td>
                              <td><button class="btn btn-primary" onclick="loadCell('${item.vir_sn_eid}')">MARKET INFO</button></td>
                           </tr>`;
        });
    } else if (type === 'cell') {
        tableHtml += `
            <thead>
                <tr>
                    <th>SLOT ID</th>
                    <th>SERIAL №</th>
                    <th>SW_VER</th>
                </tr>
            </thead>
            <tbody>`;
        tableHtml += `<tr>
                          <td>${answer_data.name}</td>
                          <td>${answer_data.sn}</td>
                          <td>${answer_data.sw_ver}</td>
                      </tr>`;
    }

    tableHtml += '</tbody></table>';
    document.getElementById('breadcrumb').innerHTML = breadcrumbHtml;
    document.getElementById('dataDisplay').innerHTML = tableHtml;
}

function loadCells(cabinetId) {
    socket.send(JSON.stringify({'action': 'load_cells', 'cabinet_id': cabinetId}));
}

function loadCell(vir_sn_eid) {
    socket.send(JSON.stringify({'action': 'load_cell', 'vir_sn_eid': vir_sn_eid}));
}

document.querySelectorAll('.nav-link').forEach(item => {
    item.addEventListener('click', function(e) {
        socket.send(JSON.stringify({'action': 'load_cabinets'}));
    });
});

function updateBreadcrumb(type) {
    let breadcrumb = 'Главная > ';

    switch(type) {
        case 'cabinets':
            breadcrumb += 'Шкафы';
            break;
        case 'cells':
            breadcrumb += 'Шкафы > Ячейки';
            break;
        case 'cell':
            breadcrumb += 'Шкафы > Ячейки > Детали ячейки';
            break;
    }

    document.getElementById('breadcrumb').textContent = breadcrumb;
}

function goBack() {
    if (historyStack.length > 0) {
        const lastState = historyStack.pop();
        const lastType = typeStack.pop();

        document.getElementById('dataDisplay').innerHTML = lastState;
        updateBreadcrumb(lastType);
    } else {
        alert("Нет предыдущих состояний для отображения!");
        updateBreadcrumb('home');
    }
}

function toggleFilters() {
    const filters = document.getElementById("filters");
    if (filters.style.display === "none") {
        filters.style.display = "block";
    } else {
        filters.style.display = "none";
    }
}

function applyFilters() {
    const cityFilter = document.getElementById("cityFilter").value;
    const zoneFilter = document.getElementById("zoneFilter").value;

    const table = document.getElementById("dataTable");
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        const rowData = rows[i].getElementsByTagName("td");
        const city = rowData[0].innerText;
        const zone = rowData[1].innerText;
        const cityMatch = cityFilter === "" || city === cityFilter;
        const zoneMatch = zoneFilter === "" || zone === zoneFilter;
        rows[i].style.display = cityMatch && zoneMatch ? "" : "none";
    }
}

function filterTable() {
    const input = document.getElementById("searchInput").value.toLowerCase();
    const table = document.getElementById("dataTable");
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        const rowData = rows[i].getElementsByTagName("td");
        let found = false;

        for (let j = 0; j < rowData.length; j++) {
            const cellData = rowData[j].textContent.toLowerCase();
            if (cellData.indexOf(input) > -1) {
                found = true;
                break;
            }
        }

        rows[i].style.display = found ? "" : "none";
    }
}

function toggleSearch() {
    const searchContainer = document.getElementById("searchContainer");
    if (searchContainer.style.display === "none") {
        searchContainer.style.display = "block";
    } else {
        searchContainer.style.display = "none";
    }
}

function clearSearch() {
    document.getElementById("searchInput").value = "";
    filterTable();
}