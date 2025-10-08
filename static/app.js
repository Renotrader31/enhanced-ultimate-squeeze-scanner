// Options Scanner Pro - Frontend JavaScript
class OptionsScanner {
    constructor() {
        this.results = [];
        this.isScanning = false;
        this.init();
    }

    init() {
        console.log('Options Scanner Pro initialized');
        this.setupEventListeners();
        this.updateTickers();
    }

    setupEventListeners() {
        // Add any additional event listeners here
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.runScan();
            }
        });
    }

    updateTickers() {
        const preset = document.getElementById('tickerPreset').value;
        const tickerList = document.getElementById('tickerList');
        
        const presets = {
            // High short interest and squeeze potential stocks
            'squeeze_targets': 'GME, AMC, BBBY, ATER, SPRT, IRNT, OPAD, MRIN, BGFV, PROG, FFIE, MULN, REV, SNDL, CLOV, WKHS, WISH, SDC, ROOT, RIDE, GOEV, NKLA, LCID, RIVN, VRM, CVNA, OPEN, UPST, AFRM, BYND, SNOW, DAVE, APRN, GETY, GNS, RDBX',
            
            // Extended mega cap technology
            'mega_tech': 'AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA, TSM, AVGO, ORCL, ADBE, CRM, AMD, INTC, QCOM, IBM, TXN, INTU, AMAT, MU, LRCX, KLAC, ASML, ARM, PLTR',
            
            // Popular ETFs across sectors
            'etfs': 'SPY, QQQ, IWM, DIA, VOO, VTI, XLF, XLE, GLD, SLV, ARKK, ARKG, ARKQ, ARKW, ARKF, VNQ, EEM, EFA, TLT, HYG, LQD, AGG, GDX, GDXJ, USO, UNG, SQQQ, TQQQ, UVXY, VXX, SPXU, SPXL',
            
            // Meme stocks and Reddit favorites  
            'meme': 'GME, AMC, BBBY, BB, NOK, PLTR, CLOV, WISH, SNDL, TLRY, RKT, SOFI, HOOD, DKNG, COIN, RBLX, PTON, SPCE, NKLA, RIDE, WKHS, GOEV, LCID, RIVN, FSR, FFIE, MULN',
            
            // Semiconductor and chip stocks
            'semiconductors': 'NVDA, AMD, INTC, AVGO, QCOM, TXN, MU, MRVL, AMAT, LRCX, KLAC, ASML, TSM, ADI, NXPI, MCHP, ON, SWKS, QRVO, MPWR, ENTG, WOLF, SLAB, CRUS, ALGM, RMBS, INDI, SMTC',
            
            // AI and Machine Learning plays
            'ai_stocks': 'NVDA, MSFT, GOOGL, PLTR, AI, PATH, SNOW, DDOG, MDB, NET, CRWD, ZS, OKTA, PANW, FTNT, S, ESTC, SUMO, SPLK, NOW, ADBE, CRM, ORCL, IBM, AMZN, META, AAPL, TSLA, UPST, AFRM',
            
            // Electric Vehicle ecosystem
            'ev_stocks': 'TSLA, RIVN, LCID, NIO, XPEV, LI, FSR, FFIE, MULN, GOEV, RIDE, WKHS, NKLA, PTRA, LEV, CHPT, EVGO, BLNK, WBX, QS, MVST, SES, SLDP, FREY, GM, F, STLA',
            
            // Biotech and pharmaceutical
            'biotech': 'MRNA, BNTX, PFE, JNJ, ABBV, LLY, MRK, GILD, AMGN, REGN, VRTX, BIIB, ALNY, BMRN, SGEN, INCY, EXEL, HALO, SRPT, BLUE, EDIT, CRSP, NTLA, BEAM, PACB, ILMN, TMO, DHR',
            
            // Financial sector leaders
            'financials': 'JPM, BAC, WFC, GS, MS, C, BLK, SCHW, AXP, V, MA, PYPL, SQ, COIN, HOOD, SOFI, UPST, AFRM, BRK.B, PNC, USB, TFC, COF, DFS, SYF, AIG, MET, PRU, AFL',
            
            // Energy and commodities
            'energy': 'XOM, CVX, COP, SLB, EOG, PXD, MPC, PSX, VLO, OXY, HAL, BKR, DVN, FANG, HES, APA, MRO, CLR, CTRA, CPE, SM, RRC, AR, BTU, ARCH, USO, UNG, UCO, SCO',
            
            // Chinese ADRs and emerging markets
            'chinese_adrs': 'BABA, JD, BIDU, NIO, XPEV, LI, PDD, BILI, IQ, VIPS, TME, WB, DIDI, TAL, EDU, BEKE, FUTU, TIGR, DADA, YMM, BZUN, HUYA, DOYU, RLX, TUYA, KC, GOTU',
            
            // Cannabis sector
            'cannabis': 'TLRY, CGC, ACB, CRON, SNDL, HEXO, OGI, VFF, GRWG, IIPR, CURA, GTII, TRUL, CL, APHA, KERN, CURF, JUSHF, TCNNF, CRLBF, HRVSF, FFNTF',
            
            // Space exploration
            'space': 'SPCE, RKLB, ASTR, RDW, ASTS, MNTS, PL, SATS, LUNR, IRDM, LMT, NOC, BA, RTX, HON, AJRD, HEI, TDG, SPR, KTOS, AVAV, LHX, LDOS, SAIC',
            
            // Gaming and esports
            'gaming': 'RBLX, EA, TTWO, ATVI, U, DKNG, PENN, WYNN, LVS, MGM, CZR, BYD, EVRI, IGT, SGMS, GMBL, GNOG, RSI, SCR, BETZ, ESPO, HERO, GAMR, BJK',
            
            // Streaming and entertainment
            'streaming': 'NFLX, DIS, ROKU, PARA, WBD, CMCSA, T, FUBO, PTON, SPOT, TME, IQ, BILI, RBLX, EA, TTWO, ATVI, U, SONO, GPRO',
            
            // Retail and e-commerce
            'retail': 'AMZN, WMT, HD, COST, TGT, CVS, WBA, LOW, BABA, JD, PDD, SHOP, ETSY, W, CHWY, RVLV, WISH, FTCH, REAL, CPNG, MELI, SE, EBAY, OSTK',
            
            // Renewable energy
            'renewable': 'ENPH, SEDG, RUN, NOVA, SPWR, FSLR, CSIQ, JKS, NEP, BEP, ICLN, TAN, FAN, QCLN, PBW, ACES, RAYS, SMOG, NEE, AEP, D, DUK, SO, EXC, XEL',
            
            // Healthcare providers
            'healthcare': 'UNH, JNJ, PFE, ABBV, TMO, DHR, CVS, ABT, LLY, MRK, BMY, AMGN, GILD, MDT, ISRG, SYK, BDX, BSX, EW, ZBH, HOLX, ALGN, DXCM, TDOC, DOCS',
            
            // REITs
            'reits': 'AMT, PLD, CCI, EQIX, PSA, O, WELL, SPG, AVB, EQR, DLR, INVH, MAA, UDR, EXR, CUBE, IRM, PEAK, VTR, SBAC, WY, HST, VICI, GLPI',
            
            // Custom selection
            'custom': tickerList.value || 'AAPL, MSFT, NVDA'
        };

        if (preset !== 'custom') {
            tickerList.value = presets[preset];
        }
    }

    updateDTE() {
        const value = document.getElementById('daysToExp').value;
        document.getElementById('dteValue').textContent = value;
    }

    updateReturn() {
        const value = document.getElementById('minReturn').value;
        document.getElementById('returnValue').textContent = value;
    }

    async runScan() {
        if (this.isScanning) {
            this.showAlert('Scan already in progress', 'warning');
            return;
        }

        this.isScanning = true;
        this.showLoading(true);
        this.hideAllSections();
        this.updateScanStatus('Scanning...', 'warning');

        try {
            // Gather form data
            const scanData = this.gatherScanData();
            
            // Validate inputs
            if (!this.validateInputs(scanData)) {
                return;
            }

            // Make API call
            const response = await fetch('/api/scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(scanData)
            });

            const result = await response.json();

            if (result.success) {
                this.results = result.results;
                this.displayResults();
                this.updateScanStatus(`Found ${result.count} opportunities`, 'success');
            } else {
                this.showAlert(`Scan failed: ${result.error || result.message}`, 'danger');
                this.updateScanStatus('Scan failed', 'danger');
            }

        } catch (error) {
            console.error('Scan error:', error);
            this.showAlert(`Network error: ${error.message}`, 'danger');
            this.updateScanStatus('Error', 'danger');
        } finally {
            this.isScanning = false;
            this.showLoading(false);
        }
    }

    gatherScanData() {
        const tickerText = document.getElementById('tickerList').value;
        const tickers = tickerText.split(',').map(t => t.trim().toUpperCase()).filter(t => t);

        return {
            polygon_key: document.getElementById('polygonKey').value.trim(),
            uw_key: document.getElementById('uwKey').value.trim(),
            ortex_key: document.getElementById('ortexKey').value.trim(),
            tickers: tickers,
            days_to_exp: parseInt(document.getElementById('daysToExp').value),
            min_return: parseInt(document.getElementById('minReturn').value),
            strategies: ['Long Calls', 'Long Puts', 'Bull Call Spreads', 'Bear Put Spreads', 'Cash-Secured Puts']
        };
    }

    async runSqueezeScan() {
        if (this.isScanning) {
            this.showAlert('Scan already in progress', 'warning');
            return;
        }

        this.isScanning = true;
        this.showLoading(true);
        this.hideAllSections();
        this.updateScanStatus('🔥 Scanning for Squeezes...', 'danger');

        try {
            const scanData = this.gatherScanData();
            
            // Validate Ortex key for squeeze scanning
            if (!scanData.ortex_key && !scanData.uw_key) {
                this.showAlert('Ortex or Unusual Whales API key required for squeeze scanning', 'warning');
                this.updateScanStatus('Missing API key', 'warning');
                return;
            }

            if (!scanData.tickers || scanData.tickers.length === 0) {
                this.showAlert('Please enter at least one ticker symbol', 'warning');
                this.updateScanStatus('Missing tickers', 'warning');
                return;
            }

            // Make squeeze scan API call
            const response = await fetch('/api/squeeze/scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ortex_key: scanData.ortex_key,
                    polygon_key: scanData.polygon_key,
                    uw_key: scanData.uw_key,
                    tickers: scanData.tickers,
                    min_score: 20
                })
            });

            const result = await response.json();

            if (result.success) {
                this.results = result.results;
                this.displaySqueezeResults();
                this.updateScanStatus(`🚨 Found ${result.count} squeeze candidates!`, 'danger');
            } else {
                this.showAlert(`Squeeze scan failed: ${result.error || result.message}`, 'danger');
                this.updateScanStatus('Squeeze scan failed', 'danger');
            }

        } catch (error) {
            console.error('Squeeze scan error:', error);
            this.showAlert(`Network error: ${error.message}`, 'danger');
            this.updateScanStatus('Error', 'danger');
        } finally {
            this.isScanning = false;
            this.showLoading(false);
        }
    }

    displaySqueezeResults() {
        if (!this.results || this.results.length === 0) {
            this.showNoResults();
            return;
        }

        this.updateSqueezeResultsSummary();
        this.populateSqueezeResultsTable();
        this.createSqueezeCharts();
        this.showResultsSection();
    }

    updateSqueezeResultsSummary() {
        const results = this.results;
        
        // Calculate squeeze metrics
        const totalCandidates = results.length;
        const scores = results.map(r => parseFloat(r.squeeze_score) || 0);
        const bestScore = Math.max(...scores);
        const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
        
        // Count extreme risks
        const extremeRisks = results.filter(r => parseFloat(r.squeeze_score) >= 80).length;
        const highRisks = results.filter(r => parseFloat(r.squeeze_score) >= 60).length;

        // Get top candidate
        const topCandidate = results[0]?.ticker || 'N/A';

        // Update DOM
        document.getElementById('totalOps').textContent = totalCandidates.toLocaleString();
        document.getElementById('bestReturn').textContent = `${bestScore.toFixed(0)}`;
        document.getElementById('avgReturn').textContent = `${avgScore.toFixed(0)}`;
        document.getElementById('topStrategy').textContent = extremeRisks > 0 ? `${extremeRisks} EXTREME` : `${highRisks} HIGH RISK`;
        document.getElementById('avgDTE').textContent = topCandidate;

        document.getElementById('resultsSummary').classList.remove('d-none');
        document.getElementById('resultsSummary').classList.add('fade-in');
    }

    populateSqueezeResultsTable() {
        const tbody = document.getElementById('resultsBody');
        tbody.innerHTML = '';

        // Update table headers for squeeze data
        const thead = document.querySelector('#resultsTable thead tr');
        thead.innerHTML = `
            <th>Ticker</th>
            <th>Squeeze Score</th>
            <th>Risk Level</th>
            <th>Short Interest %</th>
            <th>Days to Cover</th>
            <th>Utilization %</th>
            <th>Cost to Borrow</th>
            <th>Gamma Exposure</th>
            <th>Alert Level</th>
        `;

        this.results.forEach(result => {
            const row = document.createElement('tr');
            
            const scoreClass = this.getSqueezeScoreClass(parseFloat(result.squeeze_score) || 0);
            const riskClass = this.getRiskLevelClass(result.squeeze_type);
            
            const ortexData = result.ortex_data || {};
            const gammaData = result.gamma_data || {};
            
            row.innerHTML = `
                <td><strong>${result.ticker}</strong></td>
                <td class="${scoreClass}">${result.squeeze_score?.toFixed(0) || 0}</td>
                <td class="${riskClass}">${result.squeeze_type}</td>
                <td>${this.formatPercentage(ortexData.short_interest)}</td>
                <td>${ortexData.days_to_cover?.toFixed(1) || '-'}</td>
                <td>${this.formatPercentage(ortexData.utilization)}</td>
                <td>${this.formatPercentage(ortexData.cost_to_borrow)}</td>
                <td>${this.formatNumber(gammaData.net_gamma)}</td>
                <td class="${this.getAlertClass(result.squeeze_score)}">${this.getAlertLevel(result.squeeze_score)}</td>
            `;

            tbody.appendChild(row);
        });

        document.getElementById('resultsTable').classList.remove('d-none');
        document.getElementById('resultsTable').classList.add('fade-in');
    }

    validateInputs(data) {
        if (!data.polygon_key && !data.uw_key) {
            this.showAlert('Please enter at least one API key', 'warning');
            this.updateScanStatus('Missing API key', 'warning');
            return false;
        }

        if (!data.tickers || data.tickers.length === 0) {
            this.showAlert('Please enter at least one ticker symbol', 'warning');
            this.updateScanStatus('Missing tickers', 'warning');
            return false;
        }

        return true;
    }

    displayResults() {
        if (!this.results || this.results.length === 0) {
            this.showNoResults();
            return;
        }

        this.updateResultsSummary();
        this.populateResultsTable();
        this.createCharts();
        this.showResultsSection();
    }

    updateResultsSummary() {
        const results = this.results;
        
        // Calculate summary metrics
        const totalOps = results.length;
        const returns = results.map(r => parseFloat(r.return) || 0);
        const bestReturn = Math.max(...returns);
        const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
        
        // Get strategy counts
        const strategyCounts = {};
        results.forEach(r => {
            strategyCounts[r.strategy] = (strategyCounts[r.strategy] || 0) + 1;
        });
        const topStrategy = Object.keys(strategyCounts).reduce((a, b) => 
            strategyCounts[a] > strategyCounts[b] ? a : b
        );

        // Average DTE
        const dtes = results.map(r => parseInt(r.dte) || 0).filter(d => d > 0);
        const avgDTE = dtes.length > 0 ? Math.round(dtes.reduce((a, b) => a + b, 0) / dtes.length) : 0;

        // Update DOM
        document.getElementById('totalOps').textContent = totalOps.toLocaleString();
        document.getElementById('bestReturn').textContent = `${bestReturn.toFixed(1)}%`;
        document.getElementById('avgReturn').textContent = `${avgReturn.toFixed(1)}%`;
        document.getElementById('topStrategy').textContent = topStrategy.substring(0, 15) + (topStrategy.length > 15 ? '...' : '');
        document.getElementById('avgDTE').textContent = `${avgDTE}d`;

        document.getElementById('resultsSummary').classList.remove('d-none');
        document.getElementById('resultsSummary').classList.add('fade-in');
    }

    populateResultsTable() {
        const tbody = document.getElementById('resultsBody');
        tbody.innerHTML = '';

        // Show top 50 results
        const displayResults = this.results.slice(0, 50);

        displayResults.forEach(result => {
            const row = document.createElement('tr');
            
            const returnClass = this.getReturnClass(parseFloat(result.return) || 0);
            
            row.innerHTML = `
                <td><strong>${result.ticker}</strong></td>
                <td>${result.strategy}</td>
                <td class="${returnClass}">${this.formatReturn(result.return)}</td>
                <td>${this.formatCurrency(result.current_price)}</td>
                <td>${this.formatCurrency(result.strike)}</td>
                <td>${this.formatDate(result.expiration)}</td>
                <td>${result.dte || '-'}</td>
                <td>${this.formatPercentage(result.iv)}</td>
                <td>${this.formatCurrency(result.premium)}</td>
            `;

            tbody.appendChild(row);
        });

        document.getElementById('resultsTable').classList.remove('d-none');
        document.getElementById('resultsTable').classList.add('fade-in');
    }

    createCharts() {
        this.createReturnDistributionChart();
        this.createStrategyChart();
        document.getElementById('chartsSection').classList.remove('d-none');
        document.getElementById('chartsSection').classList.add('fade-in');
    }

    createReturnDistributionChart() {
        const returns = this.results.map(r => parseFloat(r.return) || 0);
        
        const trace = {
            x: returns,
            type: 'histogram',
            nbinsx: 20,
            marker: {
                color: returns,
                colorscale: [[0, '#667eea'], [0.5, '#00ff88'], [1, '#00d4ff']],
                line: { color: '#2a2a3e', width: 1 }
            },
            hovertemplate: 'Return: %{x:.1f}%<br>Count: %{y}<extra></extra>'
        };

        const layout = {
            title: {
                text: 'Return Distribution',
                font: { color: '#00ff88', size: 16 }
            },
            xaxis: { 
                title: 'Return (%)',
                gridcolor: '#2a2a3e',
                color: '#e0e0e0'
            },
            yaxis: { 
                title: 'Count',
                gridcolor: '#2a2a3e',
                color: '#e0e0e0'
            },
            plot_bgcolor: '#1a1a2e',
            paper_bgcolor: '#1a1a2e',
            font: { color: '#e0e0e0' },
            height: 300,
            margin: { t: 50, b: 50, l: 50, r: 50 }
        };

        Plotly.newPlot('returnChart', [trace], layout, { displayModeBar: false });
    }

    createStrategyChart() {
        const strategyCounts = {};
        this.results.forEach(r => {
            strategyCounts[r.strategy] = (strategyCounts[r.strategy] || 0) + 1;
        });

        const strategies = Object.keys(strategyCounts);
        const counts = Object.values(strategyCounts);

        const trace = {
            labels: strategies,
            values: counts,
            type: 'pie',
            hole: 0.6,
            marker: {
                colors: ['#667eea', '#00ff88', '#00d4ff', '#ff6b6b', '#ffd93d', '#a8e6cf', '#ff8cc8', '#6bcf7f'],
                line: { color: '#1a1a2e', width: 2 }
            },
            textposition: 'outside',
            textinfo: 'label+percent',
            hovertemplate: '%{label}<br>Count: %{value}<br>%{percent}<extra></extra>'
        };

        const layout = {
            title: {
                text: 'Strategy Distribution',
                font: { color: '#00ff88', size: 16 }
            },
            plot_bgcolor: '#1a1a2e',
            paper_bgcolor: '#1a1a2e',
            font: { color: '#e0e0e0' },
            height: 300,
            showlegend: false,
            margin: { t: 50, b: 50, l: 50, r: 50 },
            annotations: [{
                text: `${strategies.length}<br>Strategies`,
                x: 0.5, y: 0.5,
                font: { size: 16, color: '#00ff88' },
                showarrow: false
            }]
        };

        Plotly.newPlot('strategyChart', [trace], layout, { displayModeBar: false });
    }

    // Utility Methods
    getReturnClass(returnValue) {
        if (returnValue >= 30) return 'return-high';
        if (returnValue >= 15) return 'return-medium';
        return 'return-low';
    }

    formatCurrency(value) {
        if (!value || value === '' || isNaN(value)) return '-';
        return `$${parseFloat(value).toFixed(2)}`;
    }

    formatPercentage(value) {
        if (!value || value === '' || isNaN(value)) return '-';
        return `${parseFloat(value).toFixed(1)}%`;
    }

    formatReturn(value) {
        if (!value || value === '' || isNaN(value)) return '-';
        const num = parseFloat(value);
        return `${num.toFixed(1)}%`;
    }

    formatDate(dateStr) {
        if (!dateStr) return '-';
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        } catch {
            return dateStr;
        }
    }

    formatNumber(value) {
        if (!value || value === '' || isNaN(value)) return '-';
        return parseFloat(value).toLocaleString();
    }

    getSqueezeScoreClass(score) {
        if (score >= 80) return 'text-danger fw-bold';
        if (score >= 60) return 'text-warning fw-bold';
        if (score >= 40) return 'text-info';
        return 'text-light';
    }

    getRiskLevelClass(riskLevel) {
        if (riskLevel?.includes('EXTREME')) return 'text-danger fw-bold';
        if (riskLevel?.includes('High')) return 'text-warning';
        if (riskLevel?.includes('Moderate')) return 'text-info';
        return 'text-muted';
    }

    getAlertClass(score) {
        if (score >= 80) return 'badge bg-danger';
        if (score >= 60) return 'badge bg-warning';
        if (score >= 40) return 'badge bg-info';
        return 'badge bg-secondary';
    }

    getAlertLevel(score) {
        if (score >= 80) return 'CRITICAL';
        if (score >= 60) return 'HIGH';
        if (score >= 40) return 'MEDIUM';
        return 'LOW';
    }

    createSqueezeCharts() {
        this.createSqueezeScoreChart();
        this.createRiskDistributionChart();
        document.getElementById('chartsSection').classList.remove('d-none');
        document.getElementById('chartsSection').classList.add('fade-in');
    }

    createSqueezeScoreChart() {
        const scores = this.results.map(r => parseFloat(r.squeeze_score) || 0);
        const tickers = this.results.map(r => r.ticker);
        
        const trace = {
            x: tickers,
            y: scores,
            type: 'bar',
            marker: {
                color: scores.map(score => {
                    if (score >= 80) return '#dc3545';
                    if (score >= 60) return '#ffc107'; 
                    if (score >= 40) return '#0dcaf0';
                    return '#6c757d';
                }),
                line: { color: '#2a2a3e', width: 1 }
            },
            hovertemplate: '%{x}<br>Squeeze Score: %{y:.0f}<extra></extra>'
        };

        const layout = {
            title: {
                text: '🔥 Squeeze Risk Scores',
                font: { color: '#ff6b6b', size: 16 }
            },
            xaxis: { 
                title: 'Ticker',
                gridcolor: '#2a2a3e',
                color: '#e0e0e0'
            },
            yaxis: { 
                title: 'Squeeze Score',
                gridcolor: '#2a2a3e',
                color: '#e0e0e0',
                range: [0, 100]
            },
            plot_bgcolor: '#1a1a2e',
            paper_bgcolor: '#1a1a2e',
            font: { color: '#e0e0e0' },
            height: 300,
            margin: { t: 50, b: 50, l: 50, r: 50 }
        };

        Plotly.newPlot('returnChart', [trace], layout, { displayModeBar: false });
    }

    createRiskDistributionChart() {
        const riskCounts = {};
        this.results.forEach(r => {
            const risk = r.squeeze_type;
            riskCounts[risk] = (riskCounts[risk] || 0) + 1;
        });

        const risks = Object.keys(riskCounts);
        const counts = Object.values(riskCounts);

        const trace = {
            labels: risks,
            values: counts,
            type: 'pie',
            hole: 0.6,
            marker: {
                colors: ['#dc3545', '#ffc107', '#0dcaf0', '#6c757d'],
                line: { color: '#1a1a2e', width: 2 }
            },
            textposition: 'outside',
            textinfo: 'label+percent',
            hovertemplate: '%{label}<br>Count: %{value}<br>%{percent}<extra></extra>'
        };

        const layout = {
            title: {
                text: '⚠️ Risk Level Distribution',
                font: { color: '#ff6b6b', size: 16 }
            },
            plot_bgcolor: '#1a1a2e',
            paper_bgcolor: '#1a1a2e',
            font: { color: '#e0e0e0' },
            height: 300,
            showlegend: false,
            margin: { t: 50, b: 50, l: 50, r: 50 },
            annotations: [{
                text: `${risks.length}<br>Risk Levels`,
                x: 0.5, y: 0.5,
                font: { size: 16, color: '#ff6b6b' },
                showarrow: false
            }]
        };

        Plotly.newPlot('strategyChart', [trace], layout, { displayModeBar: false });
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.remove('d-none');
        } else {
            loading.classList.add('d-none');
        }
    }

    showAlert(message, type = 'danger') {
        const alert = document.getElementById('errorAlert');
        const messageEl = document.getElementById('errorMessage');
        
        alert.className = `alert alert-${type}`;
        messageEl.textContent = message;
        alert.classList.remove('d-none');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            alert.classList.add('d-none');
        }, 5000);
    }

    updateScanStatus(message, type) {
        const status = document.getElementById('scanStatus');
        status.textContent = message;
        status.className = `badge bg-${type}`;
    }

    hideAllSections() {
        ['errorAlert', 'resultsSummary', 'resultsTable', 'chartsSection', 'noResults'].forEach(id => {
            document.getElementById(id).classList.add('d-none');
        });
        // Hide export button
        document.getElementById('exportBtn').classList.add('d-none');
    }

    showResultsSection() {
        // Results are shown by individual methods
        // Show export button
        document.getElementById('exportBtn').classList.remove('d-none');
    }

    showNoResults() {
        document.getElementById('noResults').classList.remove('d-none');
        document.getElementById('noResults').classList.add('fade-in');
        this.updateScanStatus('No results', 'secondary');
    }

    // Enhanced squeeze detection helper methods
    getSqueezeScoreClass(score) {
        if (score >= 80) return 'text-danger fw-bold';
        if (score >= 60) return 'text-warning fw-bold';
        if (score >= 40) return 'text-info';
        return 'text-muted';
    }

    getRiskLevelClass(type) {
        if (type === 'EXTREME SQUEEZE RISK') return 'badge bg-danger';
        if (type === 'High Squeeze Risk') return 'badge bg-warning text-dark';
        if (type === 'Moderate Squeeze Risk') return 'badge bg-info';
        return 'badge bg-secondary';
    }

    getAlertClass(score) {
        if (score >= 80) return 'text-danger animate-pulse';
        if (score >= 60) return 'text-warning';
        return '';
    }

    getAlertLevel(score) {
        if (score >= 80) return '🚨 CRITICAL';
        if (score >= 60) return '⚠️ HIGH';
        if (score >= 40) return '👀 WATCH';
        return '📊 MONITOR';
    }

    formatPercentage(value) {
        if (value === null || value === undefined) return '-';
        return `${value.toFixed(2)}%`;
    }

    formatNumber(value) {
        if (value === null || value === undefined) return '-';
        if (value > 1000000) return `${(value/1000000).toFixed(2)}M`;
        if (value > 1000) return `${(value/1000).toFixed(2)}K`;
        return value.toFixed(2);
    }

    // Add real-time alert monitoring
    startAlertMonitoring() {
        if (this.alertMonitor) clearInterval(this.alertMonitor);
        
        this.alertMonitor = setInterval(() => {
            this.checkForCriticalSqueezes();
        }, 30000); // Check every 30 seconds
    }

    checkForCriticalSqueezes() {
        if (!this.results || this.results.length === 0) return;
        
        const criticalSqueezes = this.results.filter(r => 
            parseFloat(r.squeeze_score) >= 80
        );
        
        if (criticalSqueezes.length > 0) {
            const tickers = criticalSqueezes.map(r => r.ticker).join(', ');
            this.showNotification(`🚨 CRITICAL SQUEEZE ALERT: ${tickers}`, 'danger');
        }
    }

    showNotification(message, type = 'info') {
        // Create floating notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} position-fixed`;
        notification.style.cssText = `
            top: 80px;
            right: 20px;
            z-index: 10000;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideIn 0.3s ease;
        `;
        notification.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>${message}</span>
                <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 10000);
    }
}

