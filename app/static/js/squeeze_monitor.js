// Advanced Squeeze Monitoring System
class SqueezeMonitor {
    constructor() {
        this.watchlist = [];
        this.alerts = [];
        this.priceTargets = {};
        this.soundEnabled = true;
        this.notificationPermission = false;
        this.init();
    }

    init() {
        this.requestNotificationPermission();
        this.loadWatchlist();
        this.startMonitoring();
    }

    requestNotificationPermission() {
        if ('Notification' in window && Notification.permission !== 'granted') {
            Notification.requestPermission().then(permission => {
                this.notificationPermission = permission === 'granted';
            });
        }
    }

    // Advanced watchlist management
    addToWatchlist(ticker, targetScore = 60, priceTarget = null) {
        if (!this.watchlist.find(item => item.ticker === ticker)) {
            const watchItem = {
                ticker: ticker,
                targetScore: targetScore,
                priceTarget: priceTarget,
                addedAt: new Date().toISOString(),
                lastCheck: null,
                lastScore: null,
                triggered: false
            };
            
            this.watchlist.push(watchItem);
            this.saveWatchlist();
            this.showToast(`${ticker} added to watchlist`, 'success');
            return true;
        }
        return false;
    }

    removeFromWatchlist(ticker) {
        this.watchlist = this.watchlist.filter(item => item.ticker !== ticker);
        this.saveWatchlist();
        this.showToast(`${ticker} removed from watchlist`, 'info');
    }

    saveWatchlist() {
        localStorage.setItem('squeezeWatchlist', JSON.stringify(this.watchlist));
    }

    loadWatchlist() {
        const saved = localStorage.getItem('squeezeWatchlist');
        if (saved) {
            this.watchlist = JSON.parse(saved);
        }
    }

    // Real-time monitoring
    async startMonitoring() {
        // Check every minute during market hours
        setInterval(() => {
            const now = new Date();
            const hour = now.getHours();
            const day = now.getDay();
            
            // Only monitor during extended market hours (4 AM - 8 PM ET, Mon-Fri)
            if (day > 0 && day < 6 && hour >= 4 && hour <= 20) {
                this.checkWatchlist();
            }
        }, 60000); // Check every minute
    }

    async checkWatchlist() {
        if (this.watchlist.length === 0) return;
        
        for (const item of this.watchlist) {
            // Skip if already triggered in last hour
            if (item.triggered && 
                new Date() - new Date(item.lastCheck) < 3600000) {
                continue;
            }
            
            try {
                // Simulate API call - replace with actual API
                const score = await this.getSqueezeScore(item.ticker);
                
                item.lastCheck = new Date().toISOString();
                item.lastScore = score;
                
                // Check if alert should trigger
                if (score >= item.targetScore && !item.triggered) {
                    this.triggerAlert(item, score);
                    item.triggered = true;
                } else if (score < item.targetScore - 10) {
                    // Reset trigger if score drops significantly
                    item.triggered = false;
                }
            } catch (error) {
                console.error(`Error checking ${item.ticker}:`, error);
            }
        }
        
        this.saveWatchlist();
        this.updateWatchlistDisplay();
    }

    async getSqueezeScore(ticker) {
        // Simulate score - replace with actual API call
        return Math.random() * 100;
    }

    triggerAlert(item, score) {
        const alert = {
            ticker: item.ticker,
            score: score,
            targetScore: item.targetScore,
            timestamp: new Date().toISOString(),
            type: score >= 80 ? 'critical' : score >= 60 ? 'high' : 'moderate'
        };
        
        this.alerts.push(alert);
        this.saveAlerts();
        
        // Visual notification
        this.showNotification(alert);
        
        // Sound alert
        if (this.soundEnabled) {
            this.playAlertSound(alert.type);
        }
        
        // Browser notification
        if (this.notificationPermission) {
            this.showBrowserNotification(alert);
        }
    }

