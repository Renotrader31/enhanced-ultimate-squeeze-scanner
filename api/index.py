from flask import Flask, request, jsonify
import json
import urllib.request
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><title>Enhanced Squeeze Scanner v2.0</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:Arial,sans-serif;margin:0;padding:20px;background:linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#334155 100%);color:white;min-height:100vh}
.container{max-width:1200px;margin:0 auto;background:rgba(15,23,42,0.9);border-radius:15px;padding:30px;box-shadow:0 25px 50px rgba(0,0,0,0.3)}
.header{text-align:center;margin-bottom:30px}
.header h1{font-size:2.5em;margin:0 0 10px 0;color:#60a5fa}
.header p{color:#94a3b8;font-size:1.1em}
.main{display:grid;grid-template-columns:1fr 2fr;gap:30px}
.form-panel{background:rgba(30,41,59,0.6);border-radius:10px;padding:25px;border:1px solid rgba(255,255,255,0.1)}
.form-group{margin-bottom:20px}
.form-group label{display:block;margin-bottom:8px;color:#cbd5e1;font-weight:500}
.form-group input,.form-group textarea{width:100%;padding:12px;border:1px solid rgba(255,255,255,0.2);border-radius:8px;background:rgba(51,65,85,0.8);color:white;font-size:14px}
.form-group input:focus,.form-group textarea:focus{outline:none;border-color:#3b82f6;box-shadow:0 0 0 2px rgba(59,130,246,0.2)}
.scan-btn{width:100%;padding:15px;background:linear-gradient(135deg,#059669,#10b981);border:none;border-radius:8px;color:white;font-size:16px;font-weight:600;cursor:pointer;transition:all 0.3s}
.scan-btn:hover{transform:translateY(-2px);box-shadow:0 8px 25px rgba(16,185,129,0.3)}
.scan-btn:disabled{opacity:0.6;cursor:not-allowed;transform:none}
.results-panel{background:rgba(30,41,59,0.6);border-radius:10px;padding:25px;border:1px solid rgba(255,255,255,0.1)}
.results-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.results-header h3{margin:0;color:#60a5fa;font-size:1.3em}
.status{padding:6px 12px;border-radius:15px;font-size:12px;font-weight:600;text-transform:uppercase}
.status.ready{background:rgba(16,185,129,0.2);color:#10b981}
.status.scanning{background:rgba(245,158,11,0.2);color:#f59e0b}
.status.complete{background:rgba(59,130,246,0.2);color:#3b82f6}
.results{max-height:500px;overflow-y:auto}
.stock-card{background:rgba(51,65,85,0.4);border:1px solid rgba(255,255,255,0.1);border-radius:10px;padding:20px;margin-bottom:15px;transition:all 0.3s}
.stock-card:hover{transform:translateY(-2px);border-color:rgba(59,130,246,0.3);box-shadow:0 8px 25px rgba(0,0,0,0.2)}
.stock-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px}
.ticker{font-size:1.4em;font-weight:700;color:#f1f5f9}
.score{padding:6px 12px;border-radius:15px;font-weight:700;font-size:14px}
.score.high{background:linear-gradient(135deg,#dc2626,#ef4444);color:white}
.score.medium{background:linear-gradient(135deg,#ea580c,#f97316);color:white}
.score.low{background:linear-gradient(135deg,#65a30d,#84cc16);color:white}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-top:10px}
.metric{text-align:center;padding:10px;background:rgba(71,85,105,0.3);border-radius:8px}
.metric-label{font-size:11px;color:#94a3b8;text-transform:uppercase;font-weight:600}
.metric-value{font-size:14px;font-weight:700;color:#f1f5f9;margin-top:4px}
.loading{text-align:center;color:#94a3b8;padding:40px;font-style:italic}
.error{background:rgba(220,38,38,0.1);border:1px solid rgba(220,38,38,0.2);color:#fca5a5;padding:15px;border-radius:8px}
@media(max-width:768px){.main{grid-template-columns:1fr}.header h1{font-size:2em}.metrics{grid-template-columns:repeat(2,1fr)}}
</style>
</head><body>
<div class="container">
<div class="header">
<h1>🚀 Enhanced Ultimate Squeeze Scanner v2.0</h1>
<p>Professional-Grade Short Squeeze Analysis with Real-Time Ortex Integration</p>
</div>
<div class="main">
<div class="form-panel">
<h3 style="color:#60a5fa;margin-bottom:20px">📊 Configuration Panel</h3>
<div class="form-group">
<label for="key">Ortex API Key</label>
<input type="password" id="key" placeholder="Enter your Ortex API key..." autocomplete="off">
</div>
<div class="form-group">
<label for="tickers">Stock Tickers</label>
<textarea id="tickers" rows="3" placeholder="GME, AMC, TSLA, BBBY, APE">GME,AMC,TSLA</textarea>
</div>
<button class="scan-btn" onclick="scan()">🔍 Start Enhanced Squeeze Scan</button>
</div>
<div class="results-panel">
<div class="results-header">
<h3>📈 Live Squeeze Analysis</h3>
<span class="status ready" id="status">Ready</span>
</div>
<div class="results" id="results">
<div class="loading">Ready to scan for squeeze opportunities...<br><small>Enter your Ortex API key and click scan to begin</small></div>
</div>
</div>
</div>
</div>
<script>
let scanning = false;
function updateStatus(text, className) {
    const status = document.getElementById('status');
    status.textContent = text;
    status.className = 'status ' + className;
}
async function scan() {
    if (scanning) return;
    const key = document.getElementById('key').value;
    const tickers = document.getElementById('tickers').value;
    if (!key) { alert('Please enter your Ortex API key'); return; }
    
    scanning = true;
    updateStatus('Scanning...', 'scanning');
    const btn = document.querySelector('.scan-btn');
    btn.disabled = true;
    btn.textContent = '🔄 Scanning in progress...';
    
    document.getElementById('results').innerHTML = '<div class="loading">🔍 Performing enhanced squeeze analysis...<br><small>Fetching real-time Ortex data and calculating squeeze metrics</small></div>';
    
    try {
        const r = await fetch('/api/scan', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ortex_key: key, tickers: tickers})
        });
        const d = await r.json();
        
        if (d.success) {
            let html = '';
            d.results.forEach(x => {
                const priceColor = x.price_change_pct >= 0 ? '#10b981' : '#ef4444';
                const pricePrefix = x.price_change_pct >= 0 ? '+' : '';
                const scoreClass = x.squeeze_score >= 60 ? 'high' : x.squeeze_score >= 30 ? 'medium' : 'low';
                const scoreText = x.squeeze_score >= 60 ? 'HIGH SQUEEZE RISK' : x.squeeze_score >= 30 ? 'MODERATE RISK' : 'Low Risk';
                
                html += `<div class="stock-card">
                    <div class="stock-header">
                        <div class="ticker">${x.ticker}</div>
                        <div class="score ${scoreClass}">${x.squeeze_score}/100 - ${scoreText}</div>
                    </div>
                    <div style="display:flex;justify-content:space-between;margin-bottom:15px">
                        <div style="font-size:1.2em;font-weight:600">$${x.current_price}</div>
                        <div style="color:${priceColor};font-weight:600">${pricePrefix}${x.price_change_pct}%</div>
                    </div>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-label">Short Interest</div>
                            <div class="metric-value">${x.ortex_data.short_interest}%</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Score</div>
                            <div class="metric-value">${x.squeeze_score}/100</div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Status</div>
                            <div class="metric-value">${x.success ? '✅' : '❌'}</div>
                        </div>
                    </div>
                </div>`;
            });
            document.getElementById('results').innerHTML = html;
            updateStatus('Scan Complete', 'complete');
        } else {
            document.getElementById('results').innerHTML = '<div class="error">Error: ' + d.error + '</div>';
            updateStatus('Scan Failed', 'ready');
        }
    } catch (e) {
        document.getElementById('results').innerHTML = '<div class="error">Network error: ' + e.message + '</div>';
        updateStatus('Network Error', 'ready');
    } finally {
        scanning = false;
        btn.disabled = false;
        btn.textContent = '🔍 Start Enhanced Squeeze Scan';
    }
}
// Auto-save API key
document.getElementById('key').addEventListener('input', e => localStorage.setItem('ortex_key', e.target.value));
window.addEventListener('load', () => {
    const saved = localStorage.getItem('ortex_key');
    if (saved) document.getElementById('key').value = saved;
});
</script>
</body></html>'''

@app.route('/api/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json() or {}
        ortex_key = data.get('ortex_key', '')
        tickers_input = data.get('tickers', 'GME,AMC,TSLA')
        
        if not ortex_key:
            return jsonify({'success': False, 'error': 'Ortex API key required'})
        
        tickers = [t.strip().upper() for t in tickers_input.replace(',', ' ').split() if t.strip()]
        tickers = tickers[:10]  # Increased limit
        
        results = []
        total_credits = 0
        
        for ticker in tickers:
            try:
                # Enhanced Yahoo Finance price fetch
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (compatible; EnhancedSqueezeScanner/2.0)')
                
                current_price = 0
                price_change_pct = 0
                volume = 0
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    price_data = json.loads(response.read())
                    
                    if 'chart' in price_data and price_data['chart']['result']:
                        meta = price_data['chart']['result'][0]['meta']
                        current_price = meta.get('regularMarketPrice', 0)
                        previous_close = meta.get('previousClose', 0)
                        volume = meta.get('regularMarketVolume', 0)
                        price_change = current_price - previous_close if previous_close else 0
                        price_change_pct = (price_change / previous_close * 100) if previous_close else 0
                
                # Enhanced Ortex fetch with multiple endpoints
                short_interest = 0
                cost_to_borrow = 0
                days_to_cover = 0
                credits_used = 0
                data_sources = []
                
                # Try multiple Ortex endpoints
                ortex_endpoints = [
                    f"https://api.ortex.com/api/v1/stock/us/{ticker}/short_interest?format=json",
                    f"https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/short_interest",
                ]
                
                for endpoint in ortex_endpoints:
                    try:
                        ortex_req = urllib.request.Request(endpoint)
                        ortex_req.add_header('Ortex-Api-Key', ortex_key)
                        ortex_req.add_header('User-Agent', 'Enhanced-Ultimate-Squeeze-Scanner/2.0')
                        
                        with urllib.request.urlopen(ortex_req, timeout=8) as ortex_response:
                            if ortex_response.getcode() == 200:
                                ortex_data = json.loads(ortex_response.read())
                                if 'rows' in ortex_data and ortex_data['rows']:
                                    row = ortex_data['rows'][0]
                                    short_interest = row.get('shortInterestPcFreeFloat', 0)
                                    credits_used += ortex_data.get('creditsUsed', 0)
                                    data_sources.append('ortex_si')
                                    break
                    except:
                        continue
                
                # Try cost to borrow endpoint
                try:
                    ctb_req = urllib.request.Request(f"https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/ctb/new")
                    ctb_req.add_header('Ortex-Api-Key', ortex_key)
                    with urllib.request.urlopen(ctb_req, timeout=5) as ctb_response:
                        ctb_data = json.loads(ctb_response.read())
                        if 'rows' in ctb_data and ctb_data['rows']:
                            cost_to_borrow = ctb_data['rows'][0].get('costToBorrow', 0)
                            credits_used += ctb_data.get('creditsUsed', 0)
                            data_sources.append('ortex_ctb')
                except:
                    pass
                
                # Enhanced squeeze score calculation
                score = 0
                score += min(short_interest * 1.5, 40)  # Short Interest (0-40 points)
                score += min(cost_to_borrow * 1.2, 25)  # Cost to Borrow (0-25 points)
                score += min(max(0, price_change_pct) * 0.8, 15)  # Price momentum (0-15 points)
                
                squeeze_score = min(int(score), 100)
                total_credits += credits_used
                
                # Determine risk classification
                if squeeze_score >= 80:
                    risk_type = "EXTREME SQUEEZE RISK"
                elif squeeze_score >= 60:
                    risk_type = "HIGH SQUEEZE RISK"
                elif squeeze_score >= 40:
                    risk_type = "MODERATE SQUEEZE RISK"
                else:
                    risk_type = "Low Risk"
                
                results.append({
                    'ticker': ticker,
                    'current_price': round(current_price, 2),
                    'price_change_pct': round(price_change_pct, 2),
                    'volume': volume,
                    'squeeze_score': squeeze_score,
                    'squeeze_type': risk_type,
                    'ortex_data': {
                        'short_interest': round(short_interest, 2),
                        'cost_to_borrow': round(cost_to_borrow, 2),
                        'days_to_cover': round(days_to_cover, 2),
                        'data_sources': data_sources
                    },
                    'credits_used': credits_used,
                    'success': True
                })
                        
            except Exception as e:
                results.append({
                    'ticker': ticker,
                    'squeeze_score': 0,
                    'current_price': 0,
                    'price_change_pct': 0,
                    'volume': 0,
                    'squeeze_type': 'Error',
                    'ortex_data': {
                        'short_interest': 0,
                        'cost_to_borrow': 0,
                        'days_to_cover': 0,
                        'data_sources': []
                    },
                    'credits_used': 0,
                    'success': False
                })
        
        # Sort by squeeze score
        results.sort(key=lambda x: x['squeeze_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'results': results,
            'total_tickers': len(results),
            'high_risk_count': len([r for r in results if r['squeeze_score'] >= 60]),
            'total_credits_used': total_credits,
            'scan_timestamp': datetime.now().isoformat(),
            'message': f'Enhanced squeeze scan complete - {len(results)} tickers analyzed'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api')
def api_info():
    return jsonify({
        'status': 'healthy',
        'version': 'enhanced_v2.0',
        'endpoints': {
            '/': 'Enhanced Professional Homepage', 
            '/api/scan': 'Enhanced Squeeze Scan Endpoint',
            '/api': 'API Information'
        },
        'features': [
            'Enhanced Ortex integration (multiple endpoints)',
            'Real-time Yahoo Finance price data',
            'Advanced squeeze scoring algorithm',
            'Professional responsive UI',
            'Risk classification system',
            'Auto-save API key functionality'
        ],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
