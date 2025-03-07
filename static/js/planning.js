// script.js
document.addEventListener('DOMContentLoaded', function () {
    const calendarBody = document.querySelector('.calendar tbody');
    const month = 2; // March (0-indexed)
    const year = 2025;

    // Fetch tasks from the backend
    fetch('/planning/')  // Add a URL to fetch tasks as JSON
        .then(response => response.json())
        .then(tasks => {
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const daysInMonth = lastDay.getDate();
            const startingDay = firstDay.getDay();

            let date = 1;
            let html = '';

            for (let i = 0; i < 6; i++) {
                html += '<tr>';
                for (let j = 0; j < 7; j++) {
                    if (i === 0 && j < startingDay) {
                        html += `<td class="empty"></td>`;
                    } else if (date > daysInMonth) {
                        html += `<td class="empty"></td>`;
                    } else {
                        const currentDate = new Date(year, month, date);
                        const task = tasks.find(t => t.date === currentDate.toISOString().split('T')[0]);
                        html += `<td>
                            <div>${date}</div>
                            ${task ? `<div class="task">${task.title}</div>` : ''}
                        </td>`;
                        date++;
                    }
                }
                html += '</tr>';
                if (date > daysInMonth) break;
            }

            calendarBody.innerHTML = html;
        });
});
