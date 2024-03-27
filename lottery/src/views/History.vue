<template>
    <div class="right-content">
      <h2>收益结果</h2>

      <h3>总场次：<B>{{bought}}</B>, 总收益: <B>{{ (totalWin * 100).toFixed(2) }}%</B></h3>

      <div ref="earn" style="width: 1800px; height: 200px;"></div>

      <i-table :columns="columns" :data="tableData"></i-table>
      
    </div>
  </template>
  
<script>
import { fetchData } from '@/api/dataService';
import * as echarts from "echarts";

export default {
  data() {
    return {
      data: null,
      error: null, 
      totalWin: 0, 
      strategy: ['1', '2', '3'],
      earnInstance: null,
      bought: 0,
      log_earns: [],
      columns: [
        {
          title: '购买组合',
          key: 'COMBO',
          render: (h, params) => {
            return h('div', [
                              h('pre', params.row.COMBO)
                          ]);
                      }
        },
        {
          title: '盈利比例',
          key: 'PAY'
        },
        {
          title: '购买时间', 
          key: 'PURCHASE_TIME',
          sortable: true
        }
      ],
      tableData: [

      ]
    };
  },
  async mounted() {
    try {
      this.data = await this.fetchData();
    } catch (err) {
      this.error = err.message;
    }
  }, 
  methods: {
    getMatchResult: function(host_goal, guest_goal) {
      if (host_goal > guest_goal) {
        return "主胜"
      } else if (host_goal < guest_goal) {
        return "客胜"
      } else {
        return "平"
      }
    },
    fetchData: async function () {
        const response = await fetchData('/history');
        let labels = {
          'WIN': '主胜',
          'SAME': '平',
          'LOST': '客胜'
        }
        let earns = []
        let totalWin = 0
        if (response != null) {
            this.tableData = response
            this.bought = 0
            this.totalWin = 0
            for (let i = this.tableData.length - 1; i >= 0; i--) {
              // 分离 match ，获取match的信息
              let item = this.tableData[i]
              item.COMBO = ''
              item.PURCHASE_TIME = (new Date(item.PURCHASE_TIME)).toLocaleString()
              let matches = item.MATCHES.split(",")
              let sels = item.SELS.split(",")
              for (let j = 0; j < matches.length; j++) {
                let match = matches[j]
                let info = await fetchData('/match/' + match)
                if (info.length > 0) {
                  item.COMBO += info[0].SOURCE_MATCH_ID + " " + info[0].HOST_NAME + ' vs. ' + info[0].GUEST_NAME + ' '
                  item.COMBO += "购买选择: " + labels[sels[j]] + "(" + item.PAY + ")\n"
                  if (item.STATUS == 2) {
                    item.COMBO += "-- 只看不买 -- \n"
                    if (info[0].MATCH_STATUS == -1) {
                      item.COMBO += "比赛结果：" + info[0].HOST_GOAL + " : " + info[0].GUEST_GOAL + " (" + this.getMatchResult(info[0].HOST_GOAL, info[0].GUEST_GOAL) + ") " + (new Date(info[0].MATCH_TIME)).toLocaleString() + ""
                    }
                  } else if (info[0].MATCH_STATUS == -1) {
                    item.COMBO += "比赛结果：" + info[0].HOST_GOAL + " : " + info[0].GUEST_GOAL + " (" + this.getMatchResult(info[0].HOST_GOAL, info[0].GUEST_GOAL) + ") " + (new Date(info[0].MATCH_TIME)).toLocaleString() + ""
                    this.bought += 1
                  } else {
                    item.COMBO += "比赛未开始 " + (new Date(info[0].MATCH_TIME)).toLocaleString() + "\n"
                  }
                  
                  if (this.getMatchResult(info[0].HOST_GOAL, info[0].GUEST_GOAL) != labels[sels[j]] || info[0].MATCH_STATUS == 0) {
                    item.PAY = 0
                  }
                }
              }
              if (item.STATUS == 1) {
                totalWin += item.PAY
              }
              if (this.bought > 0) {
                this.log_earns.push((totalWin / this.bought - 1) * 100 )
              }
              
           }
           this.totalWin = totalWin / this.bought - 1 
        }
        this.earnInstance = echarts.init(this.$refs.earn)
        console.log(this.earnInstance)
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
                { 
                  type: 'value', 
                  gridIndex: 0, 
                  axisLabel: {
                    formatter: '{value} %'
                  } 
                },
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
                data: ['收益'],
                // 根据需要可以添加更多的配置
            },
            series: [
                { name: '收益', type: 'line', data: this.log_earns, xAxisIndex: 0, yAxisIndex: 0 },
            ]
        };
        this.earnInstance.setOption(earn_option);
        this.earnInstance.resize();
      }
    }
  }
</script>

<style scoped>
    .right-content {
        flex: 1; /* 充满剩余空间 */
        padding: 1rem;
        color: #333
    }
</style>
  