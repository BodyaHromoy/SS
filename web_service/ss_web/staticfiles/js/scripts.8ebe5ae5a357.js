const socket = new WebSocket('ws://' + window.location.host + '/ws/ss_main/');
const socket_reports = new WebSocket('ws://' + window.location.host + '/ws/ss_main/reports');

console.log("hi!");
let historyStack = [];
let typeStack = [];

socket.onmessage = function(event) {
    const response = JSON.parse(event.data);
    updateContent(response);
};

socket_reports.onmessage = function(event) {
    const response = JSON.parse(event.data);
    updateReports(response);
};

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
                    <th>City &#9650;</th>
                    <th>Zone &#9650;</th>
                    <th>Box ID &#9650;</th>
                    <th>Address &#9650;</th>
                    <th>Locker ID &#9650;</th>
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
                    <th>Box &#9650;</th>
                    <th>Slot ID &#9650;</th>
                    <th>Status &#9650;</th>
                    <th>Charge in % &#9650;</th>
                    <th>Vendor &#9650;</th>
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
    document.getElementById('dataDisplay