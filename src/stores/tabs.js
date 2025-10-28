import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useTabsStore = defineStore('tabs', () => {
  const tabs = ref([]);
  const activeTab = ref('');

  function addTab(tab) {
    if (!tabs.value.some(t => t.path === tab.path)) {
      tabs.value.push(tab);
    }
    activeTab.value = tab.path;
  }

  function removeTab(targetPath) {
    const tabsToKeep = tabs.value.filter(tab => tab.path !== targetPath);
    if (activeTab.value === targetPath) {
      const lastTab = tabsToKeep[tabsToKeep.length - 1];
      activeTab.value = lastTab ? lastTab.path : '/';
    }
    tabs.value = tabsToKeep;
  }

  return { tabs, activeTab, addTab, removeTab };
});