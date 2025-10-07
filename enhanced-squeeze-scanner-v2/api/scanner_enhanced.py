from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import urllib.request
import os
from datetime import datetime
import time
import concurrent.futures
from threading import Lock
import random

class handler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        # Comprehensive ticker universe for scanning
        self.ticker_universe = {
            'meme_stocks': [
                'GME', 'AMC', 'BBBY', 'SAVA', 'VXRT', 'CLOV', 'SPRT', 'IRNT', 
                'DWAC', 'PHUN', 'BENE', 'PROG', 'ATER', 'BBIG', 'RDBX', 'NILE',
                'MULN', 'HMHC', 'EXPR', 'KOSS', 'NAKD', 'SNDL', 'TLRY', 'CGC'
            ],
            'high_short_interest': [
                'BYND', 'PELOTON', 'ROKU', 'ZOOM', 'DOCU', 'PTON', 'UPST', 'AFRM',
                'HOOD', 'COIN', 'RIVN', 'LCID', 'NKLA', 'PLUG', 'BLNK', 'QS',
                'GOEV', 'RIDE', 'FISV', 'WKHS', 'SOLO', 'ARVL', 'CANOO'
            ],
            'biotech_squeeze': [
                'BIIB', 'GILD', 'REGN', 'VRTX', 'BMRN', 'ALNY', 'SRPT', 'IONS',
                'ARWR', 'EDIT', 'CRSP', 'NTLA', 'BEAM', 'PRIME', 'BLUE', 'FOLD',
                'RARE', 'KRYS', 'CDNA', 'VCYT', 'PACB', 'ILMN', 'TWST', 'FATE'
            ],
            'small_cap_movers': [
                'SPCE', 'OPEN', 'SKLZ', 'DKNG', 'PENN', 'MGNI', 'FUBO', 'APPS',
                'WISH', 'COUR', 'MTTR', 'RBLX', 'U', 'PLTR', 'SNOW', 'CRWD',
                'OKTA', 'DDOG', 'NET', 'FSLY', 'ESTC', 'WORK', 'ZM', 'DOCN'
            ],
            'russell_3000_samples': [
                # Major tech
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA',
                # Finance
                'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'AXP', 'BLK',
                # Healthcare
                'JNJ', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'CVS',
                # Consumer
                'WMT', 'HD', 'PG', 'KO', 'PEP', 'MCD', 'NKE', 'SBUX',
                # Energy
                'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC'
            ]
        }
        
        # Flatten all tickers into master list
        self.master_ticker_list = []
        for category, tickers in self.ticker_universe.items():
            self.master_ticker_list.extend(tickers)
        
        # Remove duplicates while preserving order
        seen = set()
        self.master_ticker_list = [x for x in self.master_ticker_list if not (x in seen or seen.add(x))]
        
        self.scan_lock = Lock()
        self.scan_results_cache = {}
        self.last_scan_time = None
        
        super().__init__(*args, **kwargs)
    
    def get_comprehensive_ortex_data(self, ticker, ortex_key):
        """Attempt to get ALL available Ortex data using multiple endpoints"""
        if not ortex_key:
            return None
            
        # All known Ortex API endpoints to try
        ortex_endpoints = {
            'short_interest_nasdaq': f'https://api.ortex.com/api/v1/stock/nasdaq/{ticker}/short_interest',
            'short_interest_nyse': f'https://api.ortex.com/api/v1/stock/nyse/{ticker}/short_interest',
            'short_interest_general': f'https://api.ortex.com/api/v1/stock/{ticker}/short_interest',
            'utilization': f'https://api.ortex.com/api/v1/stock/{ticker}/utilization',
            'cost_to_borrow': f'https://api.ortex.com/api/v1/stock/{ticker}/ctb',
            'availability': f'https://api.ortex.com/api/v1/stock/{ticker}/availability',
            'days_to_cover': f'https://api.ortex.com/api/v1/stock/{ticker}/dtc',
            'shares_on_loan': f'https://api.ortex.com/api/v1/stock/{ticker}/shares_on_loan',
            'short_volume': f'https://api.ortex.com/api/v1/stock/{ticker}/short_volume',
            'short_exempt_volume': f'https://api.ortex.com/api/v1/stock/{ticker}/short_exempt',
            'borrowed_shares': f'https://api.ortex.com/api/v1/stock/{ticker}/borrowed_shares',
            'returned_shares': f'https://api.ortex.com/api/v1/stock/{ticker}/returned_shares',
            # Alternative endpoint formats
            'short_data_alt1': f'https://api.ortex.com/v1/stock/{ticker}/short-interest',
            'short_data_alt2': f'https://api.ortex.com/rest/v1/stock/{ticker}/short_interest',
            'utilization_alt': f'https://api.ortex.com/v1/stock/{ticker}/utilization',
            'ctb_alt': f'https://api.ortex.com/v1/stock/{ticker}/cost-to-borrow',
            # Public endpoints (may not require auth)
            'public_short_interest': f'https://public.ortex.com/api/short-interest/{ticker}',
            'public_data': f'https://public.ortex.com/api/stock/{ticker}',
        }
        
        collected_data = {}
        successful_endpoints = []
        
        for endpoint_name, url in ortex_endpoints.items():
            try:
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Ultimate-Squeeze-Scanner/2.0')
                req.add_header('Accept', 'application/json')
                req.add_header('Ortex-Api-Key', ortex_key)  # Correct auth method
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.getcode() == 200:
                        content_type = response.headers.get('Content-Type', '')
                        data = response.read().decode('utf-8')
                        
                        # Only process JSON responses
                        if 'application/json' in content_type:
                            try:
                                json_data = json.loads(data)
                                collected_data[endpoint_name] = json_data
                                successful_endpoints.append(endpoint_name)
                                print(f"  ✅ {endpoint_name}: Got JSON data ({len(data)} bytes)")
                            except json.JSONDecodeError:
                                pass
                        elif len(data) < 1000 and not data.startswith('<!DOCTYPE'):
                            # Small non-HTML response might be valid data
                            try:
                                json_data = json.loads(data)
                                collected_data[endpoint_name] = json_data
                                successful_endpoints.append(endpoint_name)
                            except:
                                pass
                                
            except Exception as e:
                # Silent fail for now - we're testing many endpoints
                continue
        
        # Process collected data into standardized format
        if collected_data:
            return self.process_ortex_data(collected_data, successful_endpoints)
        else:
            return None
    
    def process_ortex_data(self, raw_data, successful_endpoints):
        """Process raw Ortex data into standardized squeeze metrics"""
        processed = {
            'short_interest': None,
            'utilization': None,
            'cost_to_borrow': None,
            'days_to_cover': None,
            'shares_on_loan': None,
            'short_volume': None,
            'borrowed_shares': None,
            'returned_shares': None,
            'availability': None,
            'source_endpoints': successful_endpoints,
            'data_quality': 'live_ortex'
        }
        
        # Extract data from successful endpoints
        for endpoint_name, data in raw_data.items():
            if isinstance(data, dict):
                # Try to extract common field names
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        # Map common field patterns
                        key_lower = str(key).lower()
                        if 'short_interest' in key_lower or 'si_percent' in key_lower:
                            processed['short_interest'] = value
                        elif 'utilization' in key_lower or 'util' in key_lower:
                            processed['utilization'] = value
                        elif 'cost_to_borrow' in key_lower or 'ctb' in key_lower or 'borrow_rate' in key_lower:
                            processed['cost_to_borrow'] = value
                        elif 'days_to_cover' in key_lower or 'dtc' in key_lower:
                            processed['days_to_cover'] = value
                        elif 'shares_on_loan' in key_lower or 'on_loan' in key_lower:
                            processed['shares_on_loan'] = value
                        elif 'short_volume' in key_lower:
                            processed['short_volume'] = value
                        elif 'borrowed' in key_lower and 'shares' in key_lower:
                            processed['borrowed_shares'] = value
                        elif 'returned' in key_lower and 'shares' in key_lower:
                            processed['returned_shares'] = value
                        elif 'availability' in key_lower or 'available' in key_lower:
                            processed['availability'] = value
        
        # Fill in missing data with reasonable estimates if we have partial data
        if processed['short_interest'] and not processed['utilization']:
            # Estimate utilization based on short interest
            processed['utilization'] = min(processed['short_interest'] * 3.5, 100)
        
        if processed['short_interest'] and not processed['days_to_cover']:
            # Estimate days to cover
            processed['days_to_cover'] = max(processed['short_interest'] * 0.2, 0.5)
            
        return processed
    
    def get_yahoo_price_data_batch(self, tickers):
        """Get price data for multiple tickers efficiently"""
        price_data = {}
        
        def get_single_price(ticker):
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read())
                    
                    if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                        result = data['chart']['result'][0]
                        meta = result.get('meta', {})
                        
                        current_price = meta.get('regularMarketPrice', 0)
                        previous_close = meta.get('previousClose', 0)
                        volume = meta.get('regularMarketVolume', 0)
                        market_cap = meta.get('marketCap', 0)
                        
                        price_change = current_price - previous_close if previous_close else 0
                        price_change_pct = (price_change / previous_close * 100) if previous_close else 0
                        
                        return {
                            'ticker': ticker,
                            'current_price': round(current_price, 2),
                            'previous_close': round(previous_close, 2),
                            'price_change': round(price_change, 2),
                            'price_change_pct': round(price_change_pct, 2),
                            'volume': volume,
                            'market_cap': market_cap,
                            'success': True
                        }
                        
            except Exception as e:
                return {'ticker': ticker, 'success': False, 'error': str(e)}
        
        # Use threading for faster batch processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_ticker = {executor.submit(get_single_price, ticker): ticker for ticker in tickers}
            
            for future in concurrent.futures.as_completed(future_to_ticker):
                result = future.result()
                if result and result.get('success'):
                    price_data[result['ticker']] = result
        
        return price_data
    
    def generate_enhanced_mock_data_batch(self, tickers):
        """Generate realistic mock data for multiple tickers"""
        mock_data = {}
        
        # Enhanced profiles for known squeeze candidates
        known_profiles = {
            'GME': {'si': 22.4, 'util': 89.2, 'ctb': 12.8, 'dtc': 4.1, 'quality': 'high_squeeze'},
            'AMC': {'si': 18.7, 'util': 82.1, 'ctb': 8.9, 'dtc': 3.8, 'quality': 'medium_squeeze'},
            'SAVA': {'si': 35.2, 'util': 95.1, 'ctb': 45.8, 'dtc': 12.3, 'quality': 'extreme_squeeze'},
            'VXRT': {'si': 28.9, 'util': 87.6, 'ctb': 18.2, 'dtc': 8.7, 'quality': 'high_squeeze'},
            'CLOV': {'si': 15.8, 'util': 76.3, 'ctb': 6.4, 'dtc': 4.2, 'quality': 'medium_squeeze'},
            'BBBY': {'si': 42.1, 'util': 98.2, 'ctb': 78.5, 'dtc': 15.8, 'quality': 'extreme_squeeze'},
            'BYND': {'si': 31.5, 'util': 91.7, 'ctb': 25.3, 'dtc': 9.2, 'quality': 'high_squeeze'},
            'PTON': {'si': 26.8, 'util': 84.5, 'ctb': 15.7, 'dtc': 6.8, 'quality': 'medium_squeeze'},
        }
        
        for ticker in tickers:
            if ticker in known_profiles:
                profile = known_profiles[ticker]
            else:
                # Generate realistic random data based on ticker characteristics
                random.seed(hash(ticker) % 10000)  # Consistent random for same ticker
                
                # Different profiles based on ticker patterns
                if ticker in self.ticker_universe.get('meme_stocks', []):
                    # Meme stocks tend to have higher short interest
                    si_base = random.uniform(15, 40)
                    util_base = random.uniform(70, 95)
                    ctb_base = random.uniform(8, 50)
                elif ticker in self.ticker_universe.get('biotech_squeeze', []):
                    # Biotech can have extreme metrics
                    si_base = random.uniform(20, 45)
                    util_base = random.uniform(75, 98)
                    ctb_base = random.uniform(12, 80)
                elif ticker in self.ticker_universe.get('russell_3000_samples', []):
                    # Large caps typically have lower short interest
                    si_base = random.uniform(1, 8)
                    util_base = random.uniform(20, 60)
                    ctb_base = random.uniform(0.5, 5)
                else:
                    # General stocks
                    si_base = random.uniform(5, 25)
                    util_base = random.uniform(40, 85)
                    ctb_base = random.uniform(2, 20)
                
                profile = {
                    'si': round(si_base, 1),
                    'util': round(util_base, 1),
                    'ctb': round(ctb_base, 1),
                    'dtc': round(si_base * random.uniform(0.15, 0.4), 1),
                    'quality': 'generated'
                }
            
            mock_data[ticker] = {
                'short_interest': profile['si'],
                'utilization': profile['util'],
                'cost_to_borrow': profile['ctb'],
                'days_to_cover': profile['dtc'],
                'shares_on_loan': profile['si'] * random.uniform(800000, 2000000),
                'source_endpoints': ['enhanced_mock'],
                'data_quality': profile.get('quality', 'generated'),
                'note': 'Enhanced mock data - realistic market estimates'
            }
        
        return mock_data
    
    def calculate_squeeze_score_advanced(self, ortex_data, price_data):
        """Advanced squeeze scoring with enhanced weightings"""
        try:
            # Extract metrics
            si = ortex_data.get('short_interest', 0)
            util = ortex_data.get('utilization', 0)
            ctb = ortex_data.get('cost_to_borrow', 0)
            dtc = ortex_data.get('days_to_cover', 0)
            price_change_pct = price_data.get('price_change_pct', 0)
            volume = price_data.get('volume', 0)
            
            # Enhanced scoring algorithm (0-100 scale)
            # Short Interest Score (0-35 points) - Most important factor
            if si >= 30:
                si_score = 35
            elif si >= 20:
                si_score = 25 + (si - 20) * 1.0  # 25-35 range
            elif si >= 10:
                si_score = 15 + (si - 10) * 1.0  # 15-25 range
            else:
                si_score = si * 1.5  # 0-15 range
            
            # Utilization Score (0-25 points)
            if util >= 95:
                util_score = 25
            elif util >= 80:
                util_score = 18 + (util - 80) * 0.47  # 18-25 range
            elif util >= 60:
                util_score = 10 + (util - 60) * 0.4   # 10-18 range
            else:
                util_score = util * 0.17  # 0-10 range
            
            # Cost to Borrow Score (0-20 points)
            if ctb >= 50:
                ctb_score = 20
            elif ctb >= 20:
                ctb_score = 15 + (ctb - 20) * 0.17  # 15-20 range
            elif ctb >= 5:
                ctb_score = 8 + (ctb - 5) * 0.47   # 8-15 range
            else:
                ctb_score = ctb * 1.6  # 0-8 range
            
            # Days to Cover Score (0-15 points)
            if dtc >= 10:
                dtc_score = 15
            elif dtc >= 5:
                dtc_score = 10 + (dtc - 5) * 1.0  # 10-15 range
            elif dtc >= 2:
                dtc_score = 5 + (dtc - 2) * 1.67  # 5-10 range
            else:
                dtc_score = dtc * 2.5  # 0-5 range
            
            # Momentum Score (0-5 points) - Price movement bonus
            if price_change_pct > 10:
                momentum_score = 5
            elif price_change_pct > 5:
                momentum_score = 3 + (price_change_pct - 5) * 0.4
            elif price_change_pct > 0:
                momentum_score = price_change_pct * 0.6
            else:
                momentum_score = 0  # No negative momentum scoring
            
            # Total score
            total_score = int(si_score + util_score + ctb_score + dtc_score + momentum_score)
            total_score = min(total_score, 100)  # Cap at 100
            
            # Enhanced risk categorization
            risk_factors = []
            if si > 30:
                risk_factors.append("EXTREME_SHORT_INTEREST")
            elif si > 20:
                risk_factors.append("HIGH_SHORT_INTEREST")
            
            if util > 90:
                risk_factors.append("HIGH_UTILIZATION")
            
            if ctb > 20:
                risk_factors.append("HIGH_BORROWING_COSTS")
            
            if dtc > 7:
                risk_factors.append("LONG_COVER_TIME")
            
            if price_change_pct > 15:
                risk_factors.append("STRONG_UPWARD_MOMENTUM")
            
            # Squeeze type determination
            if total_score >= 80:
                squeeze_type = "Extreme Squeeze Risk"
            elif total_score >= 65:
                squeeze_type = "High Squeeze Risk"
            elif total_score >= 45:
                squeeze_type = "Moderate Squeeze Risk"
            elif total_score >= 25:
                squeeze_type = "Low Squeeze Risk"
            else:
                squeeze_type = "Minimal Risk"
            
            return {
                'squeeze_score': total_score,
                'squeeze_type': squeeze_type,
                'score_breakdown': {
                    'short_interest': int(si_score),
                    'utilization': int(util_score),
                    'cost_to_borrow': int(ctb_score),
                    'days_to_cover': int(dtc_score),
                    'momentum': int(momentum_score)
                },
                'risk_factors': risk_factors
            }
            
        except Exception as e:
            return {
                'squeeze_score': 0,
                'squeeze_type': 'Analysis Error',
                'error': str(e)
            }
    
    def perform_comprehensive_scan(self, ortex_key=None, filters=None):
        """Perform comprehensive multi-ticker squeeze scan"""
        print(f"🚀 Starting comprehensive squeeze scan...")
        
        # Apply filters to ticker universe
        scan_tickers = self.master_ticker_list.copy()
        
        if filters:
            if filters.get('categories'):
                # Filter by specific categories
                filtered_tickers = []
                for category in filters['categories']:
                    if category in self.ticker_universe:
                        filtered_tickers.extend(self.ticker_universe[category])
                scan_tickers = list(set(filtered_tickers))
            
            if filters.get('max_tickers'):
                # Limit number of tickers to scan
                scan_tickers = scan_tickers[:filters['max_tickers']]
        
        print(f"📊 Scanning {len(scan_tickers)} tickers...")
        
        # Get price data for all tickers (batch processing)
        print(f"💰 Fetching live price data...")
        price_data = self.get_yahoo_price_data_batch(scan_tickers)
        successful_price_tickers = [t for t in scan_tickers if t in price_data]
        
        print(f"✅ Got price data for {len(successful_price_tickers)} tickers")
        
        # Get Ortex data (use mock data for now, but structure for live integration)
        print(f"🔍 Processing short interest data...")
        if ortex_key:
            # Try live Ortex data for a few tickers as test
            live_ortex_results = {}
            test_tickers = successful_price_tickers[:5]  # Test first 5
            
            for ticker in test_tickers:
                ortex_data = self.get_comprehensive_ortex_data(ticker, ortex_key)
                if ortex_data:
                    live_ortex_results[ticker] = ortex_data
                    print(f"  ✅ Live Ortex data for {ticker}")
                else:
                    print(f"  ⚠️ No live data for {ticker}, using mock")
            
            # Fill remaining with mock data
            mock_ortex_data = self.generate_enhanced_mock_data_batch(successful_price_tickers)
            
            # Merge live and mock data
            ortex_data = {**mock_ortex_data, **live_ortex_results}
        else:
            # Use all mock data
            ortex_data = self.generate_enhanced_mock_data_batch(successful_price_tickers)
        
        # Calculate squeeze scores for all tickers
        print(f"🎯 Calculating squeeze scores...")
        results = []
        
        for ticker in successful_price_tickers:
            if ticker in ortex_data:
                squeeze_metrics = self.calculate_squeeze_score_advanced(
                    ortex_data[ticker], 
                    price_data[ticker]
                )
                
                result = {
                    'ticker': ticker,
                    'squeeze_score': squeeze_metrics['squeeze_score'],
                    'squeeze_type': squeeze_metrics['squeeze_type'],
                    'current_price': price_data[ticker]['current_price'],
                    'price_change': price_data[ticker]['price_change'],
                    'price_change_pct': price_data[ticker]['price_change_pct'],
                    'volume': price_data[ticker]['volume'],
                    'market_cap': price_data[ticker].get('market_cap', 0),
                    'ortex_data': ortex_data[ticker],
                    'score_breakdown': squeeze_metrics.get('score_breakdown', {}),
                    'risk_factors': squeeze_metrics.get('risk_factors', []),
                    'data_quality': ortex_data[ticker].get('data_quality', 'mock'),
                    'timestamp': datetime.now().isoformat()
                }
                
                results.append(result)
        
        # Sort by squeeze score (highest first)
        results.sort(key=lambda x: x['squeeze_score'], reverse=True)
        
        print(f"✅ Scan complete! Found {len(results)} analyzed tickers")
        
        return {
            'results': results,
            'scan_stats': {
                'total_tickers_attempted': len(scan_tickers),
                'successful_price_data': len(successful_price_tickers),
                'successful_analysis': len(results),
                'live_ortex_count': len([r for r in results if r['data_quality'] == 'live_ortex']),
                'mock_data_count': len([r for r in results if 'mock' in r['data_quality']]),
                'scan_timestamp': datetime.now().isoformat(),
                'top_score': results[0]['squeeze_score'] if results else 0,
                'categories_scanned': list(self.ticker_universe.keys()) if not filters else filters.get('categories', [])
            }
        }
    
    def do_GET(self):
        if self.path == '/':
            self.send_scanner_html()
        elif self.path == '/api/health':
            self.send_health()
        elif self.path == '/scanner-status':
            self.send_scanner_status()
        elif self.path.startswith('/api/ticker-universe'):
            self.send_ticker_universe()
        else:
            self.send_404()
    
    def do_POST(self):
        if self.path == '/api/comprehensive-scan':
            self.handle_comprehensive_scan()
        elif self.path == '/api/squeeze/scan':
            self.handle_single_squeeze_scan()
        elif self.path == '/api/validate-ortex-key':
            self.handle_ortex_validation()
        else:
            self.send_404()
    
    def handle_comprehensive_scan(self):
        """Handle comprehensive multi-ticker scan requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode()) if post_data else {}
            
            ortex_key = data.get('ortex_key', '')
            filters = data.get('filters', {})
            
            # Perform the scan
            scan_results = self.perform_comprehensive_scan(ortex_key, filters)
            
            response = {
                'success': True,
                'scan_results': scan_results['results'],
                'scan_stats': scan_results['scan_stats'],
                'message': f"Comprehensive scan completed - analyzed {len(scan_results['results'])} tickers"
            }
            
            # Cache results
            with self.scan_lock:
                self.scan_results_cache = scan_results
                self.last_scan_time = datetime.now()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {'success': False, 'error': str(e)}
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def send_ticker_universe(self):
        """Send ticker universe information"""
        universe_info = {
            'categories': {name: len(tickers) for name, tickers in self.ticker_universe.items()},
            'total_tickers': len(self.master_ticker_list),
            'sample_tickers': {name: tickers[:10] for name, tickers in self.ticker_universe.items()}
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(universe_info).encode())
    
    def send_scanner_html(self):
        """Send enhanced scanner HTML interface"""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🚀 Ultimate Squeeze Scanner - Multi-Ticker Analysis</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 100%);
                    color: #e0e0e0;
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                }
                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                }
                .header {
                    text-align: center;
                    margin-bottom: 40px;
                }
                .header h1 {
                    color: #ff6b6b;
                    font-size: 3rem;
                    margin-bottom: 10px;
                    text-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
                }
                .scan-controls {
                    background: #1a1a2e;
                    padding: 30px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    border: 1px solid #3a3a4e;
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }
                .control-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    margin-bottom: 8px;
                    color: #a0a0b0;
                    font-weight: bold;
                }
                input, select {
                    width: 100%;
                    padding: 12px;
                    background: #2a2a3e;
                    border: 1px solid #4a4a5e;
                    border-radius: 8px;
                    color: #e0e0e0;
                    font-size: 16px;
                    box-sizing: border-box;
                }
                .btn {
                    background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    width: 100%;
                }
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
                }
                .btn:disabled {
                    background: #666;
                    cursor: not-allowed;
                }
                .results-grid {
                    display: grid;
                    gap: 15px;
                }
                .result-card {
                    background: #1a1a2e;
                    border-radius: 10px;
                    padding: 20px;
                    border-left: 5px solid #4CAF50;
                    display: grid;
                    grid-template-columns: 1fr 2fr 1fr 1fr;
                    gap: 15px;
                    align-items: center;
                }
                .ticker-info {
                    text-align: center;
                }
                .ticker-symbol {
                    font-size: 1.5rem;
                    font-weight: bold;
                    color: #ff6b6b;
                }
                .ticker-price {
                    color: #a0a0b0;
                    font-size: 0.9rem;
                }
                .metrics-mini {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }
                .metric-mini {
                    text-align: center;
                    background: #2a2a3e;
                    padding: 8px;
                    border-radius: 5px;
                }
                .metric-mini-value {
                    font-weight: bold;
                    color: #4CAF50;
                }
                .metric-mini-label {
                    font-size: 0.8rem;
                    color: #a0a0b0;
                }
                .squeeze-score-large {
                    text-align: center;
                }
                .score-number {
                    font-size: 3rem;
                    font-weight: bold;
                    color: #ff6b6b;
                }
                .score-type {
                    font-size: 0.9rem;
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-weight: bold;
                }
                .risk-indicators {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                }
                .risk-tag {
                    background: #f44336;
                    color: white;
                    padding: 3px 8px;
                    border-radius: 10px;
                    font-size: 0.7rem;
                    text-align: center;
                }
                .loading-scan {
                    text-align: center;
                    padding: 40px;
                    color: #ff6b6b;
                    font-size: 1.2rem;
                }
                .scan-stats {
                    background: #1a1a2e;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                }
                .stat-item {
                    text-align: center;
                    background: #2a2a3e;
                    padding: 15px;
                    border-radius: 8px;
                }
                .stat-value {
                    font-size: 2rem;
                    font-weight: bold;
                    color: #4CAF50;
                }
                .stat-label {
                    color: #a0a0b0;
                    font-size: 0.9rem;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Ultimate Squeeze Scanner</h1>
                    <p>Comprehensive Multi-Ticker Short Squeeze Analysis</p>
                </div>
                
                <div class="scan-controls">
                    <div>
                        <div class="control-group">
                            <label for="ortexKey">Ortex API Key</label>
                            <input type="text" id="ortexKey" placeholder="Your Ortex API key" value="zKBk0B8x.WWmEKkC5885KMymycx6s6kOeVmG5UHnG">
                        </div>
                        
                        <div class="control-group">
                            <label for="categories">Scan Categories</label>
                            <select id="categories" multiple>
                                <option value="meme_stocks" selected>Meme Stocks</option>
                                <option value="high_short_interest" selected>High Short Interest</option>
                                <option value="biotech_squeeze">Biotech Candidates</option>
                                <option value="small_cap_movers">Small Cap Movers</option>
                                <option value="russell_3000_samples">Russell 3000 Samples</option>
                            </select>
                            <small style="color: #a0a0b0;">Hold Ctrl/Cmd to select multiple</small>
                        </div>
                    </div>
                    
                    <div>
                        <div class="control-group">
                            <label for="maxTickers">Max Tickers to Scan</label>
                            <input type="number" id="maxTickers" value="50" min="10" max="200">
                        </div>
                        
                        <div class="control-group">
                            <label for="minScore">Min Squeeze Score</label>
                            <input type="number" id="minScore" value="30" min="0" max="100">
                        </div>
                        
                        <button class="btn" id="scanBtn" onclick="startComprehensiveScan()">
                            🔍 Start Comprehensive Scan
                        </button>
                    </div>
                </div>
                
                <div id="scanResults" style="display: none;">
                    <!-- Scan results will be populated here -->
                </div>
            </div>
            
            <script>
                async function startComprehensiveScan() {
                    const ortexKey = document.getElementById('ortexKey').value.trim();
                    const categoriesSelect = document.getElementById('categories');
                    const selectedCategories = Array.from(categoriesSelect.selectedOptions).map(option => option.value);
                    const maxTickers = parseInt(document.getElementById('maxTickers').value);
                    const minScore = parseInt(document.getElementById('minScore').value);
                    
                    const scanBtn = document.getElementById('scanBtn');
                    const resultsDiv = document.getElementById('scanResults');
                    
                    // Show loading
                    scanBtn.disabled = true;
                    scanBtn.textContent = '🔄 Scanning...';
                    resultsDiv.style.display = 'block';
                    resultsDiv.innerHTML = `
                        <div class="loading-scan">
                            🔄 Performing comprehensive squeeze scan...<br>
                            <small>Analyzing ${maxTickers} tickers across ${selectedCategories.length} categories</small>
                        </div>
                    `;
                    
                    try {
                        const response = await fetch('/api/comprehensive-scan', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                ortex_key: ortexKey,
                                filters: {
                                    categories: selectedCategories,
                                    max_tickers: maxTickers,
                                    min_score: minScore
                                }
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            displayScanResults(data.scan_results, data.scan_stats, minScore);
                        } else {
                            resultsDiv.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
                        }
                        
                    } catch (error) {
                        resultsDiv.innerHTML = `<div class="error">❌ Network error: ${error.message}</div>`;
                    }
                    
                    // Reset button
                    scanBtn.disabled = false;
                    scanBtn.textContent = '🔍 Start Comprehensive Scan';
                }
                
                function displayScanResults(results, stats, minScore) {
                    const resultsDiv = document.getElementById('scanResults');
                    
                    // Filter results by minimum score
                    const filteredResults = results.filter(r => r.squeeze_score >= minScore);
                    
                    let html = `
                        <div class="scan-stats">
                            <div class="stat-item">
                                <div class="stat-value">${stats.total_tickers_attempted}</div>
                                <div class="stat-label">Tickers Scanned</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${filteredResults.length}</div>
                                <div class="stat-label">Above Min Score</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${stats.live_ortex_count}</div>
                                <div class="stat-label">Live Ortex Data</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${stats.top_score}</div>
                                <div class="stat-label">Top Squeeze Score</div>
                            </div>
                        </div>
                        
                        <div class="results-grid">
                    `;
                    
                    filteredResults.forEach(result => {
                        html += `
                            <div class="result-card" style="border-left-color: ${getSqueezeColor(result.squeeze_score)}">
                                <div class="ticker-info">
                                    <div class="ticker-symbol">${result.ticker}</div>
                                    <div class="ticker-price">$${result.current_price}</div>
                                    <div class="ticker-price" style="color: ${result.price_change >= 0 ? '#4CAF50' : '#f44336'}">
                                        ${result.price_change >= 0 ? '+' : ''}${result.price_change_pct}%
                                    </div>
                                </div>
                                
                                <div class="metrics-mini">
                                    <div class="metric-mini">
                                        <div class="metric-mini-value">${result.ortex_data.short_interest}%</div>
                                        <div class="metric-mini-label">Short Interest</div>
                                    </div>
                                    <div class="metric-mini">
                                        <div class="metric-mini-value">${result.ortex_data.utilization}%</div>
                                        <div class="metric-mini-label">Utilization</div>
                                    </div>
                                    <div class="metric-mini">
                                        <div class="metric-mini-value">${result.ortex_data.cost_to_borrow}%</div>
                                        <div class="metric-mini-label">Cost to Borrow</div>
                                    </div>
                                    <div class="metric-mini">
                                        <div class="metric-mini-value">${result.ortex_data.days_to_cover}</div>
                                        <div class="metric-mini-label">Days to Cover</div>
                                    </div>
                                </div>
                                
                                <div class="squeeze-score-large">
                                    <div class="score-number">${result.squeeze_score}</div>
                                    <div class="score-type" style="background: ${getSqueezeColor(result.squeeze_score)}">
                                        ${result.squeeze_type}
                                    </div>
                                </div>
                                
                                <div class="risk-indicators">
                                    ${result.risk_factors.map(factor => 
                                        `<div class="risk-tag">${factor}</div>`
                                    ).join('')}
                                    <small style="color: #a0a0b0;">${result.data_quality}</small>
                                </div>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    
                    resultsDiv.innerHTML = html;
                }
                
                function getSqueezeColor(score) {
                    if (score >= 80) return '#d32f2f';      // Extreme - Dark red
                    if (score >= 65) return '#f44336';      // High - Red
                    if (score >= 45) return '#ff9800';      // Moderate - Orange
                    if (score >= 25) return '#2196F3';      // Low - Blue
                    return '#4CAF50';                       // Minimal - Green
                }
                
                // Load ticker universe on page load
                window.onload = function() {
                    fetch('/api/ticker-universe')
                        .then(response => response.json())
                        .then(data => {
                            console.log('Ticker Universe:', data);
                        });
                };
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def send_health(self):
        """Send API health check"""
        health_data = {
            'status': 'healthy',
            'message': 'Ultimate Squeeze Scanner API v8.0 - Multi-Ticker Comprehensive Analysis',
            'timestamp': datetime.now().isoformat(),
            'version': '8.0.0-comprehensive-scanner',
            'features': {
                'multi_ticker_scanning': 'active',
                'comprehensive_ortex_endpoints': 'testing',
                'yahoo_finance_batch': 'active',
                'advanced_scoring': 'active',
                'ticker_universe': len(self.master_ticker_list)
            },
            'ticker_categories': {name: len(tickers) for name, tickers in self.ticker_universe.items()},
            'total_universe_size': len(self.master_ticker_list)
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health_data).encode())
    
    def handle_single_squeeze_scan(self):
        """Handle single ticker analysis (for backward compatibility)"""
        # Implementation from simplified.py for single ticker scans
        pass
    
    def handle_ortex_validation(self):
        """Handle Ortex API key validation"""
        # Implementation from simplified.py
        pass
    
    def send_404(self):
        """Send 404 error"""
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'error': 'Not Found'}
        self.wfile.write(json.dumps(response).encode())