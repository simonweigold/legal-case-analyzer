// hooks/useTheme.ts
import { useState, useEffect } from 'react';

export function useTheme() {
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem("darkMode");
      if (saved) {
        return JSON.parse(saved);
      }
      // Check system preference
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem("darkMode", JSON.stringify(darkMode));
      const root = document.documentElement;
      if (darkMode) {
        root.classList.add("dark");
      } else {
        root.classList.remove("dark");
      }
    }
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode((prev: boolean) => !prev);
  };

  return {
    darkMode,
    toggleDarkMode
  };
} 
        default: background,
        paper: card
      },
      text: {
        primary: foreground,
        secondary: mutedForeground
      },
      divider: border,
    },
    shape: { borderRadius: 10 }, // Using number for MUI, CSS var applied in component overrides
    components: {
      MuiPaper: {
        styleOverrides: { 
          root: { 
            borderRadius: "var(--radius)",
            border: "1px solid var(--border)",
            backgroundColor: "var(--card)",
            color: "var(--card-foreground)"
          } 
        },
      },
      MuiButton: {
        defaultProps: { variant: "contained" },
        styleOverrides: {
          root: {
            borderRadius: "var(--radius)",
          }
        }
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              backgroundColor: "var(--input)",
              borderRadius: "var(--radius)",
              '& fieldset': {
                borderColor: "var(--border)",
              },
              '&:hover fieldset': {
                borderColor: "var(--ring)",
              },
              '&.Mui-focused fieldset': {
                borderColor: "var(--ring)",
              },
            },
          },
        },
      },
    },
  });
  }, [darkMode]); // Recreate theme when darkMode changes

  const toggleDarkMode = () => setDarkMode((prev: boolean) => !prev);

  return {
    theme,
    darkMode,
    toggleDarkMode
  };
}
