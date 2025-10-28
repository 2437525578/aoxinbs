<template>
  <el-container class="common-layout">
    <el-aside width="200px" class="common-aside">
      <el-menu
        :default-active="activeMenu"
        :key="activeMenu"
        class="el-menu-vertical-demo"
        background-color="#ffffff"
        text-color="#000000"
        active-text-color="#409EFF"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <i class="el-icon-menu"></i>
          <span slot="title">后台首页</span>
        </el-menu-item>
        <el-sub-menu index="users">
          <template #title>
            <i class="el-icon-location"></i>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/users/teacher">教师用户</el-menu-item>
          <el-menu-item index="/users/student">学生用户</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="chemicals">
          <template #title>
            <i class="el-icon-document"></i>
            <span slot="title">危化品管理</span>
          </template>
          <el-menu-item index="/chemicals/encyclopedia">危化品信息管理</el-menu-item>
          <el-menu-item index="/chemicals/warehouse">实验仓库危化品管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="purchase">
          <template #title>
            <i class="el-icon-setting"></i>
            <span slot="title">采购管理</span>
          </template>
          <el-menu-item index="/purchase/application">采购申请管理</el-menu-item>
          <el-menu-item index="/purchase/inbound">采购入库管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="borrow">
          <template #title>
            <i class="el-icon-setting"></i>
            <span slot="title">领用管理</span>
          </template>
          <el-menu-item index="/borrow/application">领用申请管理</el-menu-item>
          <el-menu-item index="/borrow/outbound">领用出库管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="scrap">
          <template #title>
            <i class="el-icon-setting"></i>
            <span slot="title">报废管理</span>
          </template>
          <el-menu-item index="/scrap/application">报废申请管理</el-menu-item>
          <el-menu-item index="/scrap/outbound">报废出库管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="allocation">
          <template #title>
            <i class="el-icon-setting"></i>
            <span slot="title">调配管理</span>
          </template>
          <el-menu-item index="/allocation/application">调配申请管理</el-menu-item>
          <el-menu-item index="/allocation/inbound">调配入库管理</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="common-header">
        <el-row type="flex" justify="space-between" align="middle" style="height: 100%;">
          <el-col :span="12">
            <div style="display: flex; align-items: center;">
              <img src="/favicon.ico" alt="Logo" class="header-logo" />
              <span class="header-title">欢迎使用高校实验室危化品管理系统</span>
            </div>
          </el-col>
          <el-col :span="12" style="text-align: right;">
            <!-- 用户信息区域保持不变 -->
          </el-col>
        </el-row>
        <!-- 新增标签页容器 -->
        <el-tabs v-model="activeTab" type="card" closable @tab-remove="handleTabRemove" @tab-click="handleTabClick" style="margin-top: 10px;">
          <el-tab-pane v-for="tab in tabs" :key="tab.path" :label="tab.title" :name="tab.path">
          </el-tab-pane>
        </el-tabs>
      </el-header>
      <el-main class="common-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ElContainer, ElAside, ElHeader, ElMain, ElMenu, ElSubMenu, ElMenuItem, ElRow, ElCol, ElDropdown, ElDropdownMenu, ElDropdownItem, ElMessage, ElLoading, ElTabs, ElTabPane } from 'element-plus';
import { ArrowDown } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import { ref, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
 // 新增Pinia store引入
 import { useTabsStore } from '@/stores/tabs';
 
 // 初始化标签页状态
 const tabsStore = useTabsStore();
 const tabs = ref(tabsStore.tabs);
 const activeTab = ref(tabsStore.activeTab);
 
 const router = useRouter();
 const activeMenu = ref('');
 
 watch(() => router.currentRoute.value.path, (newPath) => {
   activeMenu.value = newPath;
 }, { immediate: true });
 
 watch(activeTab, (newPath) => {
  if (newPath) {
    router.push(newPath);
  }
});

watch(() => router.currentRoute.value.path, (newPath) => {
  if (newPath && newPath !== activeTab.value) {
    const matchedRoute = router.resolve(newPath);
    if (matchedRoute.meta && matchedRoute.meta.title) {
      tabsStore.addTab({ path: newPath, title: matchedRoute.meta.title });
    } else {
      // Fallback to route name if meta.title is not available
      tabsStore.addTab({ path: newPath, title: matchedRoute.name.toString() });
    }
    activeTab.value = newPath;
  }
});

// 处理侧边栏菜单选择事件
const handleMenuSelect = (key, keyPath) => {
  const menuMap = {
    '/dashboard': '后台首页',
    '/users/teacher': '教师用户',
    '/users/student': '学生用户',
    '/chemicals/encyclopedia': '危化品信息管理',
    '/chemicals/warehouse': '实验仓库危化品管理',
    '/purchase/application': '采购申请管理',
    '/purchase/inbound': '采购入库管理',
    '/borrow/application': '领用申请管理',
    '/borrow/outbound': '领用出库管理',
    '/scrap/application': '报废申请管理',
    '/scrap/outbound': '报废出库管理',
    '/allocation/application': '调配申请管理',
    '/allocation/inbound': '调配入库管理',
  };
  if (menuMap[key]) {
    tabsStore.addTab({ path: key, title: menuMap[key] });
    router.push(key);
  }
};

// 处理标签页关闭事件
const handleTabRemove = (targetName) => {
  tabsStore.removeTab(targetName);
  tabs.value = tabsStore.tabs;
  activeTab.value = tabsStore.activeTab;
};

// 处理标签页点击事件
const handleTabClick = (tab) => {
  activeTab.value = tab.props.name; // 显式更新 activeTab
  router.push(tab.props.name);
};

// 原有逻辑保持不变
// const router = useRouter(); // 移除重复声明
const username = ref('');
const authStore = useAuthStore();

onMounted(() => {
  if (authStore.isAuthenticated) {
    username.value = authStore.user.username || '用户';
  }
});

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.clearAuthInfo();
    ElMessage.success('退出登录成功！');
    router.push('/login');
  } else if (command === 'changePassword') {
    router.push('/change-password');
  }
};
</script>

<style scoped>
/* 新增标签页样式 */
.el-tabs--card > .el-tabs__header .el-tabs__item {
  margin-right: 8px;
}
.common-header {
  padding-bottom: 0 !important;
  height: auto !important; /* 允许高度自适应 */
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.el-tabs--card {
  flex-grow: 1;
  overflow: hidden; /* 确保内容不会溢出 */
}

.el-tabs__header {
  margin: 0;
  border-bottom: 1px solid #e4e7ed;
  white-space: nowrap; /* 确保标签不换行 */
  overflow-x: auto; /* 允许水平滚动 */
  -webkit-overflow-scrolling: touch; /* 改善移动端滚动体验 */
}

.el-tabs__nav-wrap {
  margin-bottom: 0;
}

.el-tabs__nav-scroll {
  overflow: hidden;
}

.el-tabs__nav {
  display: flex;
  flex-wrap: nowrap; /* 确保标签不换行 */
}

.el-tabs__item {
  flex-shrink: 0; /* 防止标签收缩 */
  padding: 0 20px; /* 调整标签内边距 */
}

.el-tabs__item.is-active {
  background-color: #E0F2F7 !important; /* 选中时背景变为浅蓝色 */
  color: #409EFF !important; /* 选中时文字变为蓝色 */
}
.el-menu-vertical-demo .el-menu-item.is-active {
  background-color: #E0F2F7 !important; /* 选中时背景变为浅蓝色 */
  color: #409EFF !important; /* 选中时文字变为蓝色 */
}

/* 原有样式保持不变 */
</style>