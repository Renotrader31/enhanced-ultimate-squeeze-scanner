# Route handlers - Professional UI as default homepage
@app.route('/')
def index():
    """Enhanced Ultimate Squeeze Scanner - Professional UI (Homepage)"""
    try:
        # Use existing template system to avoid serverless crashes
        return render_template('index.html')
    except:
        # Fallback simple interface if template fails
        return '''
<!DOCTYPE html>
<html>
<head>
    <title>Enhanced Ultimate Squeeze Scanner v2.0</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a1a; color: white; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input, textarea { width: 100%; padding: 10px; border-radius: 5px; border: 1px solid #333; background: #333; color: white; }
        button { width: 100%; padding: 15px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .results { margin-top: 20px; padding: 15px; background: #333; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced Ultimate Squeeze Scanner v2.0</h1>
            <p>Professional-Grade Short Squeeze Analysis</p>
        </div>
        <div class="form-group">
            <label for="ortexKey">Ortex API Key:</label>
            <input type="password" id="ortexKey" placeholder="Enter your Ortex API key">
        </div>
        <div class="form-group">
            <label for="tickerList">Stock Tickers:</label>
            <textarea id="tickerList" rows="3" placeholder="GME, AMC, TSLA">GME, AMC, TSLA</textarea>
        </div>
        <button onclick="performScan()">🔍 Start Squeeze Scan</button>
        <div id="results" class="results" style="display:none;"></div>
    </div>
    <script>
        async function performScan() {
            const ortexKey = document.getElementById('ortexKey').value;
            const tickers = document.getElementById('tickerList').value;
            if (!ortexKey) { alert('Please enter Ortex API key'); return; }
            
            document.getElementById('results').innerHTML = 'Scanning...';
            document.getElementById('results').style.display = 'block';
            
            try {
                const response = await fetch('/api/squeeze/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ortex_key: ortexKey, tickers: tickers })
                });
                const data = await response.json();
                
                if (data.success) {
                    let html = '<h3>Scan Results:</h3>';
                    data.results.forEach(result => {
                        html += `<div style="margin: 10px 0; padding: 10px; border: 1px solid #555; border-radius: 5px;">
                            <strong>${result.ticker}</strong> - Score: ${result.squeeze_score}/100<br>
                            Price: $${result.current_price} (${result.price_change_pct}%)<br>
                            Short Interest: ${result.ortex_data.short_interest}%
                        </div>`;
                    });
                    document.getElementById('results').innerHTML = html;
                } else {
                    document.getElementById('results').innerHTML = 'Error: ' + (data.error || data.message);
                }
            } catch (error) {
                document.getElementById('results').innerHTML = 'Network error: ' + error.message;
            }
        }
    </script>
</body>
</html>
        '''
