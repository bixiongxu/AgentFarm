<template>
    <div class="right-content">
      <h2>比赛数据</h2>
      <i-table :columns="columns" :data="tableData" :border="1"></i-table>
      <div v-if="selections">
        <h2>购买策略推荐</h2>
        <i-table :columns="columns_combo" :data="selections" :border="1"></i-table>      
      </div>
      <StrategyModal :isOpen="isStrategyOpen" :dataSeries="stat" @update:isOpen="isStrategyOpen = $event" :title="currentTitle"></StrategyModal>
    </div>
  </template>
  
<script>
import { fetchData } from '@/api/dataService';
import { postData } from '@/api/dataService';
import { deleteData } from '@/api/dataService';
import StrategyModal from '@/components/StrategyModal.vue';

import { resolveComponent } from 'vue';

export default {
  components: {
    StrategyModal
  },
  data() {
    return {
      data: null,
      error: null, 
      selections: null, 
      match_infos: {}, 
      isStrategyOpen: false,
      currentTitle: '', 
      stat: null, 
      columns: [
        {
          title: 'ID',
          key: 'SOURCE_MATCH_ID'
        },
        {
          title: '主队',
          key: 'HOST_NAME'
        },
        {
          title: '客队',
          key: 'GUEST_NAME'
        },
        {
          title: '主胜',
          align: 'center',
          children: [
            {
              title: '赔率', 
              key: 'WIN'
            }, 
            {
              title: '历史胜率', 
              key: 'WIN_RATE',
              render: (h, params) => {
                return h('div', [
                                  h('span', params.row.WIN_RATE)
                              ]);
                          }
            }
            /*
            ,             
            {
              title: '期望值', 
              render: (h, params) => {
                if (params.row.WIN_RATE * params.row.WIN > 1) {
                  return h('div', [
                                  h('strong', (params.row.WIN_RATE * params.row.WIN).toFixed(2))
                              ]);
                } else {
                  return h('span', [
                                  h('span', (params.row.WIN_RATE * params.row.WIN).toFixed(2))
                              ]);
                }
              }
            },
            */
          ]
        },
        {
          title: '平',
          align: 'center',
          children: [
            {
              title: '赔率', 
              key: 'SAME'
            }, 
            {
              title: '历史胜率', 
              key: 'SAME_RATE',
              render: (h, params) => {
                return h('div', [
                                  h('span', params.row.SAME_RATE)
                              ]);
                          }
            }
            /*,             
            {
              title: '期望值', 
              render: (h, params) => {
                if (params.row.SAME_RATE * params.row.SAME > 1) {
                  return h('div', [
                                  h('strong', (params.row.SAME_RATE * params.row.SAME).toFixed(2))
                              ]);
                } else {
                  return h('span', [
                                  h('span', (params.row.SAME_RATE * params.row.SAME).toFixed(2))
                              ]);
                }

              }
            },    */        
          ]
        },
        {
          title: '客胜',
          align: 'center',
          children: [
            {
              title: '赔率', 
              key: 'LOST'
            }, 
            {
              title: '历史胜率', 
              key: 'LOST_RATE',
              render: (h, params) => {
                return h('div', [
                                  h('span', params.row.LOST_RATE)
                              ]);
                          }
            }/*,             
            {
              title: '期望值', 
              render: (h, params) => {
                if (params.row.LOST_RATE * params.row.LOST > 1) {
                  return h('div', [
                                  h('strong', (params.row.LOST_RATE * params.row.LOST).toFixed(2))
                              ]);
                } else {
                  return h('div', [
                                  h('span', (params.row.LOST_RATE * params.row.LOST).toFixed(2))
                              ]);                  
                }

              }
            },       */       
          ]
        },
        {
          title: '策略', 
          key: 'STRATEGY', 
          width: 300,
          render: (h, params) => {
                return h('div', [
                    h(resolveComponent('Button'), {
                                        type: 'text',
                                        size: 'small',
                                        style: {
                                            marginRight: '5px'
                                        },
                                        onClick: async () => {
                                            await this.showStrategyStat(params.row)
                                        }
                                    }, {
                                        default() {
                                            return params.row.STRATEGY
                                        }
                                    })
                            ]);
              }
        },
        {
          title: '比赛时间', 
          key: 'MATCH_TIME',
          sortable: true
        }
      ],
      tableData: [

      ], 
      labels: {
        "WIN": "主胜", 
        "SAME": "平",
        "LOST": "客胜"

      }, 
      columns_combo: [
        {
          title: '比赛',
          key: 'SOURCE_MATCH_ID', 
          render: (h, params) => {
            let str = ""
            for (let i = 0; i < params.row.SOURCE_MATCH_ID.length; i++) {
              let id = params.row.SOURCE_MATCH_ID[i]
              str += this.match_infos[id].HOST_NAME + " vs. " + this.match_infos[id].GUEST_NAME + ": " + this.labels[params.row.SEL[i]] + " (" + params.row.TAG + ")\n" + new Date(this.match_infos[id].MATCH_TIME).toLocaleString()
              
            }
            return h('div', [
                              h('pre', str)
                          ]);
                      }
        },
        {
          title: '期望值',
          sortable: true,
          key: 'EXP'
        },     
        {
          title: '赔付',
          sortable: true,
          key: 'PAY'
        },
        {
          title: '购买', 
          key: 'action',
          render: (h, params) => {
              let rets = []
              if (params.row.SOURCE_MATCH_ID.length == 1) {
                rets.push( h('span', [
                    h(resolveComponent('Button'), {
                                        type: 'success',
                                        size: 'small',
                                        style: {
                                            marginRight: '5px'
                                        },
                                        onClick: async () => {
                                            await this.showStrategyStat(this.match_infos[params.row.SOURCE_MATCH_ID[0] + params.row.STRATEGY[0]])
                                        }
                                    }, {
                                        default() {
                                            return '策略'
                                        }
                                    })
                            ])
                )
              }
              if (params.row.purchased == 0) {
                rets.push(h('span', [
                                h(resolveComponent('Button'), {
                                    type: 'primary',
                                    size: 'small',
                                    disabled: params.row.purchased == 1,
                                    style: {
                                        marginRight: '5px'
                                    },
                                    onClick: () => {
                                        this.buy(params.row)
                                    }
                                }, {
                                    default() {
                                        return '购买'
                                    }
                                })
                            ]))
                rets.push(h('span', [
                                h(resolveComponent('Button'), {
                                    type: 'warning',
                                    size: 'small',
                                    disabled: params.row.purchased == 1,
                                    style: {
                                        marginRight: '5px'
                                    },
                                    onClick: () => {
                                        this.buy(params.row, false)
                                    }
                                }, {
                                    default() {
                                        return '只看不买'
                                    }
                                })
                            ]))
              } else {
                rets.push(h('span', [
                                h(resolveComponent('Button'), {
                                    type: 'error',
                                    size: 'small',
                                    onClick: () => {
                                        this.cancelBuy(params.row)
                                    }
                                }, {
                                    default() {
                                        if (params.row.purchased == 1) {
                                          return '取消'
                                        }
                                        else {
                                          return '取消只看不买'
                                        }
                                        
                                    }
                                })
                            ]))
              }
              return rets

          }
        }
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
    fetchData: async function () {
        const response = await fetchData('/recommend');
        if (response != null) {
            this.tableData = response
            for (let i = 0; i < this.tableData.length; i++) {
              let item = this.tableData[i]
              
              let total = item.EXPECTED + item.UNEXPECTED + item.MID
              let maxp = Math.max(item.WIN, item.SAME, item.LOST)
              let minp = Math.min(item.WIN, item.SAME, item.LOST)

              if (item.WIN == minp) {
                item.WIN_RATE = item.EXPECTED_RATE
                item.BUY_WIN = item.EXPECTED
                if (item.BUY_WIN > 0) {
                  item.TAG = 'EXPECTED'
                }
              } else if (item.WIN == maxp) {
                item.WIN_RATE = item.UNEXPECTED_RATE
                item.BUY_WIN = item.UNEXPECTED
                if (item.BUY_WIN > 0) {
                  item.TAG = 'UNEXPECTED'
                }
              }
              else {
                item.WIN_RATE = item.MID_RATE
                item.BUY_WIN = item.MID
                if (item.BUY_WIN > 0) {
                  item.TAG = 'MID'
                }
              }
              if (item.LOST == minp) {
                item.LOST_RATE = item.EXPECTED_RATE
                item.BUY_LOST = item.EXPECTED
                if (item.BUY_LOST > 0) {
                  item.TAG = 'EXPECTED'
                }
              } else if (item.LOST == maxp) {
                item.LOST_RATE = item.UNEXPECTED_RATE
                item.BUY_LOST = item.UNEXPECTED
                if (item.BUY_LOST > 0) {
                  item.TAG = 'UNEXPECTED'
                }
              }
              else {
                item.LOST_RATE = item.MID_RATE
                item.BUY_LOST = item.MID
                if (item.BUY_LOST > 0) {
                  item.TAG = 'MID'
                }
              }
              if (item.SAME == minp) {
                item.SAME_RATE = item.EXPECTED_RATE
                item.BUY_SAME = item.EXPECTED
                if (item.BUY_SAME > 0) {
                  item.TAG = 'EXPECTED'
                }
              } else if (item.SAME == maxp) {
                item.SAME_RATE = item.UNEXPECTED_RATE
                item.BUY_SAME = item.UNEXPECTED
                if (item.BUY_SAME > 0) {
                  item.TAG = 'UNEXPECTED'
                }
              }
              else {
                item.SAME_RATE = item.MID_RATE
                item.BUY_SAME = item.MID
                if (item.BUY_SAME > 0) {
                  item.TAG = 'MID'
                }
              }


              item.MATCH_TIME = (new Date(item.MATCH_TIME)).toLocaleString();
              this.match_infos[item.SOURCE_MATCH_ID + item.STRATEGY] = item
              this.match_infos[item.SOURCE_MATCH_ID] = item
            }
        }
        this.findCombo()
    }, 

    buy: async function(selection, real = true) {
      let purchase = 1
      if (!real) {
        purchase = 2
      }
      const response = await postData('/purchase/' + this.getHash(selection), {
        SOURCE_MATCH_ID: selection.SOURCE_MATCH_ID, 
        SEL: selection.SEL,
        PAY: selection.PAY,
        PURCHASED: purchase
      });
      selection.purchased = await this.getPurchased(selection)
    }, 
    
    cancelBuy: async function(selection) {
      const response = await deleteData('/purchase/' + this.getHash(selection));
      selection.purchased = await this.getPurchased(selection)
    },
    getHash: function(selection) {
      let hash = ''
      let items = []

      for (let i = 0; i < selection.SOURCE_MATCH_ID.length; i++) {
        items.push(selection.SOURCE_MATCH_ID[i] + "_" + selection.SEL[i])
      }
      hash = items.sort().join("-")
      return hash
    },

    getPurchased: async function(selection) {
      let res = await fetchData('purchase/' + this.getHash(selection))
      return res.purchased

    }, 
    showStrategyStat: async function(selection) {
      let res = await fetchData('stat/' + selection.STRATEGY)
      // Full, Half, Quartar
      this.stat = {
        expected: [
          [], [], []
        ], 
        unexpected: [
          [], [], []
        ], 
        mid: [
          [], [], []
        ], 
        earn: []
      }
      for (let i = 0; i < res.length; i++) {
        let item = res[i]
        this.stat.expected[0].push(item.EXPECTED_RATE)
        this.stat.expected[1].push(item.EXPECTED_HALF_RATE)
        this.stat.expected[2].push(item.EXPECTED_QUARTAR_RATE)

        this.stat.unexpected[0].push(item.UNEXPECTED_RATE)
        this.stat.unexpected[1].push(item.UNEXPECTED_HALF_RATE)
        this.stat.unexpected[2].push(item.UNEXPECTED_QUARTAR_RATE)

        this.stat.mid[0].push(item.MID_RATE)
        this.stat.mid[1].push(item.MID_HALF_RATE)
        this.stat.mid[2].push(item.MID_QUARTAR_RATE)
      }

      res = await fetchData('earn/' + selection.STRATEGY)
      for (let i = 0; i < res.length; i++) {
        let item = res[i]
        this.stat.earn.push(item.EARN)
      }
      console.log(this.stat.earn)
      this.currentTitle = selection.STRATEGY
      this.isStrategyOpen = true
    }, 
    findCombo: async function() {
      let selections = []
      let checked = []
      for (let i = 0; i < this.tableData.length; i++) {
        let item = this.tableData[i]
        if (item.BUY_WIN > 0) {
          selections.push({
            SOURCE_MATCH_ID: ['' + item.SOURCE_MATCH_ID], 
            SEL: ["WIN"], 
            EXP: item.WIN * item.WIN_RATE, 
            PAY: item.WIN,
            TAG: item.TAG,
            STRATEGY: [item.STRATEGY]
          })
          
          checked.push(this.getHash(selections[selections.length-1]))
        }
        if (item.BUY_SAME > 0) {
          selections.push({
            SOURCE_MATCH_ID: ['' + item.SOURCE_MATCH_ID], 
            SEL: ["SAME"], 
            EXP: item.SAME * item.SAME_RATE,
            PAY: item.SAME,
            TAG: item.TAG,
            STRATEGY: [item.STRATEGY]
          })
          checked.push(this.getHash(selections[selections.length-1]))
        }
        if (item.BUY_LOST > 0) {
          selections.push({
            SOURCE_MATCH_ID: ['' + item.SOURCE_MATCH_ID], 
            SEL: ["LOST"], 
            EXP: item.LOST * item.LOST_RATE, 
            PAY: item.LOST,
            TAG: item.TAG,
            STRATEGY: [item.STRATEGY]
          })
          checked.push(this.getHash(selections[selections.length-1]))
        }
        if (selections.length > 0) {
          selections[selections.length-1].purchased = await this.getPurchased(selections[selections.length-1])
        }
        
        
      }
      for (let k = 0; k < 0; k++) {
        let len = selections.length
        for (let i = 0; i < len; i++) {
          for (let j = 0; j < this.tableData.length; j++) {
            let item1 = selections[i]
            let item2 = this.tableData[j]
            let candidate = [...item1.SOURCE_MATCH_ID, item2.SOURCE_MATCH_ID]
            if (checked.indexOf(candidate.sort().join(",")) >= 0 || item1.SOURCE_MATCH_ID.indexOf(item2.SOURCE_MATCH_ID) >= 0) {
              continue
            }
            let exp = 0
            if (item2.WIN * item2.WIN_RATE >= 1) {
              exp = item1.EXP * item2.WIN * item2.WIN_RATE
              if (exp > 1) {
                selections.push({
                  SOURCE_MATCH_ID: [... item1.SOURCE_MATCH_ID, '' + item2.SOURCE_MATCH_ID], 
                  SEL:[...item1.SEL, "WIN"], 
                  EXP: exp, 
                  PAY: item1.PAY * item2.WIN
                })
                checked.push(this.getHash(selections[selections.length-1]))
              }
            }

            if (item2.SAME * item2.SAME_RATE >= 1) {
              exp = item1.EXP * item2.SAME * item2.SAME_RATE
              if (exp > 1) {
                selections.push({
                  SOURCE_MATCH_ID: [... item1.SOURCE_MATCH_ID, '' + item2.SOURCE_MATCH_ID], 
                  SEL:[...item1.SEL, "SAME"], 
                  EXP: exp, 
                  PAY: item1.PAY * item2.SAME
                })
                checked.push(this.getHash(selections[selections.length-1]))
              }
            }

            if (item2.LOST * item2.LOST_RATE >= 1) {
              exp = item1.EXP * item2.LOST * item2.LOST_RATE
              if (exp > 1) {
                selections.push({
                  SOURCE_MATCH_ID: [... item1.SOURCE_MATCH_ID, '' + item2.SOURCE_MATCH_ID], 
                  SEL:[...item1.SEL, "LOST"], 
                  EXP: exp, 
                  PAY: item1.PAY * item2.LOST
                })
                checked.push(this.getHash(selections[selections.length-1]))
              }            
            }

          }
        }
      }

      this.selections = selections;
    }, 

  }
};
</script>

<style scoped>
    .right-content {
        flex: 1; /* 充满剩余空间 */
        padding: 1rem;
        color: #333
    }
</style>
  