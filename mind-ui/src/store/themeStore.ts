import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ThemeState {
  darkMode: boolean
  toggleDarkMode: () => void
  setDarkMode: (dark: boolean) => void
}

function applyDataTheme(dark: boolean) {
  const root = document.documentElement
  root.setAttribute('data-theme', dark ? 'dark' : 'light')
  root.style.colorScheme = dark ? 'dark' : 'light'
  document.body.style.background = dark ? '#0f1115' : '#f5f5f5'
  document.body.style.color = dark ? '#e6e6e6' : 'inherit'
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      darkMode: false,
      toggleDarkMode: () =>
        set((state) => {
          const next = !state.darkMode
          applyDataTheme(next)
          return { darkMode: next }
        }),
      setDarkMode: (dark) => {
        applyDataTheme(dark)
        set({ darkMode: dark })
      },
    }),
    {
      name: 'mind-theme',
      onRehydrateStorage: () => (state) => {
        if (state) applyDataTheme(state.darkMode)
      },
    }
  )
)
