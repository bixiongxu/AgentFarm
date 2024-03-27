<template>
    <div class="right-content">

        <Input v-model="question" placeholder="请输入文本检测有害内容" type="textarea"/>
        <BR/>
        严格程度（1～7，越大越宽松）:
        <Input v-model="bar" style="width: 200px" show-input min="1" max="7" step="1" type="number" @on-change="set_result" :disabled="!raw_result" size="small"></Input>
        <Button @click="filter()">检测</Button>
        <div v-for="(v, key) in result">
            {{ key }}: 
              <span style="color: red" v-if="v">Yes</span>
              <span style="color: black" v-if="!v">No</span>
            <BR/>
        </div>
    </div>
  </template>
  
<script>
import {filter} from '@/api/cf'

export default {
  components: {
    
  },
  data() {
    return {
        question: '今天天气如何', 
        raw_result: null, 
        result: {
          '自我伤害': false,
          '色情': false,
          '暴力': false,
          '歧视': false
        },
        bar: 2
    };
  },
  async mounted() {

  }, 
  watch: {

  },
  methods: {
    async filter() {
        let result = await filter(this.question)
        console.log(result)
        this.raw_result = result
        this.set_result()
    }, 
    set_result: function() {
      if (this.bar > 7) {
        this.bar = 7
      }
      if (this.bar <= 0) {
        this.bar = 1
      }
      if (this.raw_result) {
        this.result['自我伤害'] = this.raw_result['predicted_labels']['self-harm'][this.bar] > 0 ? true : false
        this.result['歧视'] = this.raw_result['predicted_labels']['hate'][this.bar] > 0 ? true : false
        this.result['色情'] = this.raw_result['predicted_labels']['sexual'][this.bar] > 0 ? true : false
        this.result['暴力'] = this.raw_result['predicted_labels']['violence'][this.bar] > 0 ? true : false
      }
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
  