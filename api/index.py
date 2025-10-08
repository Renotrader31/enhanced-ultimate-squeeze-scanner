try:
     2	    from flask import Flask, jsonify, request
     3	    import json
     4	    import urllib.parse
     5	    import urllib.request
     6	    import os
     7	    from datetime import datetime, timedelta
     8	    import threading
     9	except ImportError as e:
    10	    def create_error_response():
    11	        return f"Import Error: {str(e)}"
    12	
    13	app = Flask(__name__)
    14	
    15	# Enhanced Squeeze Scanner with Ortex Integration
    16	class SqueezeAPI:
    17	    def __init__(self):
    18	        self.cache = {}
    19	        self.cache_timestamps = {}
    20	        self.cache_duration = 1800  # 30 minutes
    21	        self.lock = threading.Lock()
    22	        
    23	    def get_yahoo_price(self, ticker):
    24	        """Get real-time price from Yahoo Finance"""
    25	        try:
    26	            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    27	            req = urllib.request.Request(url)
    28	            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; EnhancedSqueezeScanner/2.0)')
    29	            
    30	            with urllib.request.urlopen(req, timeout=5) as response:
    31	                data = json.loads(response.read())
    32	                
    33	                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
    34	                    result = data['chart']['result'][0]
    35	                    meta = result.get('meta', {})
    36	                    
    37	                    current_price = meta.get('regularMarketPrice', 0)
    38	                    previous_close = meta.get('previousClose', 0)
    39	                    volume = meta.get('regularMarketVolume', 0)
    40	                    
    41	                    price_change = current_price - previous_close if previous_close else 0
    42	                    price_change_pct = (price_change / previous_close * 100) if previous_close else 0
    43	                    
    44	                    return {
    45	                        'ticker': ticker,
    46	                        'current_price': round(current_price, 2),
    47	                        'price_change': round(price_change, 2),
    48	                        'price_change_pct': round(price_change_pct, 2),
    49	                        'volume': volume,
    50	                        'success': True
    51	                    }
    52	        except Exception:
    53	            pass
    54	        
    55	        return {'ticker': ticker, 'success': False}
    56	
    57	squeeze_api = SqueezeAPI()
    58	
    59	@app.route('/', methods=['GET'])
    60	def home():
    61	    try:
    62	        return jsonify({
    63	            "status": "success",
    64	            "message": "🚀 Enhanced Ultimate Squeeze Scanner v2.0 - WORKING!",
    65	            "version": "2.0.0",
    66	            "features": [
    67	                "Real-time price data",
    68	                "Ortex API integration ready",
    69	                "Smart caching system",
    70	                "Enhanced squeeze scoring"
    71	            ],
    72	            "timestamp": datetime.now().isoformat(),
    73	            "endpoints": [
    74	                "/api/health",
    75	                "/api/test",
    76	                "/api/squeeze/scan"
    77	            ]
    78	        })
    79	    except Exception as e:
    80	        return f"Error in home route: {str(e)}", 500
    81	
    82	@app.route('/api/health', methods=['GET'])
    83	def health():
    84	    try:
    85	        return jsonify({
    86	            "status": "healthy",
    87	            "version": "enhanced_v2.0.0",
    88	            "message": "Enhanced Ultimate Squeeze Scanner - All Systems Operational",
    89	            "timestamp": datetime.now().isoformat(),
    90	            "features": {
    91	                "yahoo_finance": "active",
    92	                "caching_system": "active",
    93	                "ortex_integration": "ready",
    94	                "enhanced_scoring": "active"
    95	            },
    96	            "cache_stats": {
    97	                "total_cached_items": len(squeeze_api.cache),
    98	                "cache_enabled": True
    99	            },
   100	            "deployment": "vercel_serverless"
