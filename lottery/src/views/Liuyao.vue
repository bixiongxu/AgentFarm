<template>
    <div class="right-content">

        <Input v-model="question" placeholder="请输入要问的问题"/>
        <Button @click="yaogua()">起卦</Button>
        <br/>
        <div class="demo-spin-container" v-if="loading">
          <Spin fix>{{ questions[idx] }}。 心诚则灵。{{status}}</Spin>
        </div>
        <div v-for="(record, idx) in records">
            问：{{ questions[idx] }}<BR/>
            {{record.gong}} ({{getgongwuxing(record.gong)}}) {{ record.name }} 
            <span v-if="record.name != record.change_name"> 之 {{ record.change_name }}</span>
            <br/>
            卦身： {{ record.guashen }}
            <BR/>
            用神：{{ record.yongshen }}
            
            <BR/>
            {{  record.year }} 年 {{ record.month }} 月 {{ record.day }} 日 {{ record.hour }} 时
            <BR/>
            <span v-if="record.is_month_yongshen">月建为用神爻</span>
            <span v-if="record.is_day_yongshen">日辰为用神爻</span>
            <Row>
                <Col>
                    <Row v-for="(item, item_idx) in record.base">
                        <Col style="margin: 0px 50px">
                            <span v-if="5 - item_idx == record.shi">世</span>
                            <span v-if="5 - item_idx == record.ying">应</span>
                            <span v-if="5 - item_idx != record.shi && 5 - item_idx != record.ying">&nbsp;</span>
                        </Col>
                    </Row>
                </Col>
                <Col>
                    <Row v-for="(item, item_idx) in record.base">
                        <Col style="margin: 0px 50px">
                            <span v-if="record.base[5 - item_idx] == 1"> ----- </span>
                            <span v-else> --  -- </span>
                            <span>
                                &nbsp;
                                {{ record.base_dizhi[5 - item_idx] }}
                                &nbsp;
                                {{ getliuqin(record.gong, record.base_dizhi[5 - item_idx]) }}
                            </span>
                        </Col>
                    </Row>
                </Col>
                <Col>
                    <Row v-for="(item, item_idx) in record.change">
                        <Col style="margin: 0px 50px">
                            <span v-if="record.change[5 - item_idx] != record.base[5 - item_idx]">
                                <span v-if="record.change[5 - item_idx] == 1"> ----- </span>
                                <span v-else> --  -- </span>
                                <span>
                                    &nbsp;
                                    {{ record.change_dizhi[5 - item_idx] }}
                                    &nbsp;
                                    {{ getliuqin(record.gong, record.change_dizhi[5 - item_idx]) }}
                                </span>
                            </span>
                            <span v-else>&nbsp;</span>
                        </Col>
                    </Row>
                </Col>
                <Col>
                    <Row v-for="(item, item_idx) in record.base">
                        <Col style="margin: 0px 50px">
                            <span v-if="record.yongshen_idx == 5 - item_idx">
                              用神
                              <span v-if="record.yongshen_kong">(旬空)</span>
                            </span>
                            <span v-if="record.yuanshen.indexOf(5 - item_idx) >= 0">
                              原神
                            </span>
                            <span v-if="record.jishen.indexOf(5 - item_idx) >= 0">
                              忌神
                            </span>
                            <span v-if="record.choushen.indexOf(5 - item_idx) >= 0">
                              仇神
                            </span>
                            <span v-if="record.fushen_idx == 5 - item_idx">
                              {{record.fushen_dizhi}} (伏神)
                            </span>
                            <span> &nbsp;</span>
                        </Col>
                    </Row>
                </Col>
                <Col>
                    <Row v-for="(item, item_idx) in record.change">
                        <Col style="margin: 0px 50px">
                            <span>
                                &nbsp;
                                {{ record.animal[5 - item_idx] }}
                            </span>
                        </Col>
                    </Row>
                </Col>
                <Col>
                    <Row v-for="(item, item_idx) in record.changsheng">
                        <Col style="margin: 0px 50px">
                            <span>
                                &nbsp;
                                {{ record.changsheng[5 - item_idx] }}
                            </span>
                        </Col>
                    </Row>
                </Col>
            </Row>
            <div>

              <h2>卦象详解：</h2>
              <div>（以下所有分析仅限于起卦的问题所讨论的范围！）</div>
              <B>卦中主人在卦中分析</B><BR/>
              {{ record.result.single[record.shi] }}<BR/>
              <B>卦中客体的分析</B><BR/>
              {{ record.result.single[record.ying] }}<BR/>
              <B>本卦所问之事分析</B><BR/>
              {{ record.result.single[record.yongshen_idx] }}<BR/>
            </div>
            <div>
              <B>断言</B><BR/>
              {{ record.answer }}
            </div>
        </div>
    </div>
  </template>
  
<script>
import {chatYongshen} from '@/api/openai'
import StrategyModal from '@/components/StrategyModal.vue';
import LunarCalendar from 'lunar-calendar'
import { chatShiValid, chatYingValid, chat } from '../api/openai';

// 定义64卦，以两个0～7的整数，内卦先，外卦后
let gua64 = {
  '乾宫': [77, 37, 17, 7, 3, 1, 5, 75], 
  '兑宫': [66, 26, 6, 16, 12, 10, 14, 64],
  '离宫': [55, 15, 35, 25, 21, 23, 27, 57],
  '震宫': [44, 4, 24, 34, 30, 32, 36, 46],
  '巽宫': [33, 73, 53, 43, 47, 45, 41, 31],
  '坎宫': [22, 62, 42, 52, 56, 54, 50, 20],
  '艮宫': [11, 51, 71, 61, 65, 67, 63, 13],
  '坤宫': [0, 40, 60, 70, 74, 76, 72, 2]
}
let sheng = {
    '子': ['寅', '卯'], 
    '丑': ['申', '酉'], 
    '寅': ['巳', '午'], 
    '卯': ['巳', '午'], 
    '辰': ['申', '酉'], 
    '巳': ['丑', '辰', '未', '戌'], 
    '午': ['丑', '辰', '未', '戌'], 
    '未': ['申', '酉'], 
    '申': ['子', '亥'], 
    '酉': ['子', '亥'], 
    '戌': ['申', '酉'], 
    '亥': ['寅', '卯']
}

