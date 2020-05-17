
    
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

    var data = {
        datasets: [{
            data: series_most_sold_products,
            backgroundColor: labels_backgroundColors
        }],
        labels: labels_most_sold_products
    };

    var options = {
        tooltips: {
            callbacks: {
                afterLabel: function(tooltipItem, data) {
                    var dataset = data['datasets'][0];
                    var temp = (dataset['data'][tooltipItem['index']]/sales_volumen_last_30)*10000;
                    var percent = Math.round(temp)/100;
                    console.log(dataset);
                    console.log("tooltipItem['index']: "+tooltipItem['index']);
                    console.log("math: "+ dataset['data'][tooltipItem['index']] );
                    console.log("sales_volumen_last_30: "+sales_volumen_last_30);
                    console.log(dataset['data'][tooltipItem['index']]/sales_volumen_last_30*100);
                    
                    return '(' + percent + '%)';
                  }
                //label: function(tooltipItem, data) {
                    //var label = data.datasets[tooltipItem.datasetIndex].label || '';
                    //var label = "Laikitas";
                    //if (label) {
                    //    label += ': ';
                    //}
                    //label += "hola";
                    // Calculate total volume
                    /*
                    var sales_volumen = 0
                    for(var i = 0, size = series_most_sold_products.length; i < size ; i++){
                        var item = series_most_sold_products[i];
                        sales_volumen += item;
                    }
                    if (label) {
                        label += sales_volumen;
                    }*/
                    //return label;
                //}
            }
        }
    };
     
    var ctx = document.getElementById('myPieChart').getContext('2d');
    var myPieChart = new Chart(ctx, {
        type: 'pie',
        data: data,
        options: options
    });


