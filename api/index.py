from flask import Flask, request, jsonify
import json
import urllib.request
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return '''<html><body><h1>Enhanced Squeeze Scanner</h1><form onsubmit="scan();return false;"><input type="password" id="key" placeholder="Ortex API Key"><br><textarea id="tickers" placeholder="GME,AMC,TSLA">GME,AMC,TSLA</textarea><br><button type="submit">Scan</button></form><div id="results"></div><script>async function scan(){const key=document.getElementById('key').value;const tickers=document.getElementById('tickers').value;if(!key)return;try{const r=await fetch('/api/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ortex_key:key,tickers:tickers})});const d=await r.json();document.getElementById('results').innerHTML=d.success?d.results.map(x=>`${x.ticker}: ${x.squeeze_score}/100`).join('<br>'):'Error: '+d.error;}catch(e){document.getElementById('results').innerHTML='Error: '+e;}}</script></body></html>'''

@app.route('/api/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json() or {}
        ortex_key = data.get('ortex_key', '')
        tickers_input = data.get('tickers', 'GME,AMC,TSLA')
        
        if not ortex_key:
            return jsonify({'success': False, 'error': 'API key required'})
        
        tickers = [t.strip().upper() for t in tickers_input.replace(',', ' ').split() if t.strip()]
        tickers = tickers[:5]  # Limit to 5 for speed
        
        results = []
        for ticker in tickers:
            try:
                # Simple Yahoo Finance price fetch
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0')
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    price_data = json.loads(response.read())
                    
                    if 'chart' in price_data and price_data['chart']['result']:
                        meta = price_data['chart']['result'][0]['meta']
                        current_price = meta.get('regularMarketPrice', 0)
                        previous_close = meta.get('previousClose', 0)
                        price_change_pct = ((current_price - previous_close) / previous_close * 100) if previous_close else 0
                        
                        # Simple Ortex fetch (just one endpoint)
                        ortex_url = f"https://api.ortex.com/api/v1/stock/us/{ticker}/short_interest?format=json"
                        ortex_req = urllib.request.Request(ortex_url)
                        ortex_req.add_header('Ortex-Api-Key', ortex_key)
                        
                        short_interest = 0
                        try:
                            with urllib.request.urlopen(ortex_req, timeout=5) as ortex_response:
                                ortex_data = json.loads(ortex_response.read())
                                if 'rows' in ortex_data and ortex_data['rows']:
                                    short_interest = ortex_data['rows'][0].get('shortInterestPcFreeFloat', 0)
                        except:
                            pass
                        
                        # Simple score calculation
                        squeeze_score = min(int(short_interest * 2), 100)
                        
                        results.append({
                            'ticker': ticker,
                            'current_price': round(current_price, 2),
                            'price_change_pct': round(price_change_pct, 2),
                            'squeeze_score': squeeze_score,
                            'ortex_data': {'short_interest': round(short_interest, 2)},
                            'success': True
                        })
                        
            except Exception:
                results.append({
                    'ticker': ticker,
                    'squeeze_score': 0,
                    'current_price': 0,
                    'price_change_pct': 0,
                    'ortex_data': {'short_interest': 0},
                    'success': False
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_tickers': len(results),
            'message': f'Scan complete - {len(results)} tickers'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api')
def api_info():
    return jsonify({
        'status': 'healthy',
        'version': 'minimal_v1.0',
        'endpoints': {'/': 'Homepage', '/api/scan': 'Scan endpoint'},
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
