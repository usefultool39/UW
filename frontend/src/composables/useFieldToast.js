import { nextTick, ref } from 'vue'

export function useFieldToast() {
  const toastMessage = ref('')
  const toastType = ref('info')
  const toastOpen = ref(false)
  let toastTimer = null

  function showToast(msg, type = 'info') {
    toastMessage.value = msg
    toastType.value = type
    clearTimeout(toastTimer)
    toastOpen.value = false
    nextTick(() => {
      toastOpen.value = true
    })
  }

  function clearToastTimer() {
    clearTimeout(toastTimer)
    toastTimer = null
  }

  return {
    toastMessage,
    toastType,
    toastOpen,
    showToast,
    clearToastTimer
  }
}

