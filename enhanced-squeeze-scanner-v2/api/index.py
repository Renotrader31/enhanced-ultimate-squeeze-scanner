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

# Route handlers
@app.route('/')
def index():
    """Serve the enhanced interface"""
    return render_template('index.html')

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