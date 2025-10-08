// Squeeze Comparison Chart Component
class SqueezeComparisonChart {
    constructor() {
        this.chartData = [];
        this.selectedTickers = [];
        this.chartType = 'radar';
    }

    addTickerToComparison(ticker, data) {
        if (this.selectedTickers.includes(ticker)) {
            showQuickAlert(`${ticker} already in comparison`, 'info');
            return;
        }
        
        if (this.selectedTickers.length >= 5) {
            showQuickAlert('Maximum 5 tickers for comparison', 'warning');
            return;
        }
        
        this.selectedTickers.push(ticker);
        this.chartData.push({
            ticker: ticker,
            data: data
        });
        
        this.updateComparisonChart();
    }

    removeTickerFromComparison(ticker) {
        const index = this.selectedTickers.indexOf(ticker);
        if (index > -1) {
            this.selectedTickers.splice(index, 1);
            this.chartData.splice(index, 1);
            this.updateComparisonChart();
        }
    }

    updateComparisonChart() {
        if (this.chartData.length === 0) {
            document.getElementById('comparisonChart').innerHTML = 
                '<p class="text-muted text-center">Select tickers to compare</p>';
            return;
        }

        if (this.chartType === 'radar') {
            this.createRadarChart();
        } else if (this.chartType === 'bar') {
            this.createBarChart();
        } else if (this.chartType === 'heatmap') {
            this.createHeatmap();
        }
    }

    createRadarChart() {
        const traces = this.chartData.map(item => {
            const ortexData = item.data.ortex_data || {};
            const gammaData = item.data.gamma_data || {};
            
            return {
                type: 'scatterpolar',
                r: [
                    ortexData.short_interest || 0,
                    ortexData.days_to_cover || 0,
                    ortexData.utilization || 0,
                    ortexData.cost_to_borrow || 0,
                    (gammaData.net_gamma / 1000000) || 0,
                    item.data.squeeze_score || 0
                ],
                theta: [
                    'Short Interest %',
                    'Days to Cover',
                    'Utilization %',
                    'Cost to Borrow %',
                    'Net Gamma (M)',
                    'Squeeze Score'
                ],
                fill: 'toself',
                name: item.ticker,
                line: {
                    width: 2
                },
                marker: {
                    size: 8
                }
            };
        });

        const layout = {
            polar: {
                radialaxis: {
                    visible: true,
                    range: [0, 100],
                    gridcolor: '#444',
                    tickfont: { color: '#aaa' }
                },
                angularaxis: {
                    gridcolor: '#444',
                    tickfont: { color: '#aaa' }
                },
                bgcolor: '#1a1a2e'
            },
            showlegend: true,
            legend: {
                font: { color: '#e0e0e0' },
                bgcolor: '#1a1a2e',
                bordercolor: '#444',
                borderwidth: 1
            },
            title: {
                text: 'Squeeze Metrics Comparison',
                font: { color: '#fff', size: 16 }
            },
            paper_bgcolor: '#1a1a2e',
            plot_bgcolor: '#1a1a2e',
            height: 400,
            margin: { t: 50, b: 50, l: 50, r: 50 }
        };

        Plotly.newPlot('comparisonChart', traces, layout, { displayModeBar: false });
    }

    createBarChart() {
        const categories = [
            'Short Interest',
            'Days to Cover',
            'Utilization',
            'Cost to Borrow',
            'Squeeze Score'
        ];

        const traces = categories.map(category => {
            const values = this.chartData.map(item => {
                const ortexData = item.data.ortex_data || {};
                switch(category) {
                    case 'Short Interest':
                        return ortexData.short_interest || 0;
                    case 'Days to Cover':
                        return ortexData.days_to_cover || 0;
                    case 'Utilization':
                        return ortexData.utilization || 0;
                    case 'Cost to Borrow':
                        return ortexData.cost_to_borrow || 0;
                    case 'Squeeze Score':
                        return item.data.squeeze_score || 0;
                    default:
                        return 0;
                }
            });

            return {
                x: this.selectedTickers,
                y: values,
                name: category,
                type: 'bar',
                marker: {
                    line: {
                        width: 1,
                        color: 'rgba(255,255,255,0.2)'
                    }
                }
            };
        });

        const layout = {
            barmode: 'group',
            title: {
                text: 'Squeeze Metrics Comparison',
                font: { color: '#fff', size: 16 }
            },
            xaxis: {
                tickfont: { color: '#aaa' },
                gridcolor: '#444'
            },
            yaxis: {
                title: 'Value',
                tickfont: { color: '#aaa' },
                gridcolor: '#444'
            },
            legend: {
                font: { color: '#e0e0e0' },
                bgcolor: '#1a1a2e',
                bordercolor: '#444',
                borderwidth: 1
            },
            paper_bgcolor: '#1a1a2e',
            plot_bgcolor: '#1a1a2e',
            height: 400
        };

        Plotly.newPlot('comparisonChart', traces, layout, { displayModeBar: false });
    }

    createHeatmap() {
        const metrics = [
            'Squeeze Score',
            'Short Interest',
            'Days to Cover',
            'Utilization',
            'Cost to Borrow',
            'Net Gamma'
        ];

        const zValues = metrics.map(metric => {
            return this.chartData.map(item => {
                const ortexData = item.data.ortex_data || {};
                const gammaData = item.data.gamma_data || {};
                
                switch(metric) {
                    case 'Squeeze Score':
                        return item.data.squeeze_score || 0;
                    case 'Short Interest':
                        return ortexData.short_interest || 0;
                    case 'Days to Cover':
                        return ortexData.days_to_cover || 0;
                    case 'Utilization':
                        return ortexData.utilization || 0;
                    case 'Cost to Borrow':
                        return ortexData.cost_to_borrow || 0;
                    case 'Net Gamma':
                        return (gammaData.net_gamma / 1000000) || 0;
                    default:
                        return 0;
                }
            });
        });

        const trace = {
            x: this.selectedTickers,
            y: metrics,
            z: zValues,
            type: 'heatmap',
            colorscale: [
                [0, '#0a0a1e'],
                [0.2, '#1a1a3e'],
                [0.4, '#3a3a6e'],
                [0.6, '#ff9999'],
                [0.8, '#ff6666'],
                [1, '#ff0000']
            ],
            showscale: true,
            colorbar: {
                tickfont: { color: '#aaa' },
                title: {
                    text: 'Intensity',
                    font: { color: '#aaa' }
                }
            }
        };

        const layout = {
            title: {
                text: 'Squeeze Intensity Heatmap',
                font: { color: '#fff', size: 16 }
            },
            xaxis: {
                tickfont: { color: '#aaa' },
                side: 'bottom'
            },
            yaxis: {
                tickfont: { color: '#aaa' },
                autosize: true
            },
            paper_bgcolor: '#1a1a2e',
            plot_bgcolor: '#1a1a2e',
            height: 400,
            margin: { t: 50, b: 50, l: 100, r: 50 }
        };

        Plotly.newPlot('comparisonChart', [trace], layout, { displayModeBar: false });
    }

    switchChartType(type) {
        this.chartType = type;
        this.updateComparisonChart();
        
        // Update button states
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-chart-type="${type}"]`).classList.add('active');
    }

    clearComparison() {
        this.selectedTickers = [];
        this.chartData = [];
        this.updateComparisonChart();
    }
}

// Initialize comparison chart
let comparisonChart;
document.addEventListener('DOMContentLoaded', function() {
    comparisonChart = new SqueezeComparisonChart();
});