let bi = {
    '子': ['亥'], 
    '丑': ['辰', '未', '戌'], 
    '寅': ['卯'], 
    '卯': ['寅'], 
    '辰': ['丑', '未', '戌'], 
    '巳': ['午'], 
    '午': ['巳'], 
    '未': ['丑', '辰', '戌'], 
    '申': ['酉'], 
    '酉': ['申'], 
    '戌': ['丑', '辰', '未'], 
    '亥': ['子']
}
// 刑
let xing = {
    '子': ['卯'], 
    '丑': ['未', '戌'], 
    '寅': ['巳'], 
    '卯': ['子'], 
    '辰': [], 
    '巳': [], 
    '午': [], 
    '未': [], 
    '申': [], 
    '酉': [], 
    '戌': [], 
    '亥': []
}

let ke = {
    '子': ['巳', '午'], 
    '丑': ['子', '亥'], 
    '寅': ['丑', '辰', '未', '戌'], 
    '卯': ['丑', '辰', '未', '戌'], 
    '辰': ['子', '亥'], 
    '巳': ['申', '酉'], 
    '午': ['申', '酉'], 
    '未': ['子', '亥'], 
    '申': ['寅', '卯'], 
    '酉': ['寅', '卯'], 
    '戌': ['子', '亥'], 
    '亥': ['巳', '午'], 
}
let liuqin = {
  '乾宫': {
    '子': '子孙', 
    '丑': '父母', 
    '寅': '妻财', 
    '卯': '妻财', 
    '辰': '父母', 
    '巳': '官鬼', 
    '午': '官鬼', 
    '未': '父母', 
    '申': '兄弟', 
    '酉': '兄弟', 
    '戌': '父母', 
    '亥': '子孙'
  },
  '兑宫': {
    '子': '子孙', 
    '丑': '父母', 
    '寅': '妻财', 
    '卯': '妻财', 
    '辰': '父母', 
    '巳': '官鬼', 
    '午': '官鬼', 
    '未': '父母', 
    '申': '兄弟', 
    '酉': '兄弟', 
    '戌': '父母', 
    '亥': '子孙'
  },
  '离宫': {
    '子': '官鬼', 
    '丑': '子孙', 
    '寅': '父母', 
    '卯': '父母', 
    '辰': '子孙', 
    '巳': '兄弟', 
    '午': '兄弟', 
    '未': '子孙', 
    '申': '妻财', 
    '酉': '妻财', 
    '戌': '子孙', 
    '亥': '官鬼'
  },
  '震宫': {
    '子': '父母', 
    '丑': '妻财', 
    '寅': '兄弟', 
    '卯': '兄弟', 
    '辰': '妻财', 
    '巳': '子孙', 
    '午': '子孙', 
    '未': '妻财', 
    '申': '官鬼', 
    '酉': '官鬼', 
    '戌': '妻财', 
    '亥': '父母'
  },
  '巽宫': {
    '子': '父母', 
    '丑': '妻财', 
    '寅': '兄弟', 
    '卯': '兄弟', 
    '辰': '妻财', 
    '巳': '子孙', 
    '午': '子孙', 
    '未': '妻财', 
    '申': '官鬼', 
    '酉': '官鬼', 
    '戌': '妻财', 
    '亥': '父母'
  },
  '坎宫': {
    '子': '兄弟', 
    '丑': '官鬼', 
    '寅': '子孙', 
    '卯': '子孙', 
    '辰': '官鬼', 
    '巳': '妻财', 
    '午': '妻财', 
    '未': '官鬼', 
    '申': '父母', 
    '酉': '父母', 
    '戌': '官鬼', 
    '亥': '兄弟'
  },
  '艮宫': {
    '子': '妻财', 
    '丑': '兄弟', 
    '寅': '官鬼', 
    '卯': '官鬼', 
    '辰': '兄弟', 
    '巳': '父母', 
    '午': '父母', 
    '未': '兄弟', 
    '申': '子孙', 
    '酉': '子孙', 
    '戌': '兄弟', 
    '亥': '妻财'
  },
  '坤宫': {
    '子': '妻财', 
    '丑': '兄弟', 
    '寅': '官鬼', 
    '卯': '官鬼', 
    '辰': '兄弟', 
    '巳': '父母', 
    '午': '父母', 
    '未': '兄弟', 
    '申': '子孙', 
    '酉': '子孙', 
    '戌': '兄弟', 
    '亥': '妻财'
  },
}

let wai_dizhi = {
  7: ['午', '申', '戌'],
  6: ['亥', '酉', '未'], 
  5: ['酉', '未', '巳'], 
  4: ['午', '申', '戌'], 
  3: ['未', '巳', '卯'], 
  2: ['申', '戌', '子'], 
  1: ['戌', '子', '寅'],
  0: ['丑', '亥', '酉']
}

let nei_dizhi = {
  7: ['子', '寅', '辰'],
  6: ['巳', '卯', '丑'], 
  5: ['卯', '丑', '亥'], 
  4: ['子', '寅', '辰'], 
  3: ['丑', '亥', '酉'], 
  2: ['寅', '辰', '午'], 
  1: ['辰', '午', '申'],
  0: ['未', '巳', '卯']
}

