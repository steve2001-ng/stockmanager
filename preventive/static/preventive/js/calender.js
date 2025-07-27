document.addEventListener('DOMContentLoaded', function() {
    // Navigation du calendrier
    const prevWeekBtn = document.getElementById('prev-week');
    const nextWeekBtn = document.getElementById('next-week');
    
    if (prevWeekBtn && nextWeekBtn) {
        prevWeekBtn.addEventListener('click', function() {
            const currentDate = new Date(this.dataset.currentDate);
            const prevWeek = new Date(currentDate.setDate(currentDate.getDate() - 7));
            window.location.href = `?date=${prevWeek.toISOString().split('T')[0]}`;
        });
        
        nextWeekBtn.addEventListener('click', function() {
            const currentDate = new Date(this.dataset.currentDate);
            const nextWeek = new Date(currentDate.setDate(currentDate.getDate() + 7));
            window.location.href = `?date=${nextWeek.toISOString().split('T')[0]}`;
        });
    }
    
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});