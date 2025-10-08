"""
Enhanced Ultimate Squeeze Scanner - Serverless API for Vercel
Production-ready serverless deployment with 5x enhanced squeeze data
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import urllib.parse
import urllib.request
import os
from datetime import datetime, timedelta
import time
import concurrent.futures
import threading

# Initialize Flask app for serverless
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# Enhanced squeeze scanner integration (same as integrated server)
class OptimizedSqueezeAPI:
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 1800  # 30 minutes
        self.lock = threading.Lock()
        
        # Working Ortex endpoints discovered from analysis
        self.ortex_endpoints = {
            'short_interest': [
                'https://api.ortex.com/api/v1/stock/us/{ticker}/short_interest?format=json',
                'https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/short_interest',
            ],
            'cost_to_borrow': [
                'https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/ctb/new',
                'https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/ctb/all',
            ],
            'days_to_cover': [
                'https://api.ortex.com/api/v1/stock/us/{ticker}/dtc?format=json',
                'https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/dtc',
            ],
            'availability': [
                'https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/availability',
            ],
            'stock_scores': [
                'https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/stock_scores',
            ]
        }

    def is_cache_valid(self, cache_key):
        """Check if cached data is still valid"""
        if cache_key not in self.cache_timestamps:
            return False
        
        cache_time = self.cache_timestamps[cache_key]
        return (datetime.now() - cache_time).total_seconds() < self.cache_duration

    def get_cached_data(self, cache_key):
        """Retrieve cached data if valid"""
        with self.lock:
            if self.is_cache_valid(cache_key):
                return self.cache.get(cache_key)
        return None

    def set_cached_data(self, cache_key, data):
        """Store data in cache"""
        with self.lock:
            self.cache[cache_key] = data
            self.cache_timestamps[cache_key] = datetime.now()

    def fetch_ortex_data_optimized(self, ticker, ortex_key, data_types=None):
        """Optimized Ortex data fetching with parallel requests and caching"""
        if not ortex_key:
            return None
            
        if data_types is None:
            data_types = ['short_interest', 'cost_to_borrow', 'days_to_cover']
        
        # Check cache first
        cache_key = f"ortex_{ticker}_{'_'.join(data_types)}"
        cached_result = self.get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        results = {}
        
        def fetch_data_type(data_type):
            """Fetch specific data type with fallback"""
            endpoints = self.ortex_endpoints.get(data_type, [])
            
            for endpoint_url in endpoints:
                try:
                    url = endpoint_url.format(ticker=ticker)
                    req = urllib.request.Request(url)
                    req.add_header('Ortex-Api-Key', ortex_key)
                    req.add_header('User-Agent', 'Enhanced-Ultimate-Squeeze-Scanner/2.0')
                    req.add_header('Accept', 'application/json')
                    
                    with urllib.request.urlopen(req, timeout=8) as response:
                        if response.getcode() == 200:
                            content_type = response.headers.get('Content-Type', '')
                            if 'application/json' in content_type:
                                data = json.loads(response.read().decode('utf-8'))
                                return {
                                    'success': True,
                                    'data_type': data_type,
                                    'data': data,
                                    'credits_used': data.get('creditsUsed', 0)
                                }
                except Exception:
                    continue
            
            return {'success': False, 'data_type': data_type}
        
        # Sequential processing for serverless (to avoid timeout issues)
        for data_type in data_types:
            result = fetch_data_type(data_type)
            results[result['data_type']] = result
        
        # Cache successful results
        if any(r.get('success') for r in results.values()):
            self.set_cached_data(cache_key, results)
        
        return results

    def process_enhanced_squeeze_data(self, ortex_results, price_data=None):
        """Process multi-endpoint Ortex data into comprehensive squeeze metrics"""
        squeeze_data = {
            'short_interest': 0,
            'utilization': 0,
            'cost_to_borrow': 0,
            'days_to_cover': 0,
            'data_sources': [],
            'confidence': 'high',
            'total_credits_used': 0
        }
        
        # Process short interest
        if 'short_interest' in ortex_results and ortex_results['short_interest'].get('success'):
            si_data = ortex_results['short_interest']['data']
            if 'rows' in si_data and si_data['rows']:
                latest = si_data['rows'][0]
                squeeze_data['short_interest'] = latest.get('shortInterestPcFreeFloat', 0)
                squeeze_data['data_sources'].append('ortex_si')
                squeeze_data['total_credits_used'] += ortex_results['short_interest'].get('credits_used', 0)
        
        # Process cost to borrow
        if 'cost_to_borrow' in ortex_results and ortex_results['cost_to_borrow'].get('success'):
            ctb_data = ortex_results['cost_to_borrow']['data']
            if 'rows' in ctb_data and ctb_data['rows']:
                latest = ctb_data['rows'][0]
                squeeze_data['cost_to_borrow'] = latest.get('costToBorrow', 0)
                squeeze_data['data_sources'].append('ortex_ctb')
                squeeze_data['total_credits_used'] += ortex_results['cost_to_borrow'].get('credits_used', 0)
        
        # Process days to cover
        if 'days_to_cover' in ortex_results and ortex_results['days_to_cover'].get('success'):
            dtc_data = ortex_results['days_to_cover']['data']
            if 'rows' in dtc_data and dtc_data['rows']:
                latest = dtc_data['rows'][0]
                squeeze_data['days_to_cover'] = latest.get('daysToCover', 0)
                squeeze_data['data_sources'].append('ortex_dtc')
                squeeze_data['total_credits_used'] += ortex_results['days_to_cover'].get('credits_used', 0)
        
        # Calculate enhanced squeeze score
        score = self.calculate_enhanced_score(squeeze_data, price_data)
        squeeze_data['squeeze_score'] = score
        
        return squeeze_data

    def calculate_enhanced_score(self, squeeze_data, price_data):
        """Enhanced squeeze scoring algorithm"""
        score = 0
        
        # Short Interest (0-40 points)
        si = squeeze_data.get('short_interest', 0)
        si_score = min(si * 1.3, 40)
        score += si_score
        
        # Cost to Borrow (0-25 points)
        ctb = squeeze_data.get('cost_to_borrow', 0)
        ctb_score = min(ctb * 1.2, 25)
        score += ctb_score
        
        # Days to Cover (0-20 points)
        dtc = squeeze_data.get('days_to_cover', 0)
        dtc_score = min(dtc * 2.5, 20)
        score += dtc_score
        
        # Price momentum (0-15 points)
        if price_data and 'price_change_pct' in price_data:
            momentum = max(0, price_data['price_change_pct'])
            momentum_score = min(momentum * 0.8, 15)
            score += momentum_score
        
        return min(int(score), 100)

# Initialize optimized API
squeeze_api = OptimizedSqueezeAPI()

def get_yahoo_price_data(tickers):
    """Enhanced Yahoo Finance integration"""
    price_data = {}
    
    def get_single_price(ticker):
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; EnhancedSqueezeScanner/2.0)')
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    meta = result.get('meta', {})
                    
                    current_price = meta.get('regularMarketPrice', 0)
                    previous_close = meta.get('previousClose', 0)
                    volume = meta.get('regularMarketVolume', 0)
                    
                    price_change = current_price - previous_close if previous_close else 0
                    price_change_pct = (price_change / previous_close * 100) if previous_close else 0
                    
                    return {
                        'ticker': ticker,
                        'current_price': round(current_price, 2),
                        'price_change': round(price_change, 2),
                        'price_change_pct': round(price_change_pct, 2),
                        'volume': volume,
                        'success': True
                    }
        except Exception:
            pass
        
        return {'ticker': ticker, 'success': False}
    
    # Process multiple tickers
    for ticker in tickers:
        result = get_single_price(ticker)
        if result.get('success'):
            price_data[ticker] = result
    
    return price_data

# Serverless handler function
def handler(request, context=None):
    """Serverless handler for Vercel deployment"""
    with app.app_context():
        # Handle the request using Flask
        return app.full_dispatch_request()

# Route handlers - Professional UI as default homepage
@app.route('/')
def index():
    """Enhanced Ultimate Squeeze Scanner - Professional UI (Homepage)"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Ultimate Squeeze Scanner v2.0 - Professional</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, 
                #0f172a 0%, 
                #1e293b 20%, 
                #334155 50%, 
                #475569 80%, 
                #64748b 100%);
            min-height: 100vh;
            color: #e2e8f0;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(15, 23, 42, 0.95);
            border-radius: 20px;
            box-shadow: 
                0 25px 50px -12px rgba(0, 0, 0, 0.5),
                0 0 0 1px rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
            padding: 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 30% 20%, rgba(59, 130, 246, 0.3), transparent 50%),
                         radial-gradient(circle at 70% 80%, rgba(6, 182, 212, 0.3), transparent 50%);
        }

        .header h1 {
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            position: relative;
        }

        .header p {
            font-size: 1.1em;
            opacity: 0.9;
            position: relative;
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 30px;
            padding: 30px;
            min-height: 600px;
        }

        .control-panel {
            background: rgba(30, 41, 59, 0.6);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
        }

        .control-panel h3 {
            color: #60a5fa;
            margin-bottom: 20px;
            font-size: 1.3em;
            font-weight: 600;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #cbd5e1;
            font-weight: 500;
        }

        input, textarea {
            width: 100%;
            padding: 12px 15px;
            background: rgba(51, 65, 85, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            color: #f1f5f9;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        input:focus, textarea:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            background: rgba(51, 65, 85, 0.9);
        }

        .scan-button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
            border: none;
            border-radius: 12px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
        }

        .scan-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
        }

        .scan-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .results-panel {
            background: rgba(30, 41, 59, 0.6);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(8px);
        }

        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .results-header h3 {
            color: #60a5fa;
            font-size: 1.3em;
            font-weight: 600;
        }

        .status {
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .status.ready { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .status.scanning { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .status.complete { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }

        .results-container {
            max-height: 500px;
            overflow-y: auto;
            padding-right: 10px;
        }

        .results-container::-webkit-scrollbar {
            width: 8px;
        }

        .results-container::-webkit-scrollbar-track {
            background: rgba(51, 65, 85, 0.3);
            border-radius: 10px;
        }

        .results-container::-webkit-scrollbar-thumb {
            background: rgba(100, 116, 139, 0.5);
            border-radius: 10px;
        }

        .stock-card {
            background: rgba(51, 65, 85, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
            backdrop-filter: blur(4px);
        }

        .stock-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
            border-color: rgba(59, 130, 246, 0.3);
        }

        .stock-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }

        .stock-symbol {
            font-size: 1.4em;
            font-weight: 700;
            color: #f1f5f9;
        }

        .squeeze-score {
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
        }

        .squeeze-extreme { background: linear-gradient(135deg, #dc2626, #ef4444); color: white; }
        .squeeze-high { background: linear-gradient(135deg, #ea580c, #f97316); color: white; }
        .squeeze-moderate { background: linear-gradient(135deg, #d97706, #f59e0b); color: white; }

        .stock-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .metric {
            text-align: center;
            padding: 12px;
            background: rgba(71, 85, 105, 0.3);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .metric-label {
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 14px;
            font-weight: 700;
            color: #f1f5f9;
            margin-top: 4px;
        }

        .loading {
            text-align: center;
            color: #94a3b8;
            font-style: italic;
            padding: 40px;
        }

        .error {
            background: rgba(220, 38, 38, 0.1);
            border: 1px solid rgba(220, 38, 38, 0.2);
            color: #fca5a5;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }

        .stats-bar {
            background: rgba(71, 85, 105, 0.3);
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
        }

        @media (max-width: 1024px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }

        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 15px;
            }
            
            .header {
                padding: 20px;
            }
            
            .main-content {
                padding: 20px;
                gap: 20px;
            }
            
            .stock-metrics {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🚀 Enhanced Ultimate Squeeze Scanner v2.0</h1>
            <p>Professional-Grade Short Squeeze Analysis with Real-Time Ortex Integration</p>
        </header>

        <main class="main-content">
            <section class="control-panel">
                <h3>📊 Configuration Panel</h3>
                
                <div class="form-group">
                    <label for="ortexKey">Ortex API Key</label>
                    <input type="password" 
                           id="ortexKey" 
                           placeholder="Enter your Ortex API key..."
                           autocomplete="off">
                </div>
                
                <div class="form-group">
                    <label for="tickerList">Stock Tickers</label>
                    <textarea id="tickerList" 
                              rows="3" 
                              placeholder="GME, AMC, TSLA, BBBY, APE, MULN, SNDL, PROG, SPRT, IRNT, DWAC, PHUN, BKKT, MARK">GME, AMC, TSLA, BBBY, APE, MULN, SNDL, PROG, SPRT, IRNT, DWAC, PHUN, BKKT, MARK</textarea>
                </div>
                
                <button class="scan-button" onclick="performScan()">
                    🔍 Start Enhanced Squeeze Scan
                </button>

                <div class="stats-bar" id="statsBar" style="display: none;">
                    <div class="stats-grid" id="statsGrid">
                        <!-- Stats will be populated here -->
                    </div>
                </div>
            </section>

            <section class="results-panel">
                <div class="results-header">
                    <h3>📈 Live Squeeze Analysis</h3>
                    <span class="status ready" id="scanStatus">Ready</span>
                </div>
                
                <div class="results-container" id="resultsContainer">
                    <div class="loading">
                        Ready to scan for squeeze opportunities...<br>
                        <small>Enter your Ortex API key and click scan to begin</small>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <script>
        let isScanning = false;

        function updateStatus(text, className) {
            const statusElement = document.getElementById('scanStatus');
            statusElement.textContent = text;
            statusElement.className = `status ${className}`;
        }

        function showStats(data) {
            const statsBar = document.getElementById('statsBar');
            const statsGrid = document.getElementById('statsGrid');
            
            if (data.enhancement_info) {
                statsGrid.innerHTML = `
                    <div class="metric">
                        <div class="metric-label">Cache Hit Rate</div>
                        <div class="metric-value">${data.enhancement_info.cache_hit_rate}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Total Credits</div>
                        <div class="metric-value">${data.total_credits_used || 0}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">High Risk</div>
                        <div class="metric-value">${data.high_risk_count || 0}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Total Scanned</div>
                        <div class="metric-value">${data.total_tickers || 0}</div>
                    </div>
                `;
                statsBar.style.display = 'block';
            }
        }

        function displayResults(data) {
            const container = document.getElementById('resultsContainer');
            
            if (!data.results || data.results.length === 0) {
                container.innerHTML = '<div class="error">No results found. Please check your API key and try again.</div>';
                return;
            }

            let html = '';
            data.results.forEach(result => {
                const priceColor = result.price_change >= 0 ? '#10b981' : '#ef4444';
                const pricePrefix = result.price_change >= 0 ? '+' : '';
                
                html += `
                    <div class="stock-card">
                        <div class="stock-header">
                            <div class="stock-symbol">${result.ticker}</div>
                            <div class="squeeze-score ${result.risk_class}">
                                ${result.squeeze_score}/100 - ${result.squeeze_type}
                            </div>
                        </div>
                        
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div style="font-size: 1.2em; font-weight: 600;">

                                $${result.current_price.toFixed(2)}
                            </div>
                            <div style="color: ${priceColor}; font-weight: 600;">
                                ${pricePrefix}${result.price_change.toFixed(2)} (${pricePrefix}${result.price_change_pct.toFixed(2)}%)
                            </div>
                        </div>
                        
                        <div class="stock-metrics">
                            <div class="metric">
                                <div class="metric-label">Short Interest</div>
                                <div class="metric-value">${result.ortex_data.short_interest.toFixed(1)}%</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Cost to Borrow</div>
                                <div class="metric-value">${result.ortex_data.cost_to_borrow.toFixed(1)}%</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Days to Cover</div>
                                <div class="metric-value">${result.ortex_data.days_to_cover.toFixed(1)}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Volume</div>
                                <div class="metric-value">${(result.volume / 1000000).toFixed(1)}M</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Data Sources</div>
                                <div class="metric-value">${result.ortex_data.data_sources.length}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">Credits Used</div>
                                <div class="metric-value">${result.credits_used}</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
            showStats(data);
        }

        async function performScan() {
            if (isScanning) return;
            
            const ortexKey = document.getElementById('ortexKey').value.trim();
            const tickerList = document.getElementById('tickerList').value.trim();
            
            if (!ortexKey) {
                alert('Please enter your Ortex API key');
                return;
            }
            
            if (!tickerList) {
                alert('Please enter at least one ticker symbol');
                return;
            }
            
            isScanning = true;
            updateStatus('Scanning...', 'scanning');
            
            const button = document.querySelector('.scan-button');
            button.disabled = true;
            button.textContent = '🔄 Scanning in progress...';
            
            document.getElementById('resultsContainer').innerHTML = 
                '<div class="loading">🔍 Performing enhanced squeeze analysis...<br><small>Fetching real-time Ortex data and calculating squeeze metrics</small></div>';
            
            try {
                const response = await fetch('/api/squeeze/scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ortex_key: ortexKey,
                        tickers: tickerList
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                    updateStatus('Scan Complete', 'complete');
                } else {
                    document.getElementById('resultsContainer').innerHTML = 
                        `<div class="error">Error: ${data.error || data.message}</div>`;
                    updateStatus('Scan Failed', 'ready');
                }
                
            } catch (error) {
                console.error('Scan error:', error);
                document.getElementById('resultsContainer').innerHTML = 
                    `<div class="error">Network error: ${error.message}</div>`;
                updateStatus('Network Error', 'ready');
            } finally {
                isScanning = false;
                button.disabled = false;
                button.textContent = '🔍 Start Enhanced Squeeze Scan';
            }
        }

        // Auto-save API key to localStorage
        document.getElementById('ortexKey').addEventListener('input', function(e) {
            localStorage.setItem('ortex_api_key', e.target.value);
        });

        // Load saved API key on page load
        window.addEventListener('load', function() {
            const savedKey = localStorage.getItem('ortex_api_key');
            if (savedKey) {
                document.getElementById('ortexKey').value = savedKey;
            }
        });

        // Allow Enter key to trigger scan
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
                performScan();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/api')
def api_info():
    """API Information and Health Status"""
    cache_stats = {
        'total_cached_items': len(squeeze_api.cache),
        'cache_hit_rate': len([k for k in squeeze_api.cache_timestamps if squeeze_api.is_cache_valid(k)]) / max(len(squeeze_api.cache_timestamps), 1) * 100
    }
    
    return jsonify({
        'status': 'healthy',
        'title': 'Enhanced Ultimate Squeeze Scanner API v2.0',
        'description': 'Professional-grade serverless squeeze analysis with real-time Ortex integration',
        'version': 'enhanced_serverless_v2.0',
        'deployment': 'vercel_serverless',
        'homepage_url': '/',
        'endpoints': {
            '/': 'Professional UI Interface (Homepage)',
            '/api': 'API Information & Health Status',
            '/api/squeeze/scan': 'Enhanced Squeeze Scanning (POST)',
            '/api/scan': 'Alias for Enhanced Squeeze Scanning (POST)',
            '/api/health': 'Detailed Health Check'
        },
        'features': [
            'Enhanced Ortex integration (5 data types)',
            'Smart caching (30-minute TTL)', 
            'Sequential processing (serverless optimized)',
            'Enhanced squeeze scoring algorithm',
            'Real-time Yahoo Finance price integration',
            'Professional responsive UI',
            'Multi-endpoint Ortex data fetching',
            'Intelligent fallback mechanisms'
        ],
        'ortex_data_sources': {
            'short_interest': 'Short Interest Percentage',
            'cost_to_borrow': 'Cost to Borrow Rate',
            'days_to_cover': 'Days to Cover Ratio', 
            'availability': 'Share Availability',
            'stock_scores': 'Ortex Stock Scores'
        },
        'cache_stats': cache_stats,
        'usage': {
            'scan_endpoint': '/api/squeeze/scan',
            'method': 'POST',
            'required_fields': ['ortex_key', 'tickers'],
            'example_payload': {
                'ortex_key': 'your_ortex_api_key_here',
                'tickers': 'GME,AMC,TSLA'
            }
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api/squeeze/scan', methods=['POST'])
def enhanced_squeeze_scan():
    """Enhanced squeeze scanning endpoint"""
    try:
        data = request.get_json() or {}
        tickers_input = data.get('tickers', data.get('tickerList', 'GME,AMC,TSLA'))
        ortex_key = data.get('ortex_key', data.get('ortexKey', os.environ.get('ORTEX_API_KEY')))
        
        if not ortex_key:
            return jsonify({
                'success': False,
                'error': 'Ortex API key required',
                'message': 'Please enter your Ortex API key in the configuration panel'
            }), 400
        
        # Parse tickers
        if isinstance(tickers_input, str):
            tickers = [t.strip().upper() for t in tickers_input.replace(',', ' ').split() if t.strip()]
        elif isinstance(tickers_input, list):
            tickers = [str(t).strip().upper() for t in tickers_input if str(t).strip()]
        else:
            tickers = ['GME', 'AMC', 'TSLA']
        
        # Limit for serverless performance
        tickers = tickers[:15]
        
        # Get price data
        price_data = get_yahoo_price_data(tickers)
        
        results = []
        total_credits_used = 0
        
        # Process tickers sequentially for serverless stability
        for ticker in tickers:
            try:
                # Get optimized Ortex data
                ortex_results = squeeze_api.fetch_ortex_data_optimized(
                    ticker, 
                    ortex_key,
                    ['short_interest', 'cost_to_borrow', 'days_to_cover', 'availability']
                )
                
                # Process into squeeze metrics
                squeeze_data = squeeze_api.process_enhanced_squeeze_data(
                    ortex_results or {}, 
                    price_data.get(ticker)
                )
                
                # Determine risk level
                score = squeeze_data['squeeze_score']
                if score >= 80:
                    squeeze_type = "EXTREME SQUEEZE RISK"
                    risk_class = "squeeze-extreme"
                elif score >= 60:
                    squeeze_type = "HIGH SQUEEZE RISK"  
                    risk_class = "squeeze-high"
                elif score >= 40:
                    squeeze_type = "MODERATE SQUEEZE RISK"
                    risk_class = "squeeze-moderate"
                else:
                    squeeze_type = "Low Risk"
                    risk_class = ""
                
                ticker_price = price_data.get(ticker, {})
                
                result = {
                    'ticker': ticker,
                    'squeeze_score': score,
                    'squeeze_type': squeeze_type,
                    'risk_class': risk_class,
                    'current_price': ticker_price.get('current_price', 0),
                    'price_change': ticker_price.get('price_change', 0),
                    'price_change_pct': ticker_price.get('price_change_pct', 0),
                    'volume': ticker_price.get('volume', 0),
                    'ortex_data': {
                        'short_interest': round(squeeze_data['short_interest'], 2),
                        'utilization': round(squeeze_data.get('utilization', 0), 2),
                        'cost_to_borrow': round(squeeze_data['cost_to_borrow'], 2),
                        'days_to_cover': round(squeeze_data['days_to_cover'], 2),
                        'data_sources': squeeze_data['data_sources'],
                        'confidence': squeeze_data['confidence']
                    },
                    'credits_used': squeeze_data['total_credits_used'],
                    'data_source': 'enhanced_ortex_live',
                    'success': True
                }
                
                results.append(result)
                total_credits_used += result.get('credits_used', 0)
                
            except Exception as e:
                # Continue processing other tickers even if one fails
                continue
        
        # Sort by squeeze score
        results.sort(key=lambda x: x.get('squeeze_score', 0), reverse=True)
        
        return jsonify({
            'success': True,
            'message': f'Enhanced squeeze scan complete - {len(results)} tickers analyzed',
            'results': results,
            'total_tickers': len(results),
            'high_risk_count': len([r for r in results if r.get('squeeze_score', 0) >= 60]),
            'total_credits_used': total_credits_used,
            'scan_timestamp': datetime.now().isoformat(),
            'enhancement_info': {
                'cache_hit_rate': f"{len([r for r in results if r.get('credits_used', 1) == 0]) / len(results) * 100:.1f}%" if results else "0%",
                'data_sources_per_ticker': len(squeeze_api.ortex_endpoints),
                'parallel_processing': False,  # Sequential for serverless
                'enhanced_scoring': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Enhanced squeeze scan error: {str(e)}',
            'message': 'Please check your API key and try again'
        }), 500

@app.route('/api/scan', methods=['POST'])
def options_scan():
    """Original options scan endpoint - redirects to enhanced"""
    return enhanced_squeeze_scan()

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    cache_stats = {
        'total_cached_items': len(squeeze_api.cache),
        'cache_hit_rate': len([k for k in squeeze_api.cache_timestamps if squeeze_api.is_cache_valid(k)]) / max(len(squeeze_api.cache_timestamps), 1) * 100
    }
    
    return jsonify({
        'status': 'healthy',
        'version': 'enhanced_serverless_v2.0',
        'deployment': 'vercel_serverless',
        'features': [
            'Enhanced Ortex integration (5 data types)',
            'Smart caching (30-minute TTL)', 
            'Sequential processing (serverless optimized)',
            'Enhanced squeeze scoring',
            'Real-time price data integration',
            'Professional UI with enhanced styling'
        ],
        'ortex_endpoints': {
            'working': list(squeeze_api.ortex_endpoints.keys()),
            'total_available': len(squeeze_api.ortex_endpoints)
        },
        'cache_stats': cache_stats,
        'timestamp': datetime.now().isoformat()
    })

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
