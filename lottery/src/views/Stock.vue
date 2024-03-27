<template>
  <div class="right-content">
    <Form inline @on-submit.prevent="fetchData" style="margin-bottom: 20px;">
      <FormItem>
        <Select v-model="code" placeholder="Select stock code">
          <Option value="US.MSFT">US.MSFT</Option>
          <Option value="US.GOOGL">US.GOOGL</Option>
        </Select>
      </FormItem>
      <FormItem>
        <DatePicker v-model="startDate" type="date" placeholder="Select start date"></DatePicker>
      </FormItem>
      <FormItem>
        <DatePicker v-model="endDate" type="date" placeholder="Select end date"></DatePicker>
      </FormItem>
      <FormItem>
        <Button type="primary" @click="fetchData" :disabled="!isQueryButtonEnabled">Query</Button>
      </FormItem>
    </Form>
    <Row>
      <Col span="22">
        <div ref="kLineChart" style="height: 800px;"></div>
        <div ref="volumeChart" style="height: 300px;"></div>
      </Col>
      <Col span="22">
        <div ref="barChart" style="height: 800px;"></div>
      </Col>
    </Row>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import { postData } from '@/api/dataService';
export default {
  components: {

  },
  data() {
    const today = new Date();
    return {
      code: '',
      startDate: today,
      endDate: today,
      kline: [],
      ticker: [],
      ticker_minute: [],
      timer: null,
      kLineChart: null, 
      volumeChart: null, 
      barChart: null
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
    this.kLineChart = echarts.init(this.$refs.kLineChart);
    this.volumeChart = echarts.init(this.$refs.volumeChart);
    this.barChart = echarts.init(this.$refs.barChart);

  }, 
  beforeDestroy() {
    this.stopTimer(); // 在组件销毁前清除定时器
  },
  methods: {
    startTimer() {
      this.stopTimer()
      // 设置定时器，每隔5秒调用一次fetchData
      if (!this.timer) {
        this.timer = setInterval(this.fetchData, 2000);
      }
      
    },
    stopTimer() {
      // 清除定时器
      if (this.timer) {
        clearInterval(this.timer);
        this.timer = null; // 重置定时器变量
      }
    }, 
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
      this.kline = response.kline
      this.ticker = response.ticker
      this.ticker_minute = response.ticker_minute


      this.drawKLineChart()
      this.drawVolumeChart(this.kline)
      this.drawBarChart(this.ticker)
      this.startTimer();
    },
    calculateStandardDeviation(array) {
      // 计算平均值
      const mean = array.reduce((acc, val) => acc + val, 0) / array.length;
      // 计算每个数值与平均值的差的平方的平均值（方差）
      const variance = array.reduce((acc, val) => acc + (val - mean) ** 2, 0) / array.length;
      // 返回方差的平方根作为标准差
      return Math.sqrt(variance);
    },

    drawKLineChart() {

      var allTimes = [...this.kline.map(data => data.time_key), ...this.ticker_minute.map(data => data.minute)]
      var uniqueTimes = Array.from(new Set(allTimes));
      uniqueTimes.sort(function(a, b) {
          return new Date(a) - new Date(b);
      });
      var k = new Array(uniqueTimes.length).fill(null);
      var ticker = new Array(uniqueTimes.length).fill(null);
      var ticker_anomaly = new Array(uniqueTimes.length).fill(null);
      this.kline.forEach(item => {
          var index = uniqueTimes.indexOf(item.time_key);
          if (index >= 0) k[index] = item;
      });
      let l = 4
      for (let i = this.ticker_minute.length - 1; i > 0 ; i--) {

        if (i < l) {
          for (let j = 0; j <= i; j++) {
            this.ticker_minute[i].buy += this.ticker_minute[i - j].buy
            this.ticker_minute[i].sell += this.ticker_minute[i - j].sell
            this.ticker_minute[i].neutral += this.ticker_minute[i - j].neutral
          }
          this.ticker_minute[i].buy /= i + 1
          this.ticker_minute[i].sell /= i + 1
          this.ticker_minute[i].neutral /= i + 1    
        }
        else {
          for (let j = 0; j <= l; j++) {
            this.ticker_minute[i].buy += this.ticker_minute[i - j].buy
            this.ticker_minute[i].sell += this.ticker_minute[i - j].sell
            this.ticker_minute[i].neutral += this.ticker_minute[i - j].neutral
          }
          this.ticker_minute[i].buy /= l + 1
          this.ticker_minute[i].sell /= l + 1
          this.ticker_minute[i].neutral /= l + 1         
        }
      }

      this.ticker_minute.forEach(item => {
          var index = uniqueTimes.indexOf(item.minute);
          if (index >= 0) ticker[index + 1] = item;
      });
      let buys = []
      let sells = []
      let neutrals = []
      let std_len = 0
      for (let i = 2; i < ticker.length; i++) {
        if (ticker[i] !== null) {
          std_len += 1
          if (std_len > 1) {
            let std = this.calculateStandardDeviation(buys)
            ticker[i].buy_std = std
            ticker[i].buy_mean = buys.reduce((acc, val) => acc + val, 0) / buys.length;
            
            std = this.calculateStandardDeviation(sells)
            ticker[i].sell_std = std       
            ticker[i].sell_mean = sells.reduce((acc, val) => acc + val, 0) / sells.length;

            std = this.calculateStandardDeviation(neutrals)
            ticker[i].neutral_std = std      
            ticker[i].neutral_mean = neutrals.reduce((acc, val) => acc + val, 0) / neutrals.length; 
          }
          buys.push(ticker[i].buy)
          sells.push(ticker[i].sell)
          neutrals.push(ticker[i].neutral)
        }
      }
      let anomaly_bar = 2.5

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        animation: false,
        dataZoom: [
            {
                type: 'slider', // 这是滑动条类型的数据区域缩放
                start: 10, // 初始化的时候滑动条选中的起始百分比, 0（最小值）-100（最大值）
                end: 100 // 初始化的时候滑动条选中的结束百分比
            }
        ],
        legend: {
          data: ['KLine', 'Buy', 'Sell', 'Neutral', 'Anomaly-B', 'Anomaly-S', 'Anomaly-N']
        },
        xAxis: {
          type: 'category',
          data: uniqueTimes
        },
        yAxis: [{
          type: 'value',
          scale: true, 
        }, {
          type: 'value', 
          scale: true
        }],
        series: [
          {
            type: 'candlestick',
            name: 'KLine',
            data: k.map(data => data != null ? [data.open, data.close, data.low, data.high] : []),
          }, 
          {
            type: 'line', 
            name: 'Buy', 
            yAxisIndex: 1, 
            data: ticker.map(data => data != null ? data.buy : null)
          },
          {
            type: 'line', 
            name: 'Sell', 
            yAxisIndex: 1, 
            data: ticker.map(data => data != null ? data.sell : null)
          }, 
          {
            type: 'line', 
            name: 'Neutral', 
            yAxisIndex: 1, 
            data: ticker.map(data => data != null ? data.neutral : null)
          },       
          {
            type: 'line', 
            name: 'Anomaly-B', 
            yAxisIndex: 1, 
            data: ticker.map(data => data != null ? (data.buy > (anomaly_bar * data.buy_std + data.buy_mean) ? 5100000 : 0) : null)
          },    
          {
            type: 'line', 
            name: 'Anomaly-S', 
            yAxisIndex: 1, 
            data: ticker.map(data => data != null ? (data.sell > (anomaly_bar * data.sell_std + data.sell_mean) ? 5200000 : 0) : null)
          },   
          {
            type: 'line', 
            name: 'Anomaly-N', 
            yAxisIndex: 1, 
            data: ticker.map(data => data != null ? (data.neutral > (anomaly_bar * data.neutral_std + data.neutral_mean) ? 6000000 : 0) : null)
          },   
        ]
      };
      this.kLineChart.setOption(option);
    },
    drawVolumeChart(data) {
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
          type: 'log',
          base: 2,
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
      this.volumeChart.setOption(option);
    },
    drawBarChart(data) {
      if(this.kline.length <= 0) {
        return
      }
      const lastKLine = this.kline[this.kline.length - 1];
      const high = lastKLine.high;
      const low = lastKLine.low;

      const highlightedBars = this.ticker.map(bar => {
        return {
          ...bar,
          // 增加一个标记属性来指示是否应该高亮这个Bar
          shouldHighlight: bar.price_key >= low && bar.price_key <= high
        };
      });

      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        title: {
            text: this.startDate, // 主标题文本
            left: 'center',        // 标题的水平对齐方式，可选值有：'left', 'center', 'right'
            top: 'bottom'             // 标题的垂直对齐方式，可选值有：'top', 'middle', 'bottom'
        },
        legend: {
          data: ['Buy', 'Sell', 'Neutral', 'Diff']
        },
        grid: {
          left: '5%',
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
            data: highlightedBars.map(data => {
                return {
                  value: data.buy, 
                  itemStyle: {
                    opacity: data.shouldHighlight ? 1 : 0.3 // 高亮颜色和默认颜色
                  }
                }
              }),
            barWidth: '40%'
          },
          {
            name: 'Sell',
            type: 'bar',
            stack: 'total',
            data: highlightedBars.map(data => {
                return {
                  value: data.sell, 
                  itemStyle: {
                    opacity: data.shouldHighlight ? 1 : 0.3 // 高亮颜色和默认颜色
                  }
                }
              }),
            barWidth: '40%'
          },
          {
            name: 'Neutral',
            type: 'bar',
            stack: 'total',
            data: highlightedBars.map(data => {
                return {
                  value: data.neutral, 
                  itemStyle: {
                    opacity: data.shouldHighlight ? 1 : 0.3 // 高亮颜色和默认颜色
                  }
                }
              }),
            barWidth: '40%'
          }, 
          {
            name: 'Diff',
            type: 'bar',
            data: highlightedBars.map(data => {
                return {
                  value: data.sell - data.buy, 
                  itemStyle: {
                    opacity: data.shouldHighlight ? 1 : 0.3 // 高亮颜色和默认颜色
                  }
                }
              }),
            barWidth: '40%'
          }
        ]
      };
      this.barChart.setOption(option);
    }
  }
};
</script>

<style scoped>
    .right-content {
        flex: 1; /* 充满剩余空间 */
        padding: 1rem;
        color: #000
    }
    .demo-spin-container{
        display: inline-block;
        width: 100%;
        height: 100px;
        position: relative;
        border: 1px solid #eee;
    }
</style>
  