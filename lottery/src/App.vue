<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
    <router-view name="root">
    </router-view>
</template>


<style lang="scss">
$header-height: 40px;
#app {
  font-family: "Segoe UI", "Microsoft YaHei", Arial;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333333;
}
#nav {
  padding: 30px;
  a {
    font-weight: bold;
    color: #2c3e50;
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}

#adalIdTokenFrame {
  display: none;
}
</style>
<style lang="scss" scoped>
    body, html {
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
    }



    #btn {
      width: 30px;
      height: 32px;
      line-height: 32px; 
      text-align: center;
      position: fixed;
      right: 0px;
      bottom: 100px;
      color: #fff;
      background-color: #2d8cf0;
      border-color: #2d8cf0;
      border: none;
      outline: none;
      cursor: pointer;
      z-index: 1000;
    }
.layout-con {
  height: 100%;
  width: 100%;
}

.header {
  height: 40px;
  text-align: left;
  padding-left: 15px;
}
.menu-item span {
  display: inline-block;
  overflow: hidden;
  width: 69px;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
  transition: width 0.2s ease 0.2s;
}
.menu-item i {
  transform: translateX(0px);
  transition: font-size 0.2s ease, transform 0.2s ease;
  vertical-align: middle;
  font-size: 16px;
}
.collapsed-menu span {
  width: 0px;
  transition: width 0.2s ease;
}
.collapsed-menu i {
  transform: translateX(5px);
  transition: font-size 0.2s ease 0.2s, transform 0.2s ease 0.2s;
  vertical-align: middle;
  font-size: 22px;
}
</style>