/** 登录/登出时统一清理各 Store 缓存，避免切换账号后仍显示旧状态 */
export async function refreshSessionAfterLogin() {
  const { useMembershipStore } = await import('../stores/membership')
  const membershipStore = useMembershipStore()
  membershipStore.error = ''
  await membershipStore.fetchMembershipStatus()

  const { useDownloadStore } = await import('../stores/download')
  const downloadStore = useDownloadStore()
  downloadStore.reconnect()
}

export async function clearSessionOnLogout() {
  const { useMembershipStore } = await import('../stores/membership')
  const membershipStore = useMembershipStore()
  membershipStore.error = ''

  const { useDownloadStore } = await import('../stores/download')
  const downloadStore = useDownloadStore()
  downloadStore.resetSession()
}