// Global functions for HTML onclick handlers
function updateTickers() {
    scanner.updateTickers();
}

function updateDTE() {
    scanner.updateDTE();
}

function updateReturn() {
    scanner.updateReturn();
}

function runScan() {
    scanner.runScan();
}

function runSqueezeScan() {
    scanner.runSqueezeScan();
}

// Add ticker search functionality
function handleTickerSearch(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        const searchInput = document.getElementById('tickerSearch');
        const tickerList = document.getElementById('tickerList');
        const newTicker = searchInput.value.trim().toUpperCase();
        
        if (newTicker) {
            // Add to existing list
            const currentTickers = tickerList.value.split(',').map(t => t.trim());
            if (!currentTickers.includes(newTicker)) {
                currentTickers.push(newTicker);
                tickerList.value = currentTickers.filter(t => t).join(', ');
                searchInput.value = '';
                
                // Show success message
                showQuickAlert(`Added ${newTicker} to scan list`, 'success');
            } else {
                showQuickAlert(`${newTicker} already in list`, 'warning');
            }
        }
    }
}

// Quick alert helper
function showQuickAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.textContent = message;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 2000);
}

// Export results to CSV
function exportResults() {
    if (!scanner.results || scanner.results.length === 0) {
        showQuickAlert('No results to export', 'warning');
        return;
    }
    
    // Prepare CSV data
    let csvContent = "data:text/csv;charset=utf-8,";
    
    // Add headers based on result type
    if (scanner.results[0].squeeze_score !== undefined) {
        // Squeeze scan results
        csvContent += "Ticker,Squeeze Score,Risk Level,Short Interest %,Days to Cover,Utilization %,Cost to Borrow,Gamma Exposure,Alert Level\\n";
        
        scanner.results.forEach(result => {
            const ortexData = result.ortex_data || {};
            const gammaData = result.gamma_data || {};
            csvContent += `${result.ticker},${result.squeeze_score || 0},${result.squeeze_type},${ortexData.short_interest || '-'},${ortexData.days_to_cover || '-'},${ortexData.utilization || '-'},${ortexData.cost_to_borrow || '-'},${gammaData.net_gamma || '-'},${scanner.getAlertLevel(result.squeeze_score)}\\n`;
        });
    } else {
        // Regular scan results
        csvContent += "Ticker,Strike,Type,Expiry,Return %,IV,Volume,OI,Strategy,Premium,Delta,Gamma,Theta,Vega\\n";
        
        scanner.results.forEach(result => {
            csvContent += `${result.ticker},${result.strike},${result.type},${result.expiry},${result.return},${result.iv || '-'},${result.volume || '-'},${result.oi || '-'},${result.strategy || '-'},${result.premium || '-'},${result.delta || '-'},${result.gamma || '-'},${result.theta || '-'},${result.vega || '-'}\\n`;
        });
    }
    
    // Create download link
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const filename = scanner.results[0].squeeze_score !== undefined ? 
        `squeeze_scan_${timestamp}.csv` : 
        `options_scan_${timestamp}.csv`;
    
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showQuickAlert(`Exported ${scanner.results.length} results to ${filename}`, 'success');
}

