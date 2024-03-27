<template>
    <Modal v-model="modalOpen" class="modal-backdrop" width="2000" :title="title">
        <div class="modal-content">
            <div ref="earn" style="width: 1800px; height: 200px;"></div>
            <div ref="chart" style="width: 1800px; height: 800px;"></div>
        </div>
    </Modal>
</template>

<script>
import * as echarts from "echarts";

export default {
    props: {
        isOpen: {
            type: Boolean,
            required: true
        },
        dataSeries: {
            type: Object,
            default: null
        }, 
        title: {
            type: String
        }
    },
    computed: {
        modalOpen: {
            get() {
                return this.isOpen;
            },
            set(value) {
                this.$emit('update:isOpen', value);
            }
        }
    }, 
    watch: {
        isOpen(newVal) {
            if (newVal) {
                console.log(newVal)
                this.drawChart();
            }
        }
    },
    methods: {
        closeModal() {
            this.$emit('update:isOpen', false);
        },
        getAccumulatedData: function (data) {
            let accumulated = 0;
            return data.map(item => accumulated += item);
        },
        drawChart() {
            console.log("Draw")
            const chartInstance = echarts.init(this.$refs.chart);
            const earnInstance = echarts.init(this.$refs.earn)

            const earn_option = {
                toolbox: {
                    feature: {
                        dataView: {
                            show: true,   // 默认为 true
                            readOnly: false,  // 默认为 true，只读
                        },
                        // ... 其他工具箱功能
                    }
                },

                grid: [
                    { top: '10%', height: '90%' },
                ],
                tooltip: {
                    trigger: 'axis',
                    // 可选：自定义提示内容的格式
                    formatter: function(params) {
                        var data = params[0].data; // 例如，获取第一个系列的数据
                        return 'Value: ' + data;
                    }
                },
                yAxis: [
                    { type: 'value', gridIndex: 0 },
                ],
                xAxis: [
                    {
                        type: 'category',
                        gridIndex: 0,
                        splitLine: { show: false },
                        axisLabel: { show: false }, // Only show x-axis labels on the last grid/chart
                        boundaryGap: false
                    }, 
                ],
                legend: {
                    data: ['累计收益'],
                    // 根据需要可以添加更多的配置
                },
                series: [
                    { name: '累计收益', type: 'line', data: this.getAccumulatedData(this.dataSeries.earn), xAxisIndex: 0, yAxisIndex: 0 },
                ]
            };

            const option = {
                toolbox: {
                    feature: {
                        dataView: {
                            show: true,   // 默认为 true
                            readOnly: false,  // 默认为 true，只读
                        },
                        // ... 其他工具箱功能
                    }
                },
                dataZoom: [
                    {
                        type: 'slider',    // 滑块形式
                        xAxisIndex: [0, 1, 2],   // 这个数组定义了滑块应用于哪些x轴（在有多轴时）。这里只有一个x轴，所以是 [0]
                        start: 10,        // 开始位置，百分比形式
                        end: 100           // 结束位置，百分比形式
                    },
                    {
                        type: 'inside',    // 内嵌形式，即使用鼠标滚轮进行放大/缩小
                        xAxisIndex: [0, 1, 2],
                    }
                ],

                tooltip: {
                    trigger: 'axis',
                    // 可选：自定义提示内容的格式
                    formatter: function(params) {
                        var data = params[0].data; // 例如，获取第一个系列的数据
                        return 'Value: ' + data;
                    }
                },
                grid: [
                    { top: '10%', height: '20%' },
                    { top: '40%', height: '20%' },
                    { top: '70%', height: '20%' }
                ],
                yAxis: [
                    { type: 'value', gridIndex: 0 },
                    { type: 'value', gridIndex: 1 },
                    { type: 'value', gridIndex: 2 }
                ],
                xAxis: [
                    {
                        type: 'category',
                        gridIndex: 0,
                        splitLine: { show: false },
                        axisLabel: { show: false }, // Only show x-axis labels on the last grid/chart
                        boundaryGap: false
                    }, 
                    {
                        type: 'category',
                        gridIndex: 1,
                        splitLine: { show: false },
                        axisLabel: { show: false }, // Only show x-axis labels on the last grid/chart
                        boundaryGap: false
                    }, 
                    {
                        type: 'category',
                        gridIndex: 2,
                        splitLine: { show: false },
                        axisLabel: { show: false }, // Only show x-axis labels on the last grid/chart
                        boundaryGap: false
                    }    
                ],
                legend: {
                    data: ['Expected Full', 'Expected Half', 'Expected Quartar', 'Unexpected Full', 'Unexpected Half', 'Unexpected Quartar', 'Mid Full', 'Mid Half', 'Mid Quartar'],
                    // 根据需要可以添加更多的配置
                },
                series: [
                    { name: 'Expected Full', type: 'line', data: this.dataSeries.expected[0], xAxisIndex: 0, yAxisIndex: 0 },
                    // { name: 'Expected Half', type: 'line', data: this.dataSeries.expected[1], xAxisIndex: 0, yAxisIndex: 0 },
                    { name: 'Expected Quartar', type: 'line', data: this.dataSeries.expected[2], xAxisIndex: 0, yAxisIndex: 0 },
                    { name: 'Unexpected Full', type: 'line', data: this.dataSeries.unexpected[0], xAxisIndex: 1, yAxisIndex: 1 },
                    // { name: 'Unexpected Half', type: 'line', data: this.dataSeries.unexpected[1], xAxisIndex: 1, yAxisIndex: 1 },
                    { name: 'Unexpected Quartar', type: 'line', data: this.dataSeries.unexpected[2], xAxisIndex: 1, yAxisIndex: 1 },
                    { name: 'Mid Full', type: 'line', data: this.dataSeries.mid[0], xAxisIndex: 2, yAxisIndex: 2 },
                    // { name: 'Mid Half', type: 'line', data: this.dataSeries.mid[1], xAxisIndex: 2, yAxisIndex: 2 },
                    { name: 'Mid Quartar', type: 'line', data: this.dataSeries.mid[2], xAxisIndex: 2, yAxisIndex: 2 }
                ]
            };
            chartInstance.setOption(option);
            chartInstance.resize();
    
            earnInstance.setOption(earn_option);
            earnInstance.resize();
        }
    }
}
</script>

<style scoped>
/* Add your modal styles here */
.modal-content {
    width: 100%;
    overflow: hidden; 
}
</style>
