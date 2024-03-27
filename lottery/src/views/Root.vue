<template>
    <div  class="layout-base">
        <Layout>
            <Sider
                class="layout-sider"
                >
            <Menu width="auto"
                @on-select="onSelectMenu"
                    >
                    <MenuItem name="recommend">
                    Recommend</MenuItem>
                    <MenuItem name="history">
                    History</MenuItem>
                    <MenuItem name="bagua">
                    起卦</MenuItem>
                    <MenuItem name="cf">
                    有害内容识别</MenuItem>
                    <MenuItem name="stock">
                    股票分析</MenuItem>
                    <MenuItem name="agentfeed">
                    Agent养成</MenuItem>
            </Menu>

            </Sider>
            <Layout>
            <Content class="layout-content">
                <router-view/>
            </Content>
            </Layout>
      </Layout>
    </div>

  </template>
  
<script>
import { MenuItem } from 'view-ui-plus';

  
    export default {
    async created() {
    },
    computed: {},
    data: function () {
        return {};
    },
    beforeRouteUpdate(to, from, next) {
        this.currentRouteName = to.name;
        this.currentRouteUrl = to.path;
        next();
    },
    methods: {
        onSelectMenu: function(name) {
      switch (name) {
        case "recommend":
          this.$router.push({ name: "Recommend" });
          break;
        case "history":
          this.$router.push({ name: "History" });
          break;
        case "bagua":
          this.$router.push({ name: "Liuyao" });
          break;
        case "cf":
          this.$router.push({ name: "ContentFilter" });
          break;
        case "stock":
          this.$router.push({ name: "Stock" });
          break;
        case "agentfeed":
          this.$router.push({ name: "AgentFeed" });
          break;
      }
    }
    },
    components: { MenuItem }
};
</script>

<style scoped>

.layout-base{
    border: 1px solid #d7dde4;
    background: #f5f7f9;
    color: white;
    text-align: center;
    overflow: hidden;
    width: 100%;
    height: 100%;
    margin: 0; 
    padding: 0
}
.layout-base > .ivu-layout {

}
.layout-con{
    overflow: hidden;
    text-align: center;
}
.layout-single{
    font-size: 14px;
    color: white;
}
.layout-con:last-child{
    margin: 0;
}
.layout-logo{
    width: 100px;
    height: 30px;
    background: #5b6270;
    border-radius: 3px;
    float: left;
    position: relative;
    top: 15px;
    left: 20px;
}
.layout-nav{
    width: 420px;
    margin: 0 auto;
        margin-right: 20px;
}
.layout-breadcrumb{
    padding: 10px 15px 0;
}
.layout-logo-left{
    width: 90%;
    height: 30px;
    background: #5b6270;
    border-radius: 3px;
    margin: 15px auto;
}
.layout-hide-text .layout-text{
    display: none;
}
.layout-header,
.layout-footer{
    background: #7CBCE9;
    color: white;
}
.layout-content{
    background: #EEE;
    min-height: 40px;
    line-height: 40px;
}
.layout-sider{
    background: #3A9FE8;
    min-height: 120px;
    line-height: 120px;
}
.layout-footer-center{
    text-align: center;
}
.layout iframe{
    width: 100%;
    border: 0;
}
.layout-header-bar{
    background: #fff;
    box-shadow: 0 1px 1px rgba(0,0,0,.1);
}


</style>
