
    
    $(function() {
        "use strict";
        // ============================================================== 
        // Product Sales
        // ============================================================== 
        /*
        new Chartist.Bar('.ct-chart-product', {
            labels: ['Q1', 'Q2', 'Q3', 'Q4'],
            series: [
                [800000, 1200000, 1400000, 1300000],
                [200000, 400000, 500000, 300000],
                [100000, 200000, 400000, 600000]
            ]
        }, {
            stackBars: true,
            axisY: {
                labelInterpolationFnc: function(value) {
                    return (value / 1000) + 'k';
                }
            }
        }).on('draw', function(data) {
            if (data.type === 'bar') {
                data.element.attr({
                    style: 'stroke-width: 40px'
                });
            }
        });*/
    });




    // ============================================================== 
    // Ventas por producto en los últimos 30 días
    // ============================================================== 

    data = {
        datasets: [{
            data: series_most_sold_products,
            backgroundColor: labels_backgroundColors
        }],
        labels: labels_most_sold_products
    };

    options = {
        tooltips: {
            enabled: false
        },
        plugins: {
            datalabels: {
                formatter: (value, ctx) => {
                    let sum = 0;
                    let dataArr = ctx.chart.data.datasets[0].data;
                    dataArr.map(data => {
                        sum += data;
                    });
                    let percentage = (value*100 / sum).toFixed(2)+"%";
                    return percentage;
                },
                color: '#fff',
            }
        }
        
    };

    var ctx = document.getElementById('myPieChart').getContext('2d');
    var myPieChart = new Chart(ctx, {
        type: 'pie',
        data: data,
        options: options
    });


