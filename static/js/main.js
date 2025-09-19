// NFL Predictions Website JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds (except result alerts)
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-success):not(.result-alert)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Score input validation
    const scoreInputs = document.querySelectorAll('input[type="number"]');
    scoreInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) this.value = 0;
            if (this.value > 100) this.value = 100;
        });
    });

    // Week navigation smooth scrolling
    const weekLinks = document.querySelectorAll('.pagination .page-link');
    weekLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Add loading state
            const loadingSpinner = document.createElement('span');
            loadingSpinner.className = 'loading me-2';
            this.prepend(loadingSpinner);
        });
    });

    // Copy prediction text functionality
    const copyButtons = document.querySelectorAll('.copy-prediction');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const gameCard = this.closest('.card');
            const gameText = gameCard.querySelector('.game-text');
            
            if (gameText) {
                navigator.clipboard.writeText(gameText.textContent).then(function() {
                    // Show success feedback
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
                    button.classList.add('btn-success');
                    button.classList.remove('btn-outline-secondary');
                    
                    setTimeout(function() {
                        button.innerHTML = originalText;
                        button.classList.remove('btn-success');
                        button.classList.add('btn-outline-secondary');
                    }, 2000);
                });
            }
        });
    });

    // Auto-refresh for pending games (if needed)
    const pendingGames = document.querySelectorAll('.badge.bg-warning');
    if (pendingGames.length > 0) {
        // Check if we should auto-refresh (e.g., on game day)
        const now = new Date();
        const dayOfWeek = now.getDay(); // 0 = Sunday, 1 = Monday, etc.
        
        // Auto-refresh every 5 minutes on Sundays (game day)
        if (dayOfWeek === 0) {
            setInterval(function() {
                location.reload();
            }, 300000); // 5 minutes
        }
    }

    // Statistics chart (if Chart.js is available)
    if (typeof Chart !== 'undefined') {
        const ctx = document.getElementById('accuracyChart');
        if (ctx) {
            const weeklyData = JSON.parse(ctx.dataset.weekly || '{}');
            const weeks = Object.keys(weeklyData).sort((a, b) => parseInt(a) - parseInt(b));
            const accuracies = weeks.map(week => {
                const stats = weeklyData[week];
                return (stats.correct / stats.total) * 100;
            });

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: weeks.map(w => `Week ${w}`),
                    datasets: [{
                        label: 'Accuracy %',
                        data: accuracies,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }
});

// Utility functions
function formatConfidence(confidence) {
    return (confidence * 100).toFixed(1) + '%';
}

function formatInjuryReport(injuries) {
    if (!injuries || injuries.length === 0) {
        return 'Both teams healthy';
    }
    return injuries.join(', ');
}

// Export functions for potential use in templates
window.NFLPredictions = {
    formatConfidence: formatConfidence,
    formatInjuryReport: formatInjuryReport
};
