import { ref, computed } from 'vue'
import locales from '../locales'

const currentLocale = ref(localStorage.getItem('locale') || 'zh')

const t = computed(() => {
  return (key) => locales[currentLocale.value]?.[key] || locales['en']?.[key] || key
})

function setLocale(locale) {
  if (locales[locale]) {
    currentLocale.value = locale
    localStorage.setItem('locale', locale)
  }
}

function getLocale() {
  return currentLocale.value
}

export function useI18n() {
  return { t, setLocale, getLocale, locale: currentLocale }
}
