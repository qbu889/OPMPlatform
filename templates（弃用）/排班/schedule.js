// roster.js
class RosterCalendar {
    constructor() {
        this.currentDate = new Date(2026, 1, 14); // 从数据中的第一个日期开始
        this.rosterData = [];
        this.init();
    }

    init() {
        this.loadData();
        this.setupEventListeners();
        this.renderCalendar();
    }

    loadData() {
        // 模拟从 CSV 数据加载
        this.rosterData = [
            {id: 191, date: '2026-02-14', time_slot: '8:00～9:00', staff_name: '林子旺', core_staff: 0},
            {id: 192, date: '2026-02-14', time_slot: '9:00～12:00', staff_name: '郑晨昊', core_staff: 1},
            {id: 193, date: '2026-02-14', time_slot: '9:00～12:00', staff_name: '林子旺', core_staff: 0},
            {id: 194, date: '2026-02-14', time_slot: '9:00～12:00', staff_name: '曾婷婷', core_staff: 0},
            {id: 195, date: '2026-02-14', time_slot: '9:00～12:00', staff_name: '陈伟强', core_staff: 0},
            {id: 196, date: '2026-02-14', time_slot: '13:30～18:00', staff_name: '郑晨昊', core_staff: 1},
            {id: 197, date: '2026-02-14', time_slot: '13:30～18:00', staff_name: '林子旺', core_staff: 0},
            {id: 198, date: '2026-02-14', time_slot: '13:30～18:00', staff_name: '曾婷婷', core_staff: 0},
            {id: 199, date: '2026-02-14', time_slot: '13:30～18:00', staff_name: '陈伟强', core_staff: 0},
            {id: 200, date: '2026-02-14', time_slot: '18:00～21:00', staff_name: '林子旺', core_staff: 0},
            {id: 201, date: '2026-02-15', time_slot: '8:00～12:00', staff_name: '林子旺', core_staff: 0},
            {id: 202, date: '2026-02-15', time_slot: '13:30～17:30', staff_name: '林子旺', core_staff: 0},
            {id: 203, date: '2026-02-15', time_slot: '17:30～21:30', staff_name: '林子旺', core_staff: 0},
            // 更多数据...
        ];

        // 按日期和时段整理数据
        this.groupedData = this.rosterData.reduce((acc, item) => {
            if (!acc[item.date]) acc[item.date] = {};
            if (!acc[item.date][item.time_slot]) acc[item.date][item.time_slot] = [];
            acc[item.date][item.time_slot].push(item);
            return acc;
        }, {});
    }

    setupEventListeners() {
        document.getElementById('monthPicker').addEventListener('change', (e) => {
            const [year, month] = e.target.value.split('-').map(Number);
            this.currentDate = new Date(year, month - 1, 1);
            this.renderCalendar();
        });

        document.getElementById('prevMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.renderCalendar();
        });

        document.getElementById('nextMonth').addEventListener('click', () => {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.renderCalendar();
        });

        document.getElementById('refreshData').addEventListener('click', () => {
            this.loadData();
            this.renderCalendar();
        });
        // 排班查询相关
        document.getElementById('searchScheduleBtn').addEventListener('click', searchSchedule);

        //排班导出
        document.getElementById('exportScheduleBtn').addEventListener('click', exportSchedule);

    }

    renderCalendar() {
        const calendarBody = document.getElementById('calendarBody');
        calendarBody.innerHTML = '';

        const startDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const endDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);

        const firstDay = new Date(startDate);
        firstDay.setDate(firstDay.getDate() - firstDay.getDay()); // 从周一开始

        const lastDay = new Date(endDate);
        lastDay.setDate(lastDay.getDate() + (6 - lastDay.getDay())); // 到周日结束

        const current = new Date(firstDay);

        while (current <= lastDay) {
            const row = this.createDateRow(current);
            calendarBody.appendChild(row);
            current.setDate(current.getDate() + 1);
        }
    }

    createDateRow(date) {
        const row = document.createElement('tr');
        const dateString = date.toISOString().split('T')[0];
        const dayOfWeek = ['日', '一', '二', '三', '四', '五', '六'][date.getDay()];

        const isWeekend = date.getDay() === 0 || date.getDay() === 6;
        const isHoliday = this.isHoliday(dateString);

        if (isHoliday) {
            row.classList.add('holiday-row');
        } else if (isWeekend) {
            row.classList.add('weekend-row');
        }

        // 日期单元格
        const dateCell = document.createElement('td');
        dateCell.className = 'date-cell';
        dateCell.textContent = `${date.getMonth() + 1}/${date.getDate()}`;
        row.appendChild(dateCell);

        // 星期单元格
        const weekdayCell = document.createElement('td');
        weekdayCell.className = 'weekday-cell';
        weekdayCell.textContent = `星期${dayOfWeek}`;
        row.appendChild(weekdayCell);

        // 时段数据
        const timeSlots = [
            '8:00～9:00',
            '9:00～12:00',
            '13:30～18:00',
            '18:00～21:00',
            '8:00～12:00',
            '13:30～17:30',
            '17:30～21:30'
        ];

        timeSlots.forEach(slot => {
            const cell = document.createElement('td');
            cell.className = 'slot-cell';

            if (this.groupedData[dateString] && this.groupedData[dateString][slot]) {
                this.groupedData[dateString][slot].forEach(item => {
                    const staffElement = document.createElement('div');
                    staffElement.className = 'staff-item';
                    staffElement.classList.add(item.core_staff ? 'core-staff' : 'regular-staff');
                    staffElement.textContent = item.staff_name;
                    cell.appendChild(staffElement);
                });
            }

            row.appendChild(cell);
        });
        return row;
    }

    isHoliday(dateString) {
        // 简单判断是否为节假日（可以根据实际的节假日数据判断）
        const holidays = ['2026-02-15', '2026-02-16', '2026-02-17', '2026-02-18', '2026-02-19', '2026-02-20', '2026-02-21', '2026-02-22'];
        return holidays.includes(dateString);
    }
}

document.addEventListener('DOMContentLoaded', function () {
        loadStaffConfig();
        setupEventListeners();

        // 确保导出按钮存在后再绑定
        const exportBtn = document.getElementById('exportScheduleBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', exportSchedule);
        }

        // 初始化日历（如果需要）
        // new RosterCalendar();
    });
