document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('materialId')) {
        fetch('/get_materials')
            .then(response => response.json())
            .then(data => {
                const materialSelect = document.getElementById('materialId');
                data.forEach(material => {
                    const option = document.createElement('option');
                    option.value = material.MaterialID;
                    option.text = material.MaterialName;
                    materialSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error fetching materials:', error));
    }

    if (document.getElementById('request-status')) {
        fetch('/get_requests')
            .then(response => response.json())
            .then(data => {
                const requestTable = document.getElementById('request-status');
                data.forEach(request => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${request.RequestID}</td>
                        <td>${request.Status}</td>
                        <td>${request.Priority}</td>
                        <td>${request.MaterialID}</td>
                        <td>${request.Quantity}</td>
                        <td>${new Date(request.Timestamp).toLocaleString()}</td>
                    `;
                    requestTable.appendChild(row);
                });
            })
            .catch(error => console.error('Error fetching requests:', error));
    }
});