// Initialize the scanner when DOM is loaded
let scanner;
document.addEventListener('DOMContentLoaded', function() {
    scanner = new OptionsScanner();
    initializeLiveTicker();
    startLiveUpdates();
});

// Live ticker functionality
function initializeLiveTicker() {
    updateLiveTicker();
    setInterval(updateLiveTicker, 5000); // Update every 5 seconds
}

function updateLiveTicker() {
    // Sample tickers with simulated price updates
    const popularTickers = [
        { symbol: 'SPY', name: 'S&P 500' },
        { symbol: 'QQQ', name: 'NASDAQ' },
        { symbol: 'GME', name: 'GameStop' },
        { symbol: 'AMC', name: 'AMC' },
        { symbol: 'NVDA', name: 'NVIDIA' },
        { symbol: 'AAPL', name: 'Apple' },
        { symbol: 'TSLA', name: 'Tesla' },
        { symbol: 'META', name: 'Meta' },
        { symbol: 'MSFT', name: 'Microsoft' },
        { symbol: 'BBBY', name: 'Bed Bath' }
    ];
    
    let tickerHTML = '';
    popularTickers.forEach(ticker => {
        // Simulate price and change
        const price = (Math.random() * 500 + 50).toFixed(2);
        const change = (Math.random() * 10 - 5).toFixed(2);
        const changeClass = change >= 0 ? 'ticker-up' : 'ticker-down';
        const arrow = change >= 0 ? '▲' : '▼';
        
        tickerHTML += `
            <span class="ticker-item">
                <span class="ticker-symbol">${ticker.symbol}</span>
                <span class="${changeClass}">
                    $${price} ${arrow} ${Math.abs(change)}%
                </span>
            </span>
        `;
    });
    
    document.getElementById('tickerContent').innerHTML = tickerHTML;
}

// Start live updates for squeeze alerts
function startLiveUpdates() {
    // Check for critical squeezes every 30 seconds
    setInterval(() => {
        if (scanner && scanner.results && scanner.results.length > 0) {
            scanner.checkForCriticalSqueezes();
        }
    }, 30000);
}

// Watchlist functions
function addToWatchlist() {
    const ticker = document.getElementById('watchlistTicker').value.trim().toUpperCase();
    const target = parseInt(document.getElementById('watchlistTarget').value) || 60;
    
    if (!ticker) {
        showQuickAlert('Please enter a ticker symbol', 'warning');
        return;
    }
    
    if (squeezeMonitor && squeezeMonitor.addToWatchlist(ticker, target)) {
        document.getElementById('watchlistTicker').value = '';
        document.getElementById('watchlistTarget').value = '60';
        squeezeMonitor.updateWatchlistDisplay();
    } else {
        showQuickAlert(`${ticker} is already in watchlist`, 'info');
    }
}