let gong_wuxing = {
  '乾宫': '金', 
  '兑宫': '金',
  '离宫': '火', 
  '震宫': '木', 
  '巽宫': '木', 
  '坎宫': '水', 
  '艮宫': '土', 
  '坤宫': '土'
}

let gong_num = {
  '乾宫': 7, 
  '兑宫': 6,
  '离宫': 5, 
  '震宫': 4, 
  '巽宫': 3, 
  '坎宫': 2, 
  '艮宫': 1, 
  '坤宫': 0
}
// 0 0 1 0 1 0   右边为外卦，水，左边为内卦 山
let gua64_names = {
  77: '乾为天', 37: '天风姤', 17: '天山遁', 7: '天地否', 3: '风地观', 1: '山地剥', 5: '火地晋', 75: '火天大有', 
  66: '兑为泽', 26: '泽水困', 6: '泽地萃', 16: '泽山咸', 12: '水山蹇', 10: '地山谦', 14: '雷山小过', 64: '雷泽归妹',
  55: '离为火', 15: '火山旅', 35: '火风鼎', 25: '火水未济', 21: '山水蒙', 23: '风水涣', 27: '天水讼', 57: '天火同人', 
  44: '震为雷', 4: '雷地豫', 24: '雷水解', 34: '雷风恒', 30: '地风升', 32: '水风井', 36: '泽风大过', 46: '泽雷随', 
  33: '巽为风', 73: '风天大畜', 53: '风火家人', 43: '风雷益', 47: '天雷无妄', 45: '火雷噬嗑', 41: '山雷颐', 31: '山风蛊', 
  22: '坎为水', 62: '水泽节', 42: '水雷屯', 52: '水火既济', 56: '泽火革', 54: '雷火丰', 50: '地火明夷', 20: '地水师', 
  11: '艮为山', 51: '山火丰', 71: '山天大畜', 61: '山泽损', 65: '火泽暌', 67: '天泽履', 63: '风泽中孚', 13: '风山渐', 
  0: '坤为地', 40: '地雷复', 60: '地泽临', 70: '地天泰', 74: '雷天大壮', 76: '雷泽中孚', 72: '水天需', 2: '水地比'
}

let animals = ['青龙', '朱雀', '勾陈', '腾蛇', '白虎', '玄武']

let changsheng = ['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养']
let wuxing_changsheng = {
  '木': '亥', 
  '火': '寅', 
  '金': '巳',
  '水': '申',
  '土': '申'
}

let pos_shi = [5, 0, 1, 2, 3, 4, 3, 2]
let pos_ying = [2, 3, 4, 5, 0, 1, 0, 5]

let tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
let dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
let dizhi_wuxing = {
  '子': '水', 
  '丑': '土', 
  '寅': '木', 
  '卯': '木', 
  '辰': '土', 
  '巳': '火', 
  '午': '火', 
  '未': '土', 
  '申': '金', 
  '酉': '金', 
  '戌': '土', 
  '亥': '水'
}
export default {
  components: {
    StrategyModal
  },
  data() {
    return {
        question: '今天天气如何', 
        questions: [],
        records: [],
        loading: false,
        status: '起卦中，请保持专注……'
    };
  },
  async mounted() {

  }, 
  methods: {
    evaluate_one: async function(record, i) {
      // 月建 自身旺，生者相，生我者休，克我者囚，我克者死
      let ke_score = 0
      let sheng_score = 0
      let chong_score = 0
      let strength = 0      
      // 先看月破
      let yuepo = false
      record.result.single[i] += '先看卦中环境因素，'
      if (Math.abs(dizhi.indexOf(record.month[1]) - dizhi.indexOf(record.base_dizhi[i])) == 6) {
        // 月破 +3
        ke_score += 4
        // record.result.single[i] += '正值月破，本卦中整体运势走低，要成事需要加倍认真努力。'
        yuepo = true
      }  
      // 看旺相休囚
      if (bi[record.month[1]].indexOf(record.base_dizhi[i]) >= 0) {
        // 旺
        sheng_score += 3
        record.result.single[i] += '月建 ' + record.month[1] + ' 给予极大的助力，天高任鸟飞，处处有吉星。'
      }
      if (sheng[record.month[1]].indexOf(record.base_dizhi[i]) >= 0) {
        // 相
        sheng_score += 2
        record.result.single[i] += '月建 ' + record.month[1] + ' 生之，在本卦中显示有很大的成长空间。'
      }
      if (sheng[record.base_dizhi[i]].indexOf(record.month[1]) >= 0) {
        // 休
        record.result.single[i] += '泄于月建 ' + record.month[1] + '，外界的环境支持有变弱的趋势，强行行动，可能付出比获得的更多，要谨慎。'
      }
      if (ke[record.base_dizhi[i]].indexOf(record.month[1]) >= 0) {
        // 囚
        record.result.single[i] += '企图克制月建 ' + record.month[1] + '，休囚无力，这种环境，自身很难产生影响，同时宜低调行事以躲避对自身的伤害。'
      } 
      if (ke[record.month[1]].indexOf(record.base_dizhi[i]) >= 0) {
        // 月建克 +3
        ke_score += 3
        record.result.single[i] += '被月建 ' + record.month[1] + ' 所克，宜尽量隐藏实力和躲避。'
      }   
      if (yuepo) {
        record.result.single[i] += '又正值月破，自身力量被严重冲散，所谓人外有人、天外有天，无论如何本月诸事宜低调躲避，自身得以保全。'
      }

      if (bi[record.day[1]].indexOf(record.base_dizhi[i]) >= 0) {
        // 日辰比 +2
        sheng_score += 2
        record.result.single[i] += '日辰 ' + record.day[1] + ' 给予很大的支持，对近期的各种行动都有利。'
      }

      if (sheng[record.day[1]].indexOf(record.base_dizhi[i]) >= 0) {
        // 日辰生 +2
        sheng_score += 1
        record.result.single[i] += '日辰 ' + record.day[1] + ' 生之，短期内可以从周围环境获得不错的支持。'
      }

      if (ke[record.base_dizhi[i]].indexOf(record.day[1]) >= 0) {
        // 日辰克 +2
        record.result.single[i] += '企图克制日辰 ' + record.day[1] + '，但是力量显然不够，当下自身行动上宜低调躲避。'
      }   

      if (sheng[record.base_dizhi[i]].indexOf(record.day[1]) >= 0) {
        // 日辰克 +2
        record.result.single[i] += '泄于日辰 ' + record.day[1] + '，当下宜休养，减少发力，等待时机。'
      }  

      if (ke[record.day[1]].indexOf(record.base_dizhi[i]) >= 0) {
        // 日辰克 +2
        ke_score += 2
        record.result.single[i] += '被日辰 ' + record.day[1] + ' 所克，短期内状态有些低迷，即使整体顺利，也应该注意一些小的波动，如果整体已经不顺，警惕雪上加霜。'
      }   

      if (Math.abs(dizhi.indexOf(record.day[1]) - dizhi.indexOf(record.base_dizhi[i])) == 6) {
        // 日辰冲 +2
        ke_score += 2
        record.result.single[i] += '正值日破，短期内力量难以聚集，应保持低调。'
      }  
      
      // TODO: 
      // 看12长生
      // 获得地支五行
      record.result.single[i] += '再看自身状态，'
      let dwuxing = dizhi_wuxing[record.base_dizhi[i]]
      console.log('开始看地支' + record.base_dizhi[i])
      let changsheng_dizhi = wuxing_changsheng[dwuxing] // 得到长生的dizhi
      let dizhi_idx = dizhi.indexOf(changsheng_dizhi)
      if (record.changsheng == undefined) {
        record.changsheng = []
      }
      

      for (let k = 0; k < 12; k++) {
        if (dizhi[(dizhi_idx + k) % 12] == record.month[1]) {
          console.log("当月处于该爻地支的十二长生序号：" + k)
          record.changsheng[i] = changsheng[k]
          if ([10, 11, 0].indexOf(k) >= 0) {
            // 处于长生区间
            if (ke_score > sheng_score) {
              record.result.single[i] += '虽然外界环境偏差，但是目前处于胎养长生阶段，因此宜努力做好自身的建设，多提高自身的修养，从环境中吸收更多的营养。'
            } else if (ke_score == sheng_score) {
              record.result.single[i] += '目前处于胎养长生阶段，外界打扰不多，宜安静生长，积蓄力量。'
            } else {
              record.result.single[i] += '目前处于胎养长生阶段，所处外界环境很好，应多利用好的环境来快速提高自身，为未来争取更好的起点。'
            }
          }
          if ([1, 2 ,3, 4].indexOf(k) >= 0) {
            // 处于帝旺阶段
            if (ke_score > sheng_score) {
              record.result.single[i] += '虽然外界环境偏差，但是目前处于自身快速发展阶段，即使外界环境虽然不够友好，通过努力和谨慎，承受住压力，积极主动，依然能够创造一番成就。'
            } else if (ke_score == sheng_score) {
              record.result.single[i] += '目前处于快速发展阶段，目前看来外界打扰不多，宜加倍努力，积极主动，同时完善自身，成就更大的事业。'
            } else {
              record.result.single[i] += '处于快速发展阶段，所处外界环境很好，应多利用好的周围的环境，加上自身的努力，积极主动，获得更高的成就。'
            }
          }
          if ([5, 6].indexOf(k) >= 0) {
            // 处于帝旺阶段
            if (ke_score > sheng_score) {
              record.result.single[i] += '外界环境偏差，自身处于休养生息的阶段，因此凡事宜低调，享受已有的成就。'
            } else if (ke_score == sheng_score) {
              record.result.single[i] += '外界打扰不多，宜休养生息，谨慎低调，享受已有的成就。'
            } else {
              record.result.single[i] += '所处环境都还不错，但是总体来说宜休养生息，谨慎低调从事，有机会也可以多帮助他人。'
            }
          }
          if ([7, 8, 9].indexOf(k) >= 0) {
            // 处于帝旺阶段
            if (ke_score > sheng_score) {
              record.result.single[i] += '处于周期的尾声，外界环境偏差，自身也处于偏弱的状态，宜尽量预判和躲避麻烦，尽量保存实力等待新的崛起的机会。'
            } else if (ke_score == sheng_score) {
              record.result.single[i] += '处于周期的尾声，外界打扰不多，宜低调，安静渡过波谷，等待新的崛起机会。'
            } else {
              record.result.single[i] += '处于周期的尾声，虽然所处的环境都还不错，宜低调，不宜主动做事，安静渡过波谷，等待新的崛起机会。'
            }
          }
          break
        }
      }

      if (record.base[i] != record.change[i]) {
        // 发现一个动爻
        // 先看动爻本身的强弱
        record.result.single[i] += '再看卦中的行为，自身发动。'
        
        if (this.iskong(record.day, record.change_dizhi[i])) {
          // 化空，则无效
          record.result.single[i] += '发动至旬空状态，化为虚无，可能错过好事，但是也能避开灾祸。'
        } else {
          if (sheng[record.change_dizhi[i]].indexOf(record.base_dizhi[i]) >= 0) {
            // 化回头生
            // ... 动爻有效
            strength = 1
            record.result.single[i] += '发动而回头生，自身积极性很强，采取行动而且能得到比较好的结果。'
          } else if (ke[record.change_dizhi[i]].indexOf(record.base_dizhi[i]) >= 0) {
            // 化回头克，动爻失效
            record.result.single[i] += '发动而回头克，自身积极性很强，但是有可能行动后会损害自身。'
          } else if (dizhi_wuxing[record.change_dizhi[i]] == dizhi_wuxing[record.base_dizhi[i]]) {
            // 进退神
            if (dizhi.indexOf(record.base_dizhi[i]) < dizhi.indexOf(record.change_dizhi) || (record.base_dizhi[i] == '亥' && record.change_dizhi[i] == '子')) {
              // 进神，动爻有效
              // ...
              strength = 1
              record.result.single[i] += '发动而精进，付出的行动得到了好的回报。'
            } else {
              // 退神，动爻效力减弱
              // ...
              record.result.single[i] += '发动但却有所衰退，可能努力方向有所偏差。'
            }
          } else if (sheng[record.base_dizhi[i]].indexOf(record.change_dizhi[i]) >= 0) {
            record.result.single[i] += '发动而泄, 若有行动，恐难有收益，宜三思而行。'
          } else if (ke[record.base_dizhi[i]].indexOf(record.change_dizhi[i]) >= 0) {
            record.result.single[i] += '发动而克, 可能弄巧成拙，因此需谨慎行事。'
          }
          if (Math.abs(dizhi.indexOf(record.change_dizhi[i]) - dizhi.indexOf(record.base_dizhi[i])) == 6) {
            chong_score += 1
            record.result.single[i] += '发动但是却得到比较强的响应，无论好坏，有愈演愈烈之势。'
          }
        }
      } else {
        record.result.single[i] += '卦中行为安静，因此当下不会有太大的变化。'
      }
      if (strength == 0) {
        // 如果是用神
        if (record.yongshen_idx == i) {
          strength = 1
        } 
      }
      if (record.result.single[i] == '') {
        record.result.single[i] = '很安静，没有打扰，也意味着状态停滞，正是修炼内功的好时机。'
      }
      return {
        base_score: (sheng_score - ke_score) * strength, 
        chong_score: chong_score
      }
    }, 
    evaluate: async function(record) {
      // 先看是否与“世”“应”有关。
      let shiValid = '否' //await chatShiValid(record.question)
      let yingValid = '否' // await chatYingValid(record.question)

      shiValid = shiValid.replaceAll('\"', '')
      yingValid = yingValid.replaceAll('\"', '')
      // 看用神是否旬空
      record.yongshen_kong = this.iskong(record.day, record.yongshen_dizhi)

      // 看用神本神的强弱
      // 看月建的影响
      record.score = []
      for (let i = 0; i < 6; i++) {
        // 看卦中动爻
        record.score.push(await this.evaluate_one(record, i))
        // 得到每一爻的强弱
      }
      let yongshen_score = {base_score: 0}
      // 开始分析用神
      if (record.fushen_idx >= 0) {
        // 看飞神
        record.result.single[record.fushen_idx] += '在本卦中，真正的用神伏于飞神之下，地支为 ' + record.fushen_dizhi + '。'
        if (record.score[record.fushen_idx].base_score > 0) {
          // 飞神有力
          if (sheng[record.base_dizhi[record.fushen_idx]].indexOf(record.fushen_dizhi) >= 0) {
            record.result.single[record.fushen_idx] += '飞神有力生伏神，大利用神，事情会顺利。'
          } else if (ke[record.base_dizhi[record.fushen_idx]].indexOf(record.fushen_dizhi)) {
            record.result.single[record.fushen_idx] += '飞神有力克伏神，对用神不利，所问之事受阻。'
          } 
        }


        if (sheng[record.base_dizhi[record.fushen_idx]].indexOf(record.fushen_dizhi) >= 0) {
          record.result.single[record.fushen_idx] += '在本卦中，真正的用神伏于飞神之下，地支为 ' + record.fushen_dizhi + '。'
          yongshen_score.base_score = record.score[record.fushen_idx].base_score
        } else if (ke[record.base_dizhi[record.fushen_idx]].indexOf(record.fushen_dizhi) >= 0) {
          yongshen_score.base_score = - record.score[record.fushen_idx].base_score
        }
        //飞神如果弱，伏神可冒头

      } else {
        // 没有伏神就用本爻的score
        if (record.score[record.yongshen_idx] != undefined) {
          yongshen_score = record.score[record.yongshen_idx]
        }
      }

      // 处理原神、忌神和仇神
      for (let i = 0; i < 6; i++) {
        if (record.yuanshen.indexOf(i) >= 0) {
          // 一个原神，看有没有仇神
          for (let j = 0; j < 6; j++) {
            if (i != j) {
              if (record.choushen.indexOf(j) >= 0) {
                record.score[i].base_score -= record.score[j].base_score
                if (record.score[i].base_score < 0) {
                  record.score[i].base_score = 0
                }
              }
            }
          }
          yongshen_score.base_score += record.score[i].base_score
        }
        if (record.jishen.indexOf(i) >= 0) {
          for (let j = 0; j < 6; j++) {
            if (i != j) {
              if (record.choushen.indexOf(j) >= 0) {
                record.score[i].base_score += record.score[j].base_score
              }
            }
          }
          yongshen_score.base_score -= record.score[i].base_score
        }
      }

      // 处理世应

      console.log(yongshen_score)
      let prompt = '你是一个善用六爻八卦预测一代宗师，你通过解读卦象来回答问题。我先给你一些前提条件：通过摇卦，得出卦象为：' + record.name
      prompt = "。我们开始分析卦象，几个基本的概念: " + 
      "六兽之中，青龙在东方，代表五行之中的木，代表正直积极的属性；" + 
      "白虎位于东方，代表五行之中的金，代表财富属性；" + 
      "朱雀位于南方，代表五行之中的火，代表可能有口舌是非；" + 
      "玄武位于北方，代表五行之中的水；" + 
      "勾陈在中心方位，代表五行之中的土，表示地产、资产相关的事情" + 
      "腾蛇也在中心方位，代表五行之中的土，有狡诈、阴谋的属性。" + 
      "卦中的世爻代表了问卦者自身，如果用神的地支生世爻的地支，那么说明所问之事对问卦之人极好，如果用神地支克世爻的地支，一般说明所问之事对问卦之人不好，但是" + 
      "有一种特殊情况，如果用神位于六亲妻财之上，用神地支克世爻地支，说明问卦之人所问和金钱、爱情相关的事情会主动来找他；" + 
      "如果世爻地支克用神，说明问卦之人正在努力追求所问之事或者人；" + 
      "如果世爻地支生用神地支，说明问卦之人需要付出努力才能得到好的结果；" + 
      "如果用神地支和世爻地支的五行属性相同，说明此事正在顺利进展。" + 
      "如果世爻属于旬空状态，说明问卦之人可能会暂时错过所问之事，短期内不受事情影响；如果用神属于旬空状态，说明所问之事或者所问之人，因为某些原因，暂时没有动作或者进展。" + 
      "如果所问的问题中出现了问卦之人之外的其他人，那么应爻的状态就代表这其他人。" + 
      "如果应爻地支克世爻地支，说明应爻对应之人主动性更强；" + 
      "如果应爻地支生世爻地支，说明应爻对应之人对问卦之人有利；" + 
      "如果世爻地支生应爻地支，说明问卦之人需要耗费精力帮助对方；" + 
      "如果世爻地支克应爻地支，说明问卦之人的主动性比对方更强；" + 
      "如果世爻地支和应爻地支五行属性相同，说明双方可能有很好的合作关系；" + 
      "如果应爻处于旬空状态，那么应爻对应之人可能在短期内无法起到有效作用，也不大受事情的影响。" + 
      "如果问题和升迁晋级、考试就业、功名事业等相关，官鬼和世爻在同一爻是好事，子孙和世爻在同一爻是坏事。" + 
      "如果问身体、疾病相关，官鬼和世爻在同一爻是坏事，子孙和世爻在同一爻是好事。" + 
      "如果问财运相关，兄弟和世爻在同一爻是坏事，妻财和世爻在同一爻是好事。" +
      "如果问婚姻恋爱，如果是男人问，遇到兄弟和世爻在同一爻是坏事；如果是女人问，遇到子孙和世爻在同一爻是坏事。" + 
      "如果问父母长辈相关的事情，妻财和世爻在同一爻是坏事。" + 
      "如果问子孙的事情，父母和世爻在同一爻是坏事。" +
      "如果问解忧避难，喜庆财利之事，子孙和世爻在同一爻是好事。"

      if (record.name != record.change_name) {
        prompt += " 之 " + record.change_name
      }
      prompt += '。'
      prompt += '用神地支为' + record.yongshen_dizhi + '，用神的六亲代表' + record.yongshen + '，坐于' + record.animal[record.yongshen_idx] + "之上。"

      if (shiValid == '是') {
        prompt += '世爻代表问问题的人，它在从下往上数第' + (record.shi + 1) + '爻。世爻地支是' + record.base_dizhi[record.shi] + ', 世爻和' + this.getliuqin(record.gong, record.base_dizhi[record.shi]) + ' 在同一爻上。'
        prompt += '从卦象上分析，世爻所代表的问卦人自身的情况是：' + record.result.single[record.shi] + '总的来说，'
        if (record.score[record.shi].base_score > 1) {
          prompt += '世爻状态很好。'
        } else if (record.score[record.shi].base_score < -1) {
          prompt += '世爻状态不好。'
        } else if (record.score[record.shi].base_score > 0) {
          prompt += '世爻状态还可以。'
        } else if (record.score[record.shi].base_score < 0) {
          prompt += '世爻状态不算太好。'
        } else {
          prompt += '世爻状态不好也不坏。'
        }


        if (record.score[record.shi].chong_score > 0) {
          prompt += '世爻最近因为外界的影响有些急躁和不稳定。'
        }
        if (this.iskong(record.day, record.base_dizhi[record.shi])) {
          prompt += '世爻处于旬空状态。'
        }
      }
      if (yingValid == '是' && !record.yongshen_is_ying) {
        prompt += '应爻代表问题中的其他人，它在从下往上数第' + (record.ying + 1) + '爻。世爻地支是' + record.base_dizhi[record.ying] + '。'
        prompt += '从卦象上分析，应爻所代表的问题中的其他人的情况是：' + record.result.single[record.ying] + '总的来说，'
        if (record.score[record.ying].base_score > 1) {
          prompt += '应爻状态很好。'
        } else if (record.score[record.ying].base_score < -1) {
          prompt += '应爻的状态不好。'
        } else if (record.score[record.ying].base_score > 0) {
          prompt += '应爻的状态还可以。'
        } else if (record.score[record.ying].base_score < 0) {
          prompt += '应爻的状态不算太好。'
        } else {
          prompt += '应爻的状态不好也不坏。'
        }
        if (record.score[record.ying].chong_score > 0) {
          prompt += '应爻最近有些急躁和不稳定。'
        }
        if (this.iskong(record.day, record.base_dizhi[record.ying])) {
          prompt += '应爻处于旬空状态。'
        }
      }
      prompt += '用神代表所问之事。'
      if (record.is_month_yongshen) {
        prompt += '本卦之中，用神直接处于月建之上，凡事无往不利，行事之人只需要保持理性正直，所问之事一定会有好的结果。'
      } else if (record.is_day_yongshen) {
        prompt += '本卦之中，用神直接处于日辰之上，当前应是顺风顺水，只要行事之人保持理性正直，所问之事将赢得加速发展。'
      }

      prompt += '从卦象上分析，用神的情况是：' + record.result.single[record.yongshen_idx] + '总的来说，'
      if (yongshen_score.base_score > 1) {
        prompt += '用神的状态特别好。'
      } else if (yongshen_score.base_score < -1) {
        prompt += '用神的状态特别不好。'
      } else if (yongshen_score.base_score > 0) {
        prompt += '用神的状态还算顺利。'
      } else if (yongshen_score.base_score < 0) {
        prompt += '用神不算太顺利。'
      } else if (yongshen_score.base_score == 0) {
        prompt += '用神的状态感觉比较停滞。'
      }
      if (yongshen_score.chong_score > 0) {
        prompt += '我问的事情现在有些蠢蠢欲动了。'
      }
      if (record.iskong) {
        prompt += '用神旬空了，暂时无法发动。'
      }


      prompt += 
                  '如果问题与我自己无关，问的是别人的事情，而且问题中没有出现与自己的直接关系，那么回答中直接用被问的人作主语。回答中不要出现"世爻"、"用神"等专业术语，可以使用对应的人名或者事物或者事件替代，使用通俗易懂的语言进行回答。回答的风格应该积极向上，即使不好的事情都应该用比较积极的语言表达和鼓励。' + 
                  '请结合以上的信息，以及现在的时间 ' + record.year + '年' + record.month + '月' + record.day +'日' + record.hour + '时，' + 
                  '问题是：' + record.question + '。 回答（使用问题相同的语言）：'
      console.log(prompt)
      record.answer = '' // await chat(prompt)
      console.log(record.answer)
      // 分析用神
    }, 
    getgongwuxing: function(gong) {
      return gong_wuxing[gong]
    }, 
    getnum: function(gua) {
      let num = (gua[0] * 4 + gua[1] * 2 + gua[2]) * 10 + (gua[3] * 4 + gua[4] * 2 + gua[5])
      return num
    },
    getliuqin: function(gong, dizhi) {
        return liuqin[gong][dizhi]
    }, 
    iskong: function(day, dz) {
      // 检查地支是否在当日旬空
      if ((dizhi.indexOf(day[1]) - (1 + tiangan.indexOf(day[0])) + 12) % 12 == dizhi.indexOf(dz) || (dizhi.indexOf(day[1]) - (1 + tiangan.indexOf(day[0])) + 11) % 12 == dizhi.indexOf(dz)) {
        return true
      } else {
        return false
      }
    }, 
    jiegua: async function(record) {
      // 先找到用神
      record.yongshen = '妻财' // await chatYongshen(this.question)
      record.yongshen = record.yongshen.replaceAll("\"", '').replaceAll("\'", '')
      if (['父母', '官鬼', '子孙', '妻财', '兄弟'].indexOf(record.yongshen) < 0) {
        // 说明没有用神，则以应爻为用神
        record.yongshen = this.getliuqin(record.gong, record.base_dizhi[record.ying])
        record.yongshen_is_ying = true
      }
      else {
        record.yongshen_is_ying = false
      }
      let yongshen_idx = -1
      for (let i = 0; i < 6; i++) {
        // 开始找用神的地支
        if (this.getliuqin(record.gong, record.base_dizhi[i]) == record.yongshen) {
          if (yongshen_idx == -1) {
            // 第一次遇到用神，记下来地支
            yongshen_idx = i
          } else {
            // 不是第一次遇到，几个原则：
            // 看是否动爻
            if (record.base[i] != record.change[i]) {
              yongshen_idx = i
            } else if (i == record.shi) {
              // 是否持世
              yongshen_idx = i
            } else if (record.base_dizhi[i] == record.month[1] && record.base_dizhi[yongshen_idx] != record.month[1]) {
              // 是否月建
              yongshen_idx = i
            } else if (record.base_dizhi[i] == record.day[1] && record.base_dizhi[yongshen_idx] != record.day[1]) {
              // 是否日辰
              yongshen_idx = i
            } else if (record.base_dizhi[i] == (dizhi.indexOf(record.month[1]) + 6) % 12) {
              // 是否月破
              yongshen_idx = i
            } else if (this.iskong(record.day, record.base_dizhi[i])) {
              // 是否旬空
              yongshen_idx = i
            } else {
              // 看离世爻的距离
              if (Math.abs(i - record.shi) < Math.abs(yongshen_idx - record.shi)) {
                yongshen_idx = i
              }
            }
          }
        }
      }
      record.yongshen_idx = yongshen_idx
      record.is_month_yongshen = false
      record.is_day_yongshen = false
      record.fushen_idx = -1
      record.fushen_dizhi = ''
      if (record.yongshen_idx == -1) {
        // 用神不上卦
        /*
        if (this.getliuqin(record.gong, record.month[1]) == record.yongshen) {
          // 用神为月建
          record.is_month_yongshen = true
          record.yongshen_dizhi = record.month[1]
        } else if (this.getliuqin(record.gong, record.day[1]) == record.yongshen) {
          record.is_day_yongshen = true
          record.yongshen_dizhi = record.day[1]
        } else {
        */
        // 向本宫八纯卦借用神
        for (let i = 0; i < 3; i++) {
          if (this.getliuqin(record.gong, nei_dizhi[gong_num[record.gong]][i]) == record.yongshen) {
            // 借来一个伏神
            record.fushen_idx = i
            record.yongshen_idx = i
            record.fushen_dizhi = nei_dizhi[gong_num[record.gong]][i]
            record.yongshen_dizhi = nei_dizhi[gong_num[record.gong]][i]
          }
        }
        if (record.fushen_idx == -1) {
          // 向外卦借
          for (let i = 0; i < 3; i++) {
            if (this.getliuqin(record.gong, wai_dizhi[gong_num[record.gong]][i]) == record.yongshen) {
              // 借来一个伏神
              record.fushen_idx = i + 3
              record.yongshen_idx = i + 3
              record.fushen_dizhi = wai_dizhi[gong_num[record.gong]][i]
              record.yongshen_dizhi = wai_dizhi[gong_num[record.gong]][i]
            }
          }            
        }
        
      } else {
        record.yongshen_dizhi = record.base_dizhi[record.yongshen_idx]
      }
      record.yuanshen = []
      record.jishen = []
      record.choushen = []
      for (let i = 0; i < 6; i++) {
        // 原神
        if (sheng[record.base_dizhi[i]].indexOf(record.yongshen_dizhi) >= 0) {
          record.yuanshen.push(i)
        }
        if (ke[record.base_dizhi[i]].indexOf(record.yongshen_dizhi) >= 0) {
          record.jishen.push(i)
        }
      }
      if (record.yuanshen.length > 0) {
        for (let i = 0; i < 6; i++) {
          if (ke[record.base_dizhi[i]].indexOf(record.base_dizhi[record.yuanshen[0]]) >= 0) {
            record.choushen.push(i)
          }
        }
      }
      if (record.jishen.length > 0) {
        for (let i = 0; i < 6; i++) {
          if (sheng[record.base_dizhi[i]].indexOf(record.base_dizhi[record.jishen[0]]) >= 0) {
            record.choushen.push(i)
          }
        }
      }
    }, 
    yaogua: async function() {
        // 0 为交爻 （老阴），7为重爻（老阳），1，2，4为阳爻，3，5，6为阴爻
        this.loading = true
        let base = []
        let change = []
        let base_dizhi = []
        let change_dizhi = []
        let animal = []
        let record = {}
        for (let i = 0; i < 6; i++) {
            let yao = Math.floor(Math.random() * 8) % 8
            if (yao == 0) {
              base.push(0)
              change.push(1)
            } else if (yao == 1) {
              base.push(1)
              change.push(0)
            } else if ([1,2,4].indexOf(yao) >= 0) {
              base.push(1)
              change.push(1)
            } else {
              base.push(0)
              change.push(0)
            }
        }
        // 找到宫位
        let num = this.getnum(base)
        let change_num = this.getnum(change)
        for (let key in gua64) {
          if (gua64[key].indexOf(num) >= 0) {
            record.gong = key
            record.order = gua64[key].indexOf(num)
            record.name = gua64_names[num]
            // 世应
            record.shi = pos_shi[record.order]
            record.ying = pos_ying[record.order]
            let idx = Math.floor(num / 10)
            let change_idx = Math.floor(change_num / 10)
            // 挂地支
            for (let i = 0; i < 3; i++) {
              // 内卦地支
              base_dizhi.push(nei_dizhi[idx][i])
              if (change[i] != base[i]) {
                // 有变化
                change_dizhi.push(nei_dizhi[change_idx][i])
              } else {
                // 没变化，填null
                change_dizhi.push(null)
              }
            }

            idx = num % 10
            change_idx = change_num % 10
            for (let i = 0; i < 3; i++) {
              // 外卦地址
              base_dizhi.push(wai_dizhi[idx][i])
              if (change[i + 3] != base[i + 3]) {
                // 有变化
                change_dizhi.push(nei_dizhi[change_idx][i])
              } else {
                // 没变化，填null
                change_dizhi.push(null)
              }
            }
            // 挂六亲
            // 可以根据gong和地支直接查到
            // 省略

            // 获取当前干支来挂六兽
            const todayDate = new Date();
            let ret = LunarCalendar.solarToLunar(todayDate.getFullYear(), todayDate.getMonth() + 1, todayDate.getDate())
            let start = 0
            if (ret.GanZhiDay[0] == '甲' || ret.GanZhiDay[0] == '乙') {
                start = 0
            } else if (ret.GanZhiDay[0] == '丙' || ret.GanZhiDay[0] == '丁') {
                start = 1
            } else if (ret.GanZhiDay[0] == '戊') {
                start = 2
            } else if (ret.GanZhiDay[0] == '己') {
                start = 3
            } else if (ret.GanZhiDay[0] == '庚' || ret.GanZhiDay[0] == '辛') {
                start = 4
            } else if (ret.GanZhiDay[0] == '壬' || ret.GanZhiDay[0] == '癸') {
                start = 5
            }

            for (let i = 0; i < 6; i++) {
                animal.push(animals[(i + start) % 6])
            }
            let hour = todayDate.getHours()
            hour = tiangan[(Math.floor((hour-1) / 2) + 2 * (tiangan.indexOf(ret.GanZhiDay[0]) + 1) - 1) % 10 ] + dizhi[Math.floor((hour + 1) / 2) % 12] 
            record.animal = animal
            record.base = base
            record.change = change
            record.change_name = gua64_names[change_num]
            record.year = ret.GanZhiYear
            record.month = ret.GanZhiMonth
            record.day = ret.GanZhiDay
            record.hour = hour
            record.base_dizhi = base_dizhi
            record.change_dizhi = change_dizhi
            
            
            console.log(this.questions)
            // 起卦身
            if (record.base[record.shi] == 0) {
                // 阴爻持世
                record.guashen = dizhi[6 + record.shi]
            } else {
                record.guashen = dizhi[record.shi]
            }

            
            record.question = this.question

            // 评估每一爻的能力
            record.evaluation = []
            this.status = '开始装卦……'
            await this.jiegua(record)
            this.status = '解卦中，稍等片刻……'
            record.result = {
              'single': ['', '', '', '', '', ''], 
              'combo': {}
            }
            await this.evaluate(record)
            this.records.splice(0, 0, record)
            this.questions.splice(0, 0, this.question)
            break
          }
        }
        this.loading = false
    }
  }
};
</script>

<style scoped>
    .right-content {
        flex: 1; /* 充满剩余空间 */
        padding: 1rem;
        color: #333
    }
    .demo-spin-container{
        display: inline-block;
        width: 100%;
        height: 100px;
        position: relative;
        border: 1px solid #eee;
    }
</style>
  