    showNotification(alert) {
        const alertClass = alert.type === 'critical' ? 'danger' : 
                          alert.type === 'high' ? 'warning' : 'info';
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${alertClass} squeeze-alert`;
        notification.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>🚨 SQUEEZE ALERT: ${alert.ticker}</strong><br>
                    Score: ${alert.score.toFixed(1)} (Target: ${alert.targetScore})
                </div>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        // Add to notifications container
        let container = document.getElementById('alertsContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'alertsContainer';
            container.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto-remove after 30 seconds
        setTimeout(() => {
            notification.remove();
        }, 30000);
    }

    showBrowserNotification(alert) {
        const notification = new Notification(`🚨 Squeeze Alert: ${alert.ticker}`, {
            body: `Score: ${alert.score.toFixed(1)} - Target: ${alert.targetScore}`,
            icon: '/favicon.ico',
            badge: '/favicon.ico',
            vibrate: alert.type === 'critical' ? [200, 100, 200] : [200],
            requireInteraction: alert.type === 'critical'
        });
        
        notification.onclick = () => {
            window.focus();
            notification.close();
        };
    }

    playAlertSound(type) {
        const audio = new Audio();
        
        // Use different sounds for different alert levels
        const sounds = {
            'critical': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBStczPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwhCnODyvmwhBSl+zPDTgjMGHm7A7OOgSwkQVqzn7KxWDwg=',
            'high': 'data:audio/wav;base64,UklGRkQEAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YSAEAAB/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/',
            'moderate': 'data:audio/wav;base64,UklGRjwCAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YRgCAAB/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/f39/'
        };
        
        audio.src = sounds[type] || sounds['moderate'];
        audio.play().catch(e => console.log('Audio play failed:', e));
    }

    saveAlerts() {
        // Keep only last 100 alerts
        if (this.alerts.length > 100) {
            this.alerts = this.alerts.slice(-100);
        }
        localStorage.setItem('squeezeAlerts', JSON.stringify(this.alerts));
    }

    loadAlerts() {
        const saved = localStorage.getItem('squeezeAlerts');
        if (saved) {
            this.alerts = JSON.parse(saved);
        }
    }

    updateWatchlistDisplay() {
        const container = document.getElementById('watchlistDisplay');
        if (!container) return;
        
        if (this.watchlist.length === 0) {
            container.innerHTML = '<p class="text-muted">No tickers in watchlist</p>';
            return;
        }
        
        let html = '<div class="watchlist-items">';
        this.watchlist.forEach(item => {
            const scoreClass = item.lastScore >= 80 ? 'text-danger' :
                              item.lastScore >= 60 ? 'text-warning' :
                              item.lastScore >= 40 ? 'text-info' : 'text-muted';
            
            html += `
                <div class="watchlist-item mb-2 p-2 border rounded">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold">${item.ticker}</span>
                        <span class="${scoreClass}">
                            ${item.lastScore ? item.lastScore.toFixed(1) : '-'}
                        </span>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="squeezeMonitor.removeFromWatchlist('${item.ticker}')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <small class="text-muted">
                        Target: ${item.targetScore} | 
                        Last: ${item.lastCheck ? new Date(item.lastCheck).toLocaleTimeString() : 'Never'}
                    </small>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 24px;
            background: ${type === 'success' ? '#00ff88' : 
                         type === 'danger' ? '#ff6b6b' : '#00d4ff'};
            color: ${type === 'success' || type === 'danger' ? '#000' : '#fff'};
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10001;
            animation: slideInUp 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutDown 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Export alerts history
    exportAlerts() {
        if (this.alerts.length === 0) {
            this.showToast('No alerts to export', 'warning');
            return;
        }
        
        let csv = 'Ticker,Score,Target Score,Type,Timestamp\\n';
        this.alerts.forEach(alert => {
            csv += `${alert.ticker},${alert.score},${alert.targetScore},${alert.type},${alert.timestamp}\\n`;
        });
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `squeeze_alerts_${new Date().toISOString().slice(0,10)}.csv`;
        a.click();
        
        this.showToast('Alerts exported successfully', 'success');
    }

    // Settings management
    toggleSound() {
        this.soundEnabled = !this.soundEnabled;
        localStorage.setItem('squeezeSoundEnabled', this.soundEnabled);
        this.showToast(`Sound alerts ${this.soundEnabled ? 'enabled' : 'disabled'}`, 'info');
    }

    clearAllAlerts() {
        this.alerts = [];
        this.saveAlerts();
        this.showToast('All alerts cleared', 'info');
    }
}

// Initialize monitor
let squeezeMonitor;
document.addEventListener('DOMContentLoaded', function() {
    squeezeMonitor = new SqueezeMonitor();
});

// CSS for animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInUp {
        from {
            transform: translateY(100px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutDown {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(100px);
            opacity: 0;
        }
    }
    
    .squeeze-alert {
        margin-bottom: 10px;
        animation: slideInUp 0.3s ease;
    }
    
    .watchlist-item {
        background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
        transition: all 0.3s ease;
    }
    
    .watchlist-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(100, 200, 255, 0.2);
    }
`;
document.head.appendChild(style);
