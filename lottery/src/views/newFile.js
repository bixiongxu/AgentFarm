import * as echarts from 'echarts';
import { postData } from '@/api/dataService';

export default (await import('vue')).defineComponent({
components: {},
data() {
const today = new Date();
return {
code: '',
startDate: today,
endDate: today,
kline: [],
ticker: []
};
},
computed: {
// 计算属性来确定查询按钮是否应该启用
isQueryButtonEnabled() {
const isCodeNotEmpty = this.code !== '';
const isDateRangeValid = this.startDate && this.endDate && this.startDate <= this.endDate;
return isCodeNotEmpty && isDateRangeValid;
}
},
async mounted() {
},
methods: {
formatDateToLocaleString(date) {
if (!date) return '';
const newDate = new Date(date);
const tzOffset = newDate.getTimezoneOffset() * 60000; // 时区偏移量，单位毫秒
const localISOTime = (new Date(newDate - tzOffset)).toISOString().slice(0, 10);
return localISOTime;
},

fetchData: async function () {
const response = await postData('/stock', {
code: this.code,
start: this.formatDateToLocaleString(this.startDate),
end: this.formatDateToLocaleString(this.endDate)
});
this.kline = response.kline;
this.ticker = response.ticker;



this.drawKLineChart(this.kline);
this.drawVolumeChart(this.kline);
this.drawBarChart(this.ticker);
},
drawKLineChart(data) {
const kLineChart = echarts.init(this.$refs.kLineChart);
const option = {
tooltip: {
trigger: 'axis',
axisPointer: {
type: 'cross'
}
},
xAxis: {
type: 'category',
data: this.kline.map(data => data.time_key)
},
yAxis: {
type: 'value',
scale: true,
},
series: [
{
type: 'candlestick',
name: 'K Line',
data: this.kline.map(data => [data.open, data.close, data.low, data.high]),
}
]
};
kLineChart.setOption(option);
},
drawVolumeChart(data) {
const volumeChart = echarts.init(this.$refs.volumeChart);
const option = {
tooltip: {
trigger: 'axis',
axisPointer: {
type: 'cross'
}
},
xAxis: {
type: 'category',
data: this.kline.map(data => data.time_key)
},
yAxis: {
type: 'value',
scale: true
},
series: [
{
type: 'bar',
name: 'Volume',
data: this.kline.map(data => data.turnover),
color: '#7cb5ec'
}
]
};
volumeChart.setOption(option);
},
drawBarChart(data) {

const lastKLine = this.kline[this.kline.length - 1];
const high = this.kline.high;
const low = this.kline.low;

const highlightedBars = this.ticker.map(bar => {
return {
...bar,
// 增加一个标记属性来指示是否应该高亮这个Bar
shouldHighlight: bar.price_key >= low && bar.price_key <= high
};
});

const barChart = echarts.init(this.$refs.barChart);
const option = {
tooltip: {
trigger: 'axis',
axisPointer: {
type: 'shadow'
}
},
legend: {
data: ['Buy', 'Sell', 'Neutral']
},
grid: {
left: '10%',
right: '10%',
bottom: '15%'
},
xAxis: {
type: 'value',
},
yAxis: {
type: 'category',
// 使用price_key作为纵轴标签，这里需要对数据进行适当转换
data: this.ticker.map(data => `${data.price_key}`),
},
series: [
{
name: 'Buy',
type: 'bar',
stack: 'total', // 指定堆叠的名称
data: this.ticker.map(data => {
value: data.buy,
itemStyle; {
color: bar.shouldHighlight ? 'red' : '#5470C6'; // 高亮颜色和默认颜色
}
}),
barWidth: '60%'
},
{
name: 'Sell',
type: 'bar',
stack: 'total',
data: this.ticker.map(data => data.sell),
barWidth: '60%'
},
{
name: 'Neutral',
type: 'bar',
stack: 'total',
data: this.ticker.map(data => data.neutral),
barWidth: '60%'
}
]
};
barChart.setOption(option);
}
}
});